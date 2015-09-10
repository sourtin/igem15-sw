#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from lib import hw
from lib.vector import Vector

from math import ceil, pi
from time import time
from threading import Thread, Event, Lock
import subprocess

import cv2
import numpy as np
import PIL.Image

class Image(object):
    """Image wrapper with helper functions for conversion between cv/numpy and PIL formats;
       keeps a record of the timestamp to allow image expiry and also includes helper
       functions to convert between image coordinates and device coordinates"""

    def cv2pil(im):
        """static Image.cv2pil -- convert cv/numpy to pil"""
        return PIL.Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB))

    def pil2cv(im):
        """static Image.pil2cv -- convert pil to cv/numpy"""
        return np.array(im.convert("RGB"))[:,:,::-1]

    def __init__(self, rectangle, data, stamp=None):
        """initialise an image with a Rectangle specifying the device coordinates it
           corresponds to, the image data (in cv/numpy BGR format), and an optional
           timestamp (otherwise is calculated automatically)"""

        if stamp is None:
            stamp = time()
        self.rectangle = rectangle
        self.data = data
        self.stamp = stamp

    def resolution(self):
        """determine the device width/height of an individual pixel, assuming square pixels"""
        dim_meter = max(self.rectangle.width, self.rectangle.height)
        dim_pixel = max(self.data.cols,       self.data.rows)
        return dim_meter / dim_pixel

    def from_bench(self, point):
        """convert device coordinates to pixels"""
        x, y = self.rectangle.from_bench(point)
        return Vector(
                int(x * self.data.cols / self.rectangle.width),
                int(y * self.data.rows / self.rectangle.height))

    def to_bench(self, coord):
        """convert pixels to device coordinates"""
        x, y = coord
        return self.rectangle.to_bench(Vector(
            x * self.rectangle.width / self.data.cols,
            y * self.rectangle.height / self.data.rows))

    def cv(self):
        """return a cv/numpy representation of the image"""
        return self.data.copy()

    def pil(self):
        """return a pil representation of the image"""
        return Image.cv2pil(self.data)

    def show(self, viewer='feh'):
        """display the image using an external program;
              viewer -- external program to use, defaults to feh,
                        should support reading a png from stdin
                        when given '-' as a cli option"""

        im = self.pil()
        p = subprocess.Popen([viewer, '-'], stdin=subprocess.PIPE)
        im.save(p.stdin, "png")
        p.stdin.close()
        p.wait()



