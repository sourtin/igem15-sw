#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from queue import Queue, Empty
from threading import Thread, Event

class Workspace(object):
    def __init__(self, stage):
        self.stage = stage
        self.stage.wait()

        self.queue = Queue()
        self.queue_optimisation = False
        self.playing = Event()
        self.playing.set()
        self.idle = Event()
        
        self.thread = Thread(target=self.worker)
        self.thread.daemon = True
        self.thread.start()

    def enqueue(self, head, coords, cb, config, options, condition=lambda:True):
        """head is a HW head, coords are a list of important coordinates passed,
        especially the start and end, so that the queue order can be optimised,
        cb is a callback function, config is the head config for config order
        optimisation, and options are for this particular action"""
        self.queue.put((head, coords, cb, config, options, condition))

    def optimise_queue(self, setting=None):
        """optimisation of the queue reorders the order of actions to minimise
        movement, head switches and head config switches to reduce time, but
        if a linear queue order is important, set this to off"""
        if setting is not None:
            self.queue.put(bool(setting))
        return self.queue_optimisation

    def apparati(self):
        """list apparati"""
        return list(self.stage.list())

    def bounds(self):
        """return bounding polygon"""
        return self.stage.bounds()

    def pause(self):
        self.playing.clear()

    def play(self):
        self.playing.set()

    def wait(self):
        self.idle.wait()

    def worker(self):
        optimisation = False
        last = None
        items = []

        def do(item):
            self.idle.clear()
            self.playing.wait()
            head, coords, cb, config, options, condition = item

            if condition():
                self.stage.select(head)

                if len(coords):
                    self.stage.move(coords[0])

                head.config(**config)
                head.act(cb, coords, **options)

            self.queue.task_done()

        def sortkey(item):
            try:
                lh, lp, _, lc, *_ = last
                ih, ip, _, ic, *_ = item
                return (lh != ih, lc != ic, abs(lp[-1] - ip[0]))
            except TypeError:
                return True

        while True:
            if self.queue.empty():
                self.idle.set()

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

                while len(items):
                    items.sort(key=sortkey)
                    last = items.pop(0)
                    do(last)

            else:
                last = self.queue.get()
                if isinstance(last, bool):
                    optimisation = last
                    self.queue.task_done()
                else:
                    do(last)


