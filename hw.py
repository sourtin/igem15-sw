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