class Canvas(object):
    """Canvas objects can be used to automatically assemble an image covering
       a supplied polygon.

       Determining rectangles to cover a given polygon is NP-hard so instead
       we just cover the bounding rectangle, taking into account if the camera
       happens to be rotated wrt the xy stage.

       After determining the appropriate rectangular areas to image, the class
       will automatically manage the process of selecting an appropriate camera
       satisfying the specified precision, imaging these areas, replacing the
       images when they expire, and stitching them into a single image (masking
       the regions outside of the polygon)."""

    def __init__(self, workspace, config, polygon, min_precision, max_age, min_stitch, timeout=None, camera=None):
        """initialise a canvas object
              workspace - the parent workspace object
              config - the configuration options to pass to the camera
              polygon - the region to cover (will image the region's bounding rectangle,
                        so complicated shapes may be imaged fairly inefficiently)
              min_precision - the minimum precision of the camera (in m px^-1) to select
              max_age - the time after which an image should expire
                        (in s, though can have up to 6dp)
              min_stitch - the minimum stitching region to include -- the rectangles will
                           intersect by this amount
              timeout - optional; after how long should an image request timeout if it
                        appears to be taking too long, defaults to max_age
                        (in s, though can have up to 6dp)
              camera - optional; supply a camera instead of having it automatically chosen"""

        if camera is None:
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
        self.config = config
        self.timeout = timeout if timeout is not None else max_age

        # qstamps remember enqueuement of image updates
        # so that if an update takes too long (e.g. failure)
        # it can be requeued after self.timeout
        self.qstamps = {}
        self.images = self.generate_rects()

        self.flags = {}
        self.flags['invalidate'] = Event()
        self.flags['image'] = Event()
        self.lock = Lock()
        self.thread = Thread(target=self.worker)
        self.thread.daemon = True
        self.thread.start()

    def status(self):
        """returns a tuplei, (i, ii), indicating the image status:
              i. whether the first round of image retrieval is complete
                 (i.e. if canvas.get() is ready to return an image)
              ii. whether the image is complete has not expired"""
        expiry = self.max_age
        return (all(image is not None for _,_,image in self.images),
                all(image is not None and time() - image.stamp < expiry for _,_,image in self.images))

    def invalidate(self, i, j):
        """manually invalidate/expire an individual tile of the image"""

        expiry = self.max_age
        def replace(el):
            (a, b), r, im = el
            if (a, b) == (i, j):
                im.stamp = time() - 2*expiry
                return (i, j), r, im
            else:
                return el

        with self.lock:
            try:
                del self.qstamps[i,j]
            except KeyError:
                pass

            self.images = [replace(el) for el in self.images]
            self.flags['invalidate'].set()

    def get(self):
        """return the assembled image, blocking if
           necessary until retrieval is complete"""
        raise NotImplementedError
        self.wait(False)
        # should probably cache the image

    def wait(self, alive=True):
        """block until all images have been retrieved
              alive - whether to also block until all
                      expired images have been replaced"""

        while not all(im is not None for _,_,im in self.images):
            self.flags['image'].wait(1)
            self.flags['image'].clear()

        if alive:
            while any(expired(*x) for x,_,_ in self.images):
                self.flags['image'].wait(1)
                self.flags['image'].clear()

    def generate_rects(self):
        """generate a list of rectangles of the cameras size covering
           the given polygon; the rectangles will intersect by the
           specified stitching amount

           TODO: eliminate any rectangles which are not in the given
                 polygon"""

        _, camera = self.backend
        prec = camera.precision()
        stitch = self.min_stitch * prec

        width, height = camera.resolution()
        width *= prec
        height *= prec
        wid = width - 2*stitch
        hei = height - 2*stitch

        bounding = self.polygon.rectangle(camera.orientation())
        o = bounding.origin
        cols = int(ceil(bounding.width / wid))
        rows = int(ceil(bounding.height / hei))

        return [i for s in [[((i,j), Rectangle(o + Vector(j*wid-stitch, i*hei-stitch), 0, width, height), None)
            for j in (reversed(range(cols)) if i%2 else range(cols))] for i in range(rows)] for i in s]

    def worker(self):
        """main loop -- continually enqueue expired images and
                        handle request timeouts"""

        while True:
            self.flags['invalidate'].clear()
            expiry = self.max_age
            workspace, camera = self.backend
            timeout = self.timeout

            with self.lock:
                for (i, j), rect, image in self.images:
                    try:
                        assert time() - self.qstamps[i,j] < timeout
                    except (KeyError, AssertionError):
                        if image is None or time() - image.stamp >= expiry:
                            self.enqueue(i, j, rect)
                            self.qstamps[i,j] = time()

            next = min(time() + timeout, *(self.expiry_time(x,im) for x,_,im in self.images))
            if next > time():
                self.flags['invalidate'].wait(next - time())
                self.flags['invalidate'].clear()
            else:
                print('Warning: Canvas.worker is possibly looping too quickly, if\n' +
                      '         you get this message a lot it may indicate a bug')

    def expired(self, i, j):
        """returns whether the specified image has expired or not"""
        for x, _, im in self.images:
            if x == (i, j) and im is not None:
                if time() - im.stamp < self.max_age:
                    return False
        return True

    def expiry_time(self, x, im):
        """helper function to return the expiry time of
           the specified image
              x=(i,j) -- the tile coordinates
              im -- the (possibly None) image"""

        try:
            return self.qstamps[x] + self.timeout
        except:
            if im is not None:
                return im.stamp + self.max_age
            else:
                return time() + self.timeout

    def update(self, i, j, image):
        """update the tile at (i,j) with the specified image"""

        def replace(el):
            """closure to selectively replace images in
               a functional way"""
            (a, b), rect, _ = el
            return ((i,j), rect, image) if (a,b)==(i,j) else el

        with self.lock:
            self.images = [replace(el) for el in self.images]
            del self.qstamps[i,j] # reset timeout
            self.flags['image'].set()

    def enqueue(self, i, j, rect):
        """enqueue the replacement of the specified image"""
        cb = lambda image: self.update(i, j, image)
        cond = lambda: self.expired(i, j)
        ws, cam = self.backend
        ws.enqueue(cam, [rect.centroid()], cb, self.config, {}, cond)


