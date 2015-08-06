#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod
from lib.vector import Vector
import threading

class HardwareException(Exception):
    pass

class Status(object):
    def __init__(self, ready, idle, calibrated, position, **kwargs):
        kwargs['ready'] = ready
        kwargs['idle'] = idle
        kwargs['calibrated'] = calibrated
        kwargs['position'] = position
        self.__dict__ = kwargs


class Head:
    __metaclass__ = ABCMeta

    @abstractmethod
    def imprint(self, parent):
        # be adopted by parent
        pass

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
        thread = threading.Thread(target=self._initialise, args=args, kwargs=kwargs)
        thread.daemon = True
        thread.start()

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
        """return a set of registered heads"""
        return {}

    @abstractmethod
    def bounds(self):
        """return bounding polygon, ideally a rectangle"""
        from .canvas import Rectangle
        return Rectangle(Vector(0,0), Vector(1,0), 1, 1)

    @abstractmethod
    def select(self, head):
        """select a head, make sure not to reselect an already selected head"""
        pass

    @abstractmethod
    def move(self, coord):
        """move head to coord"""
        pass


