#!/usr/bin/env python2
import abc
import threading
import vector

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
    """a bounding coordinate polygon specified in millimetres"""
    def __init__(self, *coords):
        self.coords = coords

    def subdivide(self):
        pass

class Rectangle(Polygon):
    """bounding polygon, guaranteed rectangular; support rotation?"""

    def __init__(self, origin, dirnAB, lenAB, lenAC):
        """create a rectangle from origin with width lenAB in the dirnAB direction and height lenAC"""
        self.origin = origin
        self.angle = dirnAN.θ()
        self.width = lenAB
        self.height = lenAC

    def polygon(self):
        """return a polygon object"""
        pass


