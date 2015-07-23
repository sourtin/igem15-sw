#!/usr/bin/env python2
import abc
import threading
from vector import Vector

class Head:
    __metaclass__ = abc.ABCMeta

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
        pass

    def config(self, **kwargs):
        # update any specified parameters
        # return current self._config
        pass

    def act(self, cb, **kwargs):
        # perform action and call cb
        pass


class Camera(Head):
    @abstractmethod
    def livefeed(self):
        pass


class Stage:
    __metaclass__ = abc.ABCMeta

    def __init__(self, *args, **kwargs):
        self._garcon = threading.Event()
        self._initialise(*arg, **kwargs)

    @abstractmethod
    def _initialise(self, *args, **kwargs):
        self._garcon.set()

    @abstractmethod
    def calibrate(self):
        pass

    @abstactmethod
    def status(self):
        """return information on:
         * ready?
         * calibration
         * idle?
         * position
         * what head is attached
        """
        pass

    def wait(self):
        self._garcon.wait()

    @abstractmethod
    def register(self, head, **kwargs):
        """register a head instance; use kwargs to specify how to switch to the head?"""
        pass

    @abstractmethod
    def query(self):
        """return a list of registered heads"""
        pass

    @abstractmethod
    def bounds(self):
        """return bounding polygon"""
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

class Rectangle(Polygon):
    """bounding polygon, guaranteed rectangular, metres; supports rotation"""

    def __init__(self, origin, dirnAB, lenAB, lenAD):
        """create a rectangle from origin with width lenAB in the dirnAB direction and height lenAD"""
        self.origin = origin
        self.angle = dirnAB.θ()
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
        r, θ = point.polar()
        return origin + Vector.from_polar(r, θ + self.angle)

    def from_bench(self, point):
        r, θ = (point - origin).polar()
        return Vector.from_polar(r, θ - self.angle)

    def subdivide(self, origin, dirnAB, lenAB, lenAD):
        origin += self.origin
        angle = self.angle + dirnAB.θ()
        return Rectangle(origin + self.origin, Vector.from_polar(lenAB, angle), lenAD)



