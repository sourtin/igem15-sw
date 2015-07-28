#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod
from vector import Vector
import threading

class HardwareException(Exception):
    pass

class Status(object):
    def __init__(self, ready, idle, calibrated, position, **kwargs):
        kwargs.ready = ready
        kwargs.idle = idle
        kwargs.calibrated = calibrated
        kwargs.position = position
        self.__dict__ = kwargs


class Head:
    __metaclass__ = ABCMeta

    @abstractmethod
    def calibrate(self):
        pass

    @abstractmethod
    def status(self):
        """return information on:
         * calibration
         * idle?
         * position
         * attached
        """
        return Status(ready=False, idle=False, calibrated=False, position=Vector(0,0), attached=False)

    @abstractmethod
    def config(self, **kwargs):
        # update any specified parameters
        # return current self._config
        pass

    @abstractmethod
    def act(self, cb, coords, **kwargs):
        # perform action and call cb
        pass


class Camera(Head):
    @abstractmethod
    def livefeed(self):
        return []

    @abstractmethod
    def orientation(self):
        """return angular orientation of images returned wrt bench coordinates"""
        return 0

    @abstractmethod
    def resolution(self):
        return 0, 0

    @abstractmethod
    def precision(self):
        return float('inf')


class Stage:
    __metaclass__ = ABCMeta

    def __init__(self, *args, **kwargs):
        self._garcon = threading.Event()
        self._initialise(*arg, **kwargs)

    @abstractmethod
    def _initialise(self, *args, **kwargs):
        self._garcon.set()

    @abstractmethod
    def calibrate(self):
        pass

    @abstractmethod
    def status(self):
        """return information on:
         * ready?
         * calibration
         * idle?
         * position
         * what head is attached
        """
        return Status(ready=False, idle=False, calibrated=False, position=Vector(0,0), attachment=None)

    def wait(self):
        self._garcon.wait()

    @abstractmethod
    def register(self, head, **kwargs):
        """register a head instance; use kwargs to specify how to switch to the head?"""
        pass

    @abstractmethod
    def list(self):
        """return a list of registered heads"""
        return []

    @abstractmethod
    def bounds(self):
        """return bounding polygon, ideally a rectangle"""
        return Rectangle(Vector(0,0), Vector(1,0), 1, 1)

    def select(self, head):
        """select a head, make sure not to reselect an already selected head"""
        pass

    def move(self, coord):
        """move head to coord"""
        pass


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
        return Rectangle(origin, self.angle + angle, self.width, self.height)

    def rectangle(self):
        return self.rotate(0)

    def centroid(self):
        return self.polygon().centroid()



