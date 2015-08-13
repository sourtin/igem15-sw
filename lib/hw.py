#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod
from lib.vector import Vector
import threading

class HardwareException(Exception):
    """Hardware-related exception"""

class Status(object):
    """Status object; essentially a wrapper around a dict"""

    def __init__(self, ready, idle, calibrated, position, **kwargs):
        """Create a status object
              ready - is the hardware setup and ready to use?
              idle - is the hardware idle with an empty action queue?
              calibrated - is the hardware properly calibrated?
              position - a Vector representing the current position
                         in some obvious coordinate system
              **kwargs - additional optional stati"""

        kwargs['ready'] = ready
        kwargs['idle'] = idle
        kwargs['calibrated'] = calibrated
        kwargs['position'] = position
        self.__dict__ = kwargs


class Head:
    """An abstract class representing an XY stage head"""
    __metaclass__ = ABCMeta

    @abstractmethod
    def imprint(self, parent):
        """used by an xy stage to adopt a head"""

    @abstractmethod
    def calibrate(self):
        """calibrate the head"""

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
        """update hardware parameters, e.g. changing microscope objective,
           return the current config"""
        return {}

    @abstractmethod
    def act(self, callback, coords, **kwargs):
        """perform the specified action
              callback - call after the action is complete with some
                         agreed upon parameters (e.g. Image object)
              coords - the string of coordinates to visit
              **kwargs - additional options"""


class Camera(Head):
    """an abstract class representing a camera head,
       specifies a few more methods"""

    @abstractmethod
    def livefeed(self):
        """return a still image at this very instant"""
        return []

    @abstractmethod
    def orientation(self):
        """return angular orientation of images returned wrt bench coordinates"""
        return 0

    @abstractmethod
    def resolution(self):
        """return the width, height of the camera images"""
        return 0, 0

    @abstractmethod
    def precision(self):
        """return the number of metres per (assumed square) pixel"""
        return float('inf')


class Stage:
    """abstract class representing an xy stage"""
    __metaclass__ = ABCMeta

    def __init__(self, *args, **kwargs):
        """begin initialisation (self._initialise) in a new thread,
           which should set self._garçon when done"""

        self._garçon = threading.Event() #waiter
        thread = threading.Thread(target=self._initialise, args=args, kwargs=kwargs)
        thread.daemon = True #no zombies
        thread.start()

    @abstractmethod
    def _initialise(self, *args, **kwargs):
        """main initialisation"""
        self._garçon.set()

    @abstractmethod
    def calibrate(self):
        """calibrate the stage"""

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
        """wait for initialisation to complete"""
        self._garçon.wait()

    @abstractmethod
    def register(self, head, **kwargs):
        """register a head instance; use kwargs to specify how to switch to the head?"""

    @abstractmethod
    def list(self):
        """return a set of registered heads"""
        return []

    @abstractmethod
    def bounds(self):
        """return bounding polygon, ideally a rectangle"""
        from .canvas import Rectangle
        return Rectangle(Vector(0,0), Vector(1,0), 1, 1)

    @abstractmethod
    def select(self, head):
        """select a head, make sure not to reselect an already selected head"""

    @abstractmethod
    def move(self, coord):
        """move head to coord"""

