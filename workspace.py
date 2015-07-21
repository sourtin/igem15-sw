#!/usr/bin/env python2

class Workspace(object):
    def __init__(self, stage):
        self.stage = stage
        self.stage.wait()
        self.queue_optimisation = False

    def enqueue(self, head, coords, cb, config, options):
        """head is a HW head, coords are a list of important coordinates passed,
        especially the start and end, so that the queue order can be optimised,
        cb is a callback function, config is the head config for config order
        optimisation, and options are for this particular action"""
        pass

    def optimise_queue(self, setting=None):
        """optimisation of the queue reorders the order of actions to minimise
        movement, head switches and head config switches to reduce time, but
        if a linear queue order is important, set this to off"""
        if setting is not None:
            self.queue_optimisation = setting
        return self.queue_optimisation

    def apparati(self):
        """list apparati and stati"""
        pass

    def bounds(self):
        """return bounding polygon"""
        pass

