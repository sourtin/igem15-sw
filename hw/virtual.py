#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from lib.canvas import Image, Rectangle
from lib.hw import Stage, Head, Camera, Status, Vector
import cv2
import numpy as np

class XY(Stage):
    def _initialise(self, w, h):
        self.stati = {'ready': False, 'idle': False, 'calibrated': False}
        self.pos = Vector(0,0)
        self.dims = w, h
        self.heads = set()
        self.head = None

        self.calibrate()
        self.stati['ready'] = True
        self.stati['idle'] = True
        self._garcon.set()

    def calibrate(self):
        print("Calibrating the virtual stage...")
        print("Bounds: %.2em x %.2em" % self.dims)
        print("Position: (%.2em, %.2em)" % self.pos)
        print()
        self.stati['calibrated'] = True

    def status(self):
        self.wait()
        return Status(position=self.pos, attachment=self.head, **self.stati)

    def register(self, head):
        self.heads.add(head)
        head.imprint(self)
        return head

    def list(self):
        return self.heads

    def bounds(self):
        return Rectangle(Vector(0, 0), Vector(1, 0), *self.dims)

    def select(self, head):
        assert head in self.heads
        self.head = head

    def move(self, coord):
        δ = coord - self.pos
        print("Actuating servos... translating by Δx=%.2em, Δy=%.2em" % δ)
        self.pos += δ
        self.pos = round(self.pos, 3)
        print("\t%r, %r" % (coord, self.pos))

    def position(self):
        return self.pos

class Σ(Camera):
    def __init__(self, layer):
        self.backend = layer
        self.stati = {'ready': False, 'idle': False, 'calibrated': False, 'attached': True}
        self.parent = None
        self.calibration = None

    def imprint(self, parent):
        self.parent = parent
        pstat = parent.status()
        if pstat.ready and pstat.calibrated and self.backend.im:
            self.stati['ready'] = True
            self.stati['idle'] = True
        self.calibrate()

    def calibrate(self):
        self.calibration = self.parent.bounds()
        self.stati['calibrated'] = True

    def status(self):
        w, h = self.parent.dims
        return Status(position=(w/2, h/2), **self.stati)

    def config(self, **config):
        print("Configuring", self, ":", config)

    def act(self, cb, coords, **kwargs):
        cb(self.capture())

    def capture(self):
        im = self.backend.get(0, 0, *self.backend.shape)
        return Image(self.calibration, im)

    def livefeed(self):
        return self.capture()

    def orientation(self):
        return 0

    def resolution(self):
        return self.backend.shape

    def precision(self):
        return 1 / self.backend.factorz

class Μ(Camera):
    def __init__(self, layer, shape):
        self.backend = layer
        self.shape = shape
        self.stati = {'ready': False, 'idle': False, 'calibrated': False}
        self.parent = None
        self.calibration = None
        self.μpos = Vector(0, 0)

    def imprint(self, parent):
        self.parent = parent
        pstat = parent.status()
        if pstat.ready and pstat.calibrated and self.backend.im:
            self.stati['ready'] = True
            self.stati['idle'] = True
        self.calibrate()

    def uncalibrate(self):
        w, h = self.shape
        x = w//8
        y = h//8

        # apply a slight radial transform to get a distorted fish eye view
        points_ob = [[2*x, 2*y, 0], [4*x, 2*y, 0], [6*x, 2*y, 0],
                     [2*x, 4*y, 0],                [6*x, 4*y, 0],
                     [2*x, 6*y, 0], [4*x, 6*y, 0], [6*x, 6*y, 0]]
        points_im = [[2*x, 2*y], [4*x, 1*y], [6*x, 2*y],
                     [1*x, 4*y],             [7*x, 4*y],
                     [2*x, 6*y], [4*x, 7*y], [6*x, 6*y]]

        points_ob = [np.array(points_ob, dtype=np.float32)]
        points_im = [np.array(points_im, dtype=np.float32)]
        mat = np.identity(3)

        self.calibration = cv2.calibrateCamera(points_ob, points_im, self.shape, mat, 0, flags=0)
        self.stati['calibrated'] = False

    def calibrate(self):
        if self.calibration is None:
            # randomly fail
            self.uncalibrate()
            return

        self.calibration = None
        self.stati['calibrated'] = True

    def status(self):
        pos = self.parent.position() if self.parent is not None else None
        attached = (self == self.parent.head) if self.parent is not None else None
        return Status(position=pos, attached=attached, **self.stati)

    def config(self, **config):
        print("Configuring", self, ":", config)

    def act(self, cb, coords, **kwargs):
        coord = coords[0]
        self.parent.select(self)
        self.parent.move(coord)
        δ = coord - self.parent.position() - self.μpos
        print("μ: Actuating servos... translating by Δx=%.2em, Δy=%.2em" % δ)
        self.μpos += δ
        cb(self.capture(*coord))

    def capture(self, x, y):
        im = self.backend.get(x, y, *self.shape)
        if self.calibration is not None:
            _, mat, coe, *_ = self.calibration
            im = cv2.undistort(im, mat, coe)
        return Image(Rectangle(Vector(0,0), Vector(1,0).rotate(self.orientation()), *self.shape), im)

    def livefeed(self):
        if self.parent is None or not self.status().attached:
            return []
        return self.capture(self.parent.position())

    def orientation(self):
        return 0

    def resolution(self):
        return self.shape

    def precision(self):
        return 1 / self.backend.factorz

class Pen(Head):
    def __init__(self):
        self.stati = {'ready': False, 'idle': False, 'calibrated': False}
        self.parent = None
        self.calibration = Vector(0, 0)
        self.colour = "red"

    def imprint(self, parent):
        self.parent = parent
        pstat = parent.status()
        if pstat.ready and pstat.calibrated:
            self.stati['ready'] = True
            self.stati['idle'] = True
        self.calibrate()

    def calibrate(self):
        self.calibration = (0.005, 0.003)
        self.stati['calibrated'] = True

    def status(self):
        pos = self.parent.position() if self.parent is not None else None
        attached = (self == self.parent.head) if self.parent is not None else None
        return Status(position=pos, attached=attached, **self.stati)

    def config(self, colour):
        self.colour = colour

    def act(self, cb, coords, **kwargs):
        coords = [x + self.calibration for x in coords]
        self.parent.select(self)
        self.parent.move(coords.pop(0))

        print("Pen down (%s)" % self.colour)
        for x in coords:
            self.parent.move(x)
        print("Pen up")

        cb(True)

class Layer(object):
    def __init__(self, im, z, side):
        iw, ih = im.dimensions
        lw, lh = im.level_dimensions[z]
        self.factor0 = max(iw, ih) / side
        self.factorz = max(lw, lh) / side

        self.im = im
        self.z = z
        self.side = side
        self.shape_im = iw, ih
        self.shape = lw, lh

    def get(self, x, y, w, h):
        x, y = map(lambda v: int(v*self.factor0), (x, y))
        return Image.pil2cv(self.im.read_region((x, y), self.z, (w, h)))

