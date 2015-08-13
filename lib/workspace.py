#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from queue import Queue, Empty
from threading import Thread, Event

class Workspace(object):
    """the workspace class manages an xy stage (could possibly be merged
       into the definition of the stage base class...)

       management primarily centers around queueing actions for
       the stage to complete, executing the queue, and optimising
       the queue (if desired) to reduce time"""

    def __init__(self, stage, qsize=500):
        """initialise the workspace with a given stage
              qsize - the queue buffer size, defaults to 500,
                      this prevents the computer from grinding
                      to a halt in case a large amount of actions
                      are queued (in the case of a while True loop,
                      for example); enqueue will block if the queue
                      is full until space opens up..."""

        self.stage = stage
        self.stage.wait()
        # wait for the stage to fully initialise

        self.queue = Queue(qsize)
        self.queue_optimisation = False
        self.playing = Event()
        self.playing.set()
        self.idle = Event()
        
        self.thread = Thread(target=self.worker)
        self.thread.daemon = True
        self.thread.start()

    def enqueue(self, head, coords, cb, config, options, condition=lambda:True):
        """enqueue an action, block if the queue is full
              head - a head within the xy stage
              coords - a list of coordinates to visit
              cb - a callback function
              config - hardware configuration of the head
              options - software configuration of the head/
                        hardware configuration which isn't
                        time expensive to change
              condition - optional; a function which should indicate whether the
                          action is still valid or not (e.g. make it expire after
                          a certain amount of time"""
        self.queue.put((head, coords, cb, config, options, condition))

    def optimise_queue(self, setting=None):
        """optimisation of the queue reorders the order of actions to minimise
        movement, head switches and head config switches to reduce time, but
        if a linear queue order is important, set this to off (which it is by default),
        also returns the current state;
        
        note that queue optimisation will take effect only after the currently queued
        actions complete - i.e., only actions enqueued after the call to optimise_queue
        will use the new setting; this also means that if the setting is on and you call
        optimise_queue(True) then there will be a discontinuity -- the actions before
        the call will be optimised seperately to those after the call"""

        if setting is not None:
            self.queue.put(bool(setting))
        return self.queue_optimisation

    def apparati(self):
        """list the apparati"""
        return list(self.stage.list())

    def bounds(self):
        """return bounding Polygon, typically a Rectangle"""
        return self.stage.bounds()

    def pause(self):
        """pause the stage after the current action completes"""
        self.playing.clear()

    def play(self):
        """resume the stage (should be immediate)"""
        self.playing.set()

    def wait(self):
        """wait for the stage to be idle"""
        self.idle.wait()

    def worker(self):
        """main loop - dequeues actions and executes them,
                       optimising their order if requested"""

        optimisation = False
        last = None
        items = []

        def do(item):
            """execute a single action"""
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
            """sort an action by similarity to the last performed
               action for queue optimisation;
                  1) same head?
                  2) same config?
                  3) closest?"""

            try:
                lh, lp, _, lc, *_ = last
                ih, ip, _, ic, *_ = item
                return (lh != ih, lc != ic, abs(lp[-1] - ip[0]))
            except (TypeError, IndexError):
                # no last action or last action
                # had no coordinates; all True
                # to keep the sort stable
                return True

        while True:
            if self.queue.empty():
                self.idle.set()

            self.queue_optimisation = optimisation
            if optimisation:
                try:
                    # only block if we have no items
                    # left to execute, otherwise
                    # pick up any new ones and continue
                    # with item execution
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

                # TODO: this probably shouldn't be a while loop
                #       as we don't pick up new actions to optimise
                #       and the above loop should take care of this
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


