#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from lib.hw import Stage, Head, Status, Vector, HardwareException
from lib.canvas import Rectangle
from .driver import Shapeoko

class XY(Stage):
    """Shapeoko Stage interface"""

    class Empty(Head):
        """Shapeoko Empty head for testing - only allows movement of the head"""
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
        """initialise the shapeoko
              device: the serial file, e.g. /dev/serial/by-id/shapeoko
              bounds: [(xmin, xmax, xreal), (y...), (z...)]
                 where xmin,xmax are the shapeoko coordinate bounds
                 and xreal is the real length in meters between xmin and xmax
              options: autocalibrate: automatically calibrate and return to last
                                      known position after disconnection, defaults
                                      to true"""

        self.stati = {'ready': False, 'calibrated': False}
        self.pos = Vector(0, 0)
        self.heads = set()
        self.head = None

        options['autocalibrate'] = True
        self.shapeoko = Shapeoko(device, **options)
        self.calibrate(bounds)
        self.stati['ready'] = True

        # we're in our own thread, signal initialisation is complete
        self._garçon.set()

    def calibrate(self, bounds=None):
        """(re)calibrate the shapeoko and calculate coordinate conversion factors"""

        if not bounds:
            bounds = self._bounds
        if not shapeoko.autocalibrate or self.stati['calibrated']:
            # first time, calibrate iff not autocalibrated
            # subsequent times, calibrate anyway
            self.shapeoko.home(
                Shapeoko.Axes.x,
                Shapeoko.Axes.y,
                Shapeoko.Axes.z
            )

        self._conversions = tuple((max-min)/real for min,max,real in bounds)
        self._bounds = bounds

        pos = self.shapeoko.position()
        self.pos = self.xy2real(Vector(pos['x'], pos['y']))
        self.stati['calibrated'] = True

    def check_bounds(self, x=None, y=None, z=None, verbose=True):
        """check if a coordinate is within the calibration bounds"""
        check = all(min <= v <= max for (v,(min,max,_)) in zip([x, y, z], self._bounds) if v is not None)
        if verbose and not check:
            print("Warning: coordinate (%r,%r,%r) outside bounds" % (x,y,z))
        return check

    def bounded(self, x=None, y=None, z=None):
        """ensure coordinate is within the calibration bounds"""
        values = zip(['x','y','z'], [x,y,z])
        return dict((axis, sorted([min, v, max])[1]) for ((axis,v),(min,max,_)) in
                zip(values, self._bounds) if v is not None)

    def bounds(self):
        """return the bounding rectangle, only xy"""
        (_, _, xm), (_, _, ym), _ = self._bounds
        return Rectangle(Vector(0, 0), Vector(1, 0), xm, ym)

    def boundz(self):
        """return the z bounds, currently arbitrary units..."""
        _, _, (zmin, zmax, _) = self._bounds
        return zmin, zmax

    def real2xy(self, coord):
        """convert real-world coordinates (in metres) to
           internal shapeoko coordinates (supposedly mm but
           not really); only xy"""

        self.wait()
        x, y = coord
        xf, yf, _ = self._conversions
        (xo,_,_), (yo,_,_), _ = self._bounds
        vec = Vector(x * xf + xo, y * yf + yo)
        self.check_bounds(*vec)
        return vec

    def xy2real(self, coord):
        """convert shapeoko internal coordinates (supposedly mm
           but not really) into real-world (in metres); only xy"""

        self.wait()
        x, y = coord
        self.check_bounds(x, y)
        xf, yf, _ = self._conversions
        (xo,_,_), (yo,_,_), _ = self._bounds
        vec = Vector((x - xo) / xf, (y - yo) / yf)
        return vec

    def status(self):
        """return current status, including xy position, z height,
           calibration, currently atteched head, whether ready or idle, etc"""

        # wait for initialisation thread to complete
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
        """register a specified head"""
        self.heads.add(head)
        head.imprint(self)
        return head

    def list(self):
        """list registered heads"""
        return list(self.heads)

    def select(self, head, manual=True):
        """select a given head
              manual: whether the head needs to be manually loaded
                      (default True); the user will be prompted to
                      load it and enter 'done' when finished."""

        if head == self.head:
            return

        if manual:
            print("Please load the following head and type done when ready:")
            print("    %r" % head)
            if  input("... [done/FAILURE]: ").strip().lower() != "done":
                raise HardwareException("User failed to load head %r" % head)
        self.head = head

    def move(self, coord):
        """move to xy coordinate (in real-world units -- metres)"""
        coord = self.bounded(*self.real2xy(coord))
        self.shapeoko.move(coord['x'], coord['y'])

    def movez(self, z):
        """move in the z-direction (currently in arbitrary units, check .boundz())"""
        z = self.bounded(z=z)['z']
        self.shapeoko.move(z=z)

    def origin(self):
        """move to the origin"""
        self.shapeoko.move(*[o for o,_,_ in self._bounds])

