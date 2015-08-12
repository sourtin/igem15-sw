#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from lib.hw import Stage, Head, Status, Vector, HardwareException
from lib.canvas import Rectangle
from .driver import Shapeoko

class XY(Stage):
    class Empty(Head):
        def __init__(self):
            self.stati = {'ready': False, 'idle': False, 'calibrated': True}
            self.parent = None

        def imprint(self, parent):
            self.parent = parent
            pstat = parent.status()
            if pstat.ready and pstat.calibrated:
                self.stati['ready'] = True
                self.stati['idle'] = True

        def calibrate(self):
            pass

        def status(self):
            pos = self.parent.position() if self.parent is not None else None
            attached = (self == self.parent.head) if self.parent is not None else None
            return Status(position=pos, attached=attached, **self.stati)

        def config(self):
            pass

        def act(self, cb, coords, **kwargs):
            self.parent.select(self)
            for coord in coords:
                self.parent.move(coord)
            cb(True)

    def _initialise(self, device, bounds, **options):
        self.stati = {'ready': False, 'calibrated': False}
        self.pos = Vector(0, 0)
        self.heads = set()
        self.head = None

        options['autocalibrate'] = True
        self.shapeoko = Shapeoko(device, **options)
        self.calibrate(bounds)
        self.stati['ready'] = True

        self._garcon.set()

    def calibrate(self, bounds):
        self.shapeoko.home(
            Shapeoko.Axes.x,
            Shapeoko.Axes.y,
            Shapeoko.Axes.z
        )
        self.pos = Vector(0, 0)

        self._conversions = tuple((max-min)/real for min,max,real in bounds)
        self._bounds = bounds

    def check_bounds(self, x=None, y=None, z=None):
        check = all(min <= v <= max for (v,(min,max,_)) in zip([x, y, z], self._bounds) if v is not None)
        if not check:
            print("Warning: coordinate (%r,%r,%r) outside bounds" % (x,y,z))
        return check

    def bounded(self, x=None, y=None, z=None):
        values = zip(['x','y','z'], [x,y,z])
        return dict((axis, sorted([min, v, max])[1]) for ((axis,v),(min,max,_)) in
                zip(values, self._bounds) if v is not None)

    def bounds(self):
        (_, _, xm), (_, _, ym), _ = self._bounds
        return Rectangle(Vector(0, 0), Vector(1, 0), xm, ym)

    def real2xy(self, coord):
        self.wait()
        x, y = coord
        xf, yf, _ = self._conversions
        (xo,_,_), (yo,_,_), _ = self._bounds
        vec = Vector(x * xf + xo, y * yf + yo)
        self.check_bounds(*vec)
        return vec

    def xy2real(self, coord):
        self.wait()
        x, y = coord
        self.check_bounds(x, y)
        xf, yf, _ = self._conversions
        (xo,_,_), (yo,_,_), _ = self._bounds
        vec = Vector((x - xo) / xf, (y - yo) / yf)
        return vec

    def status(self):
        self.wait()
        try:
            idle = self.shapeoko.wait()
            pos = self.shapeoko.position()
            coord = self.xy2real(Vector(pos['x'], pos['y']))
            return Status(position=coord, height=pos['z'],
                    attachment=self.head, idle=idle, **self.stati)
        except:
            self.calibrate(self._bounds)
            return Status(position=Vector(0, 0), height=pos['z'],
                    attachment=self.head, idle=True, **self.stati)

    def register(self, head):
        self.heads.add(head)
        head.imprint(self)
        return head

    def list(self):
        return list(self.heads)

    def select(self, head):
        if head == self.head:
            return

        print("Please load the following head and type done when ready:")
        print("    %r" % head)
        if  input("... [done/FAILURE]: ").strip().lower() != "done":
            raise HardwareException("User failed to load head %r" % head)
        self.head = head

    def move(self, coord):
        coord = self.bounded(*self.real2xy(coord))
        self.shapeoko.move(coord['x'], coord['y'])

    def movez(self, z):
        z = self.bounded(z=z)['z']
        self.shapeoko.move(z=z)