class Polygon(object):
    """represents the bounding polygon of a region via
       a list of Vector coordinates (in metres) and some
       helper functions"""
    
    def __init__(self, *points):
        """initialise the polygon with a set
           of points (in device coordinates)"""
        self.points = points

    def polygon(self):
        """return a polygon representation
           (essentially just copy)"""
        return Polygon(*self.points)

    def to_bench(self, point):
        """convert a point in the polygon to device coordinates"""
        return point

    def from_bench(self, point):
        """convert device coordinates to a point in the polygon"""
        return point

    def subdivide(self, *points):
        """create a new polygon from a set of points defined in
           the current polygon's reference frame"""
        return Polygon(*points)

    def rectangle(self, angle=0):
        """return the smallest bounding rectangle
              angle - the orientation of the rectangle,
                      given in anticlockwise radians"""

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
        """return the centroid in polygon coordinates"""
        origin = Vector(0,0)
        return sum(self.points, origin) / len(self.points)

    def __repr__(self):
        return "Polygon(%r)" % self.points


class Rectangle(Polygon):
    """represents a polygon bounding a certain region as a list
       of Vector coordinates in metres with some helper functions;
       this subclass s guaranteed rectangular, and supports
       rectangles rotated wrt the stage coordinate system"""

    def __init__(self, origin, dirnAB, lenAB, lenAD):
        """create a rectangle ABCD from origin (A) with width
           lenAB in the dirnAB direction and height lenAD;
              origin - the origin of the rectangle in device coordinates
              dirnAB - an angle in radians or a direction Vector
              lenAB - the width (parallel to dirnAB) in metres
              lenAD - the height (perpendicular to dirnAB) in metres"""

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
        b = a + Vector.from_polar(self.width, self.angle)
        c = b + Vector.from_polar(self.height, self.angle + 0.5*pi)
        d = a + Vector.from_polar(self.height, self.angle + 0.5*pi)

        return Polygon(a, b, c, d)

    def to_bench(self, point):
        """convert rectangle coordinates to device coordinates"""
        return origin + point.rotate(self.angle)

    def from_bench(self, point):
        """convert device coordinates to rectangle coordinates"""
        return (point - origin).rotate(-self.angle)

    def subdivide(self, origin, dirnAB, lenAB, lenAD):
        """return a new rectangle given a description in terms
           of the current rectangles coordinate system
              origin - the origin of the new rectangle relative to the current
              dirnAB - an angle in radians or a direction Vector
              lenAB - the width (parallel to dirnAB) in metres
              lenAD - the height (perpendicular to dirnAB) in metres"""

        origin += self.origin
        try:
            angle = self.angle + dirnAB.θ()
        except AttributeError:
            angle = self.angle + dirnAB
        return Rectangle(origin + self.origin, self.angle + dirnAB.θ(), lenAB, lenAD)

    def rotate(self, angle):
        """rotate the rectangle"""
        return Rectangle(self.origin, self.angle + angle, self.width, self.height)

    def rectangle(self, angle=0):
        """return the bounding rectangle at the given angle"""
        return self.rotate(0) if angle == 0 else self.polygon().rectangle(angle)

    def centroid(self):
        """determine the centre of the rectangle"""
        return self.polygon().centroid()

    def __repr__(self):
        return "Rectangle(%r, %r, %r, %r)" % (self.origin, self.angle, self.width, self.height)



