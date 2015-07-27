#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from Queue import Queue
from threading import Thread

class Workspace(object):
    def __init__(self, stage):
        self.stage = stage
        self.stage.wait()
        self.queue = Queue()
        self.queue_optimisation = False
        self.thread = Thread(target=self.worker)
        self.thread.daemon = True
        self.thread.start()

    def enqueue(self, head, coords, cb, config, options):
        """head is a HW head, coords are a list of important coordinates passed,
        especially the start and end, so that the queue order can be optimised,
        cb is a callback function, config is the head config for config order
        optimisation, and options are for this particular action"""
        self.queue.put((head, coords, cb, config, options))

    def optimise_queue(self, setting=None):
        """optimisation of the queue reorders the order of actions to minimise
        movement, head switches and head config switches to reduce time, but
        if a linear queue order is important, set this to off"""
        if setting is not None:
            self.queue.put(bool(setting))
        return self.queue_optimisation

    def apparati(self):
        """list apparati"""
        return []

    def bounds(self):
        """return bounding polygon"""
        return self.stage.bounds()

    def worker(self):
        optimisation = False
        last = None
        items = []

        def do(item):
            head, coords, cb, config, options = item
            self.stage.select(head)
            self.stage.move(coords[0])
            head.config(**config)
            head.act(cb, coords, **options)
            self.queue.task_done()

        def sortkey(item):
            lh, lp, _, lc, _ = last
            ih, ip, _, ic, _ = item
            return (lh != ih, lc != ic, abs(lp[-1] - ip[0]))

        while True:
            self.queue_optimisation = optimisation
            if optimisation:
                try:
                    block = not bool(items)
                    while True:
                        item = self.queue.get(block)
                        if isinstance(item, bool):
                            optimisation = item
                            self.queue.task_done()
                            break
                        items.append(item)
                        block = False
                except Empty:
                    pass

                sort(items, key=sortkey)
                last = items.pop(0)
                do(last)

            else:
                last = self.queue.get()
                if isinstance(last, bool):
                    optimisation = last
                    self.queue.task_done()
                else:
                    do(last)


