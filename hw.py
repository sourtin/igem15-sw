#!/usr/bin/env python2
from abc import ABCMeta

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
    __metaclass__ = ABCMeta

    @abstractmethod
    def calibrate(self):
        pass

    @abstactmethod
    def status(self):
        """return information on:
         * calibration
         * idle?
         * position
         * what head is attached
        """
        pass

    @abstractmethod
    def register(self, head, **kwargs):
        """register a head instance; use kwargs to specify how to switch to the head?"""
        pass

    @abstractmethod
    def query(self):
        """return a list of registered heads"""
        pass


