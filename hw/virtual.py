#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Simulate an XY stage and other associated hardware
   for testing in the context of the rest of the library.
   
   Use the var.tests.virtual test to setup an XY stage
   with a view of the Andromeda galaxy; This can be used
   to take overview pictures as well as microscopy images,
   and to fake mark the canvas.
   
   XY -- xy stage
   Σ -- overhead camera
   Μ -- microscope (note this is capital μ!!)
   Pen -- annotater (supposedly marks the canvas with a pen) """


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

        # we are in our own thread, so we need to indicate
        # to the garçon ('waiter') that we are done
        self._garçon.set()

    def calibrate(self):
        print("Calibrating the virtual stage...")
        print("Bounds: %.2em x %.2em" % self.dims)
        print("Position: (%.2em, %.2em)" % self.pos)
        print()
        self.stati['calibrated'] = True

    def status(self):
        self.wait() # initialisation is in a separate thread, so wait
                    # for it to complete (self._garçon -- the 'waiter')
        return Status(position=self.pos, attachment=self.head, **self.stati)

    def register(self, head):
        self.heads.add(head)
        head.imprint(self)
        return head

    def list(self):
        return list(self.heads)

    def bounds(self):
        # origin, x-axis unit vector, width, height
        return Rectangle(Vector(0, 0), Vector(1, 0), *self.dims)

    def select(self, head):
        assert head in self.heads
        self.head = head

    def move(self, coord):
        δ = coord - self.pos
        print("Actuating servos... translating by Δx=%.2em, Δy=%.2em" % δ)
        self.pos += δ

        # impose a quantisation error of 1mm :P
        self.pos = round(self.pos, 3)
        print("\t%r, %r" % (coord, self.pos))

    def position(self):
        return self.pos

class Σ(Camera):
    """The overhead camera"""

    def __init__(self, layer):
        self.backend = layer # see the layer class later on
        self.stati = {'ready': False, 'idle': False, 'calibrated': False, 'attached': True}
        self.parent = None
        self.calibration = None
        self._config = {}

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
        self._config.update(config)
        return self._config

    def act(self, callback, coords, **kwargs):
        callback(self.capture())

    def capture(self):
        im = self.backend.get(0, 0, *self.backend.shape)
        return Image(self.calibration, im)
        # Image is defined under lib.canvas and is a
        # wrapper over an opencv/numpy image

    def livefeed(self):
        return self.capture()

    def orientation(self):
        # the camera is not rotated wrt the xy axes
        return 0

    def resolution(self):
        return self.backend.shape

    def precision(self):
        return 1 / self.backend.factorz

class Μ(Camera):
    """The microscope class, note that this is capital μ!"""

    def __init__(self, layer, shape):
        self.backend = layer # see the layer class later on
        self.shape = shape
        self.stati = {'ready': False, 'idle': False, 'calibrated': False}
        self.parent = None
        self.calibration = None
        self.μpos = Vector(0, 0)
        self._config = {}

    def imprint(self, parent):
        self.parent = parent
        pstat = parent.status()
        if pstat.ready and pstat.calibrated and self.backend.im:
            self.stati['ready'] = True
            self.stati['idle'] = True
        self.calibrate()

    def uncalibrate(self):
        """generate some fake lens distortion to simulate an uncalibrated camera"""

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
        self._config.update(config)
        return self._config

    def act(self, cb, coords, **kwargs):
        # the xy stage has 1mm precision, we then actuate our own
        # finer precision servos to account for this
        coord = coords[0]
        self.parent.select(self)
        self.parent.move(coord)
        δ = coord - self.parent.position() - self.μpos
        print("μ: Actuating servos... translating by Δx=%.2em, Δy=%.2em" % δ)
        self.μpos += δ
        cb(self.capture(*coord))

    def capture(self, x, y):
        """capture an image and apply our calibration parameters to (un)distort it"""

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
    """A marker head"""

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

    def config(self, colour=None):
        """configure the marker colour"""
        if colour is not None:
            self.colour = colour
        return {'colour': self.colour}

    def act(self, cb, coords, **kwargs):
        """draw a line defined by the specified coords"""

        coords = [x + self.calibration for x in coords]
        self.parent.select(self)
        self.parent.move(coords.pop(0))

        print("Pen down (%s)" % self.colour)
        for x in coords:
            self.parent.move(x)
        print("Pen up")

        cb(True)

class Layer(object):
    """Layer object; wraps an openslide image and
       provides a view into one of the openslide layers
       and translates between 'real-world' coordinates
       and the images internal coordinates"""

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
        """Return a section of the layer;
              xy are real-world coordinates
              wh are in pixels and correspond to the 'camera' resolution"""
        x, y = map(lambda v: int(v*self.factor0), (x, y))
        return Image.pil2cv(self.im.read_region((x, y), self.z, (w, h)))

