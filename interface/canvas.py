#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from . import hw
from .vector import Vector

from math import ceil
from time import time
from threading import Thread, Event, Lock
import subprocess

import cv2
import numpy as np
import PIL

class Image(object):
    def cv2pil(im):
        return PIL.Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB))
    def pil2cv(im):
        return np.array(im.convert("RGB"))[:,:,::-1]

    def __init__(self, rectangle, data, stamp=None):
        if stamp is None:
            stamp = time()
        self.rectangle = rectangle
        self.data = data
        self.stamp = stamp

    def resolution(self):
        dim_meter = max(self.rectangle.width, self.rectangle.height)
        dim_pixel = max(self.data.cols,       self.data.rows)
        return dim_meter / dim_pixel

    def from_bench(self, point):
        x, y = self.rectangle.from_bench(point)
        return Vector(
                int(x * self.data.cols / self.rectangle.width),
                int(y * self.data.rows / self.rectangle.height))

    def to_bench(self, coord):
        x, y = coord
        return self.rectangle.to_bench(Vector(
            x * self.rectangle.width / self.data.cols,
            y * self.rectangle.height / self.data.rows))

    def cv(self):
        return self.data

    def pil(self):
        return Image.cv2pil(self.data)

    def show(self):
        im = self.pil()
        p = subprocess.Popen(['feh', '-'], stdin=subprocess.PIPE)
        im.save(p.stdin, "png")
        p.stdin.close()
        p.wait()



class Canvas(object):
    def __init__(self, workspace, config, polygon, min_precision, max_age, min_stitch):
        """max_age in seconds, but up to microsec resolution"""

        candidates = sorted(h for h in map(
            lambda head: (head.precision(), head) if isinstance(head, hw.Camera) else None,
            workspace.apparati()) if h is not None)

        try:
            precision, camera = candidates[0]
            for cp, cc in candidates:
                if cp <= min_precision:
                    precision, camera = cp, cc
        except IndexError:
            raise hw.HardwareException("No cameras installed!!!!!!")

        if precision > min_precision:
            print("Warning, camera used for canvas of insufficient resolution -- camera has" +
                    "resolution %.2em but a resolution of %.2em was requested" % (precision, min_precision))

        self.backend = workspace, camera
        self.max_age = max_age
        self.min_stitch = min_stitch
        self.polygon = polygon
        self.images = self.generate_rects()
        self.config = config

        return

        self.flags = {}
        self.flags.invalidate = Event()
        self.flags.image = Event()
        self.lock = Lock()
        self.thread = Thread(target=self.worker)
        self.thread.daemon = True
        self.thread.start()

    def generate_rects(self):
        _, camera = self.backend
        stitch = self.min_stitch
        prec = camera.precision()
        width, height = camera.resolution()
        wid = width - 2*stitch
        hei = height - 2*stitch

        bounding = self.polygon.rectangle(camera.orientation())
        cols = int(ceil(bounding.width / (wid * prec)))
        rows = int(ceil(bounding.height / (hei * prec)))

        return [i for s in [[((i,j), Rectangle(Vector(j*wid-stitch, i*hei-stitch), 0, width, height), None)
            for j in (reversed(range(cols)) if i%2 else range(cols))] for i in range(rows)] for i in s]

    def worker(self):
        while True:
            self.flags.invalidate.clear()
            next = time()
            expiry = self.max_age
            workspace, camera = self.backend
            with self.lock:
                for (i, j), rect, image in self.images:
                    if image is None or time() - image.stamp >= expiry:
                        cb = lambda image: self.update(i, j, image)
                        workspace.enqueue(camera, rect.centroid(), cb, self.config, {})
                    elif image is not None:
                        next = min(next, image.stamp + expiry)
            if next > time():
                self.flags.invalidate.wait(next - time())

    def update(self, i, j, image):
        def replace(el):
            (a, b), rect, _ = el
            return ((i,j), rect, image) if (a,b)==(i,j) else el
        with self.lock:
            self.images = [replace(el) for el in self.images]
            self.flags.image.set()

    def status(self):
        expiry = self.max_age
        return all(image is not None and time() - image.stamp < expiry for _,_,image in self.images)

    def invalidate(self, i, j):
        expiry = self.max_age
        def replace(el):
            (a, b), r, im = el
            if (a, b) == (i, j):
                im.stamp = time() - 2*expiry
                return (i, j), r, im
            else:
                return el

        with self.lock:
            self.images = [replace(el) for el in self.images]
            self.flags.invalidate.set()

    def get(self):
        image = None
        while not all(im is not None for _,_,im in self.images):
            self.flags.image.wait()
        # construct image
        return image


class Polygon(object):
    """a bounding pointinate polygon specified in metres"""
    def __init__(self, *points):
        self.points = points

    def polygon(self):
        return Polygon(*self.points)

    def to_bench(self, point):
        return point

    def from_bench(self, point):
        return point

    def subdivide(self, *points):
        return Polygon(*points)

    def rectangle(self, angle):
        """return bounding rectangle with specified angle"""
        points = [point.rotate(angle) for point in self.points]
        x_max = max(x for x,_ in points)
        x_min = min(x for x,_ in points)
        y_max = max(y for _,y in points)
        y_min = min(y for _,y in points)

        origin = Vector(x_min, y_min).rotate(-angle)
        width = x_max - x_min
        height = y_max - y_min
        return Rectangle(origin, -angle, width, height)

    def centroid(self):
        origin = Vector(0,0)
        return sum(self.points, origin) / len(self.points)

    def __repr__(self):
        return "Polygon(%r)" % self.points


class Rectangle(Polygon):
    """bounding polygon, guaranteed rectangular, metres; supports rotation"""

    def __init__(self, origin, dirnAB, lenAB, lenAD):
        """create a rectangle from origin with width lenAB in the dirnAB direction and height lenAD"""
        self.origin = origin
        try:
            self.angle = dirnAB.θ()
        except AttributeError:
            self.angle = dirnAB
        self.width = lenAB
        self.height = lenAD

    def polygon(self):
        """return a polygon object"""
        a = self.origin
        b = a + Vector.from_polar(lenAB, self.angle)
        c = b + Vector.from_polar(lenAD, self.angle + 0.5*math.pi)
        d = a + Vector.from_polar(lenAD, self.angle + 0.5*math.pi)

        return Polygon(a, b, c, d)

    def to_bench(self, point):
        return origin + point.rotate(self.angle)

    def from_bench(self, point):
        return (point - origin).rotate(-self.angle)

    def subdivide(self, origin, dirnAB, lenAB, lenAD):
        origin += self.origin
        angle = self.angle + dirnAB.θ()
        return Rectangle(origin + self.origin, self.angle + dirnAB.θ(), lenAB, lenAD)

    def rotate(self, angle):
        return Rectangle(self.origin, self.angle + angle, self.width, self.height)

    def rectangle(self, angle=0):
        return self.rotate(0) if angle == 0 else self.polygon().rectangle(angle)

    def centroid(self):
        return self.polygon().centroid()

    def __repr__(self):
        return "Rectangle(%r, %r, %r, %r)" % (self.origin, self.angle, self.width, self.height)



