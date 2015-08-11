#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from lib.hw import Stage, Status, Vector, HardwareException
from .driver import Shapeoko

class XY(Stage):
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

        (xx, xr), (yy, yr), z = bounds
        self._conversions = (xx / xr, yy / yr)
        self._bounds = bounds[:2]
        self._boundz = z

    def real2xy(self, coord):
        self.wait()
        (_, xm), (_, ym) = self._bounds
        xf, yf = self._conversions
        x, y = coord

        if x < 0 or x > xm or y < 0 or y > ym:
            print("Warning[Shapeoko:XY.real2xy]: coordinate outside bounds")
        return Vector(x * xf, y * yf)

    def xy2real(self, coord):
        self.wait()
        (xm, _), (ym, _) = self._bounds
        xf, yf = self._conversions
        x, y = coord

        if x < 0 or x > xm or y < 0 or y > ym:
            print("Warning[Shapeoko:XY.xy2real]: coordinate outside bounds")
        return Vector(x / xf, y / yf)

    def status(self):
        self.wait()
        try:
            idle = self.shapeoko.wait()
            pos = self.shapeoko.position()
            coord = self.xy2real(Vector(pos['x'], pos['y']))
            return Status(position=coord, height=pos['z'],
                    attachment=self.head, idle=idle, **self.stati)
        except:
            bounds = self._bounds + [self._boundz]
            self.calibrate(bounds)
            return Status(position=Vector(0, 0), height=pos['z'],
                    attachment=self.head, idle=True, **self.stati)

    def register(self, head):
        self.heads.add(head)
        head.imprint(self)
        return head

    def list(self):
        return list(self.heads)

    def bounds(self):
        (_, xm), (_, ym) = self._bounds
        return Rectangle(Vector(0, 0), Vector(1, 0), xm, ym)

    def boundz(self):
        return self._boundz

    def bounded(self, coord):
        (xm, _), (ym, _) = self._bounds
        x, y = coord
        x = sorted([0, x, xm])[1]
        y = sorted([0, y, ym])[1]
        return Vector(x, y)

    def boundedz(self, z):
        zn, zx = self._boundz
        return sorted([zn, z, zx])[1]

    def select(self, head):
        print("Please load the following head and type done when ready:")
        print("    %r" % head)
        answer = input("... [done/FAILURE]: ").strip().lower()
        if answer != "done":
            raise HardwareException("User failed to load head %r" % head)

    def move(self, coord):
        coord = self.bounded(self.real2xy(coord))
        print(coord)
        self.shapeoko.move(coord.x(), coord.y())

    def movez(self, z):
        z = self.boundedz(z)
        self.shapeoko.move(z=z)

if __name__ == '__main__':
    import os
    import glob

    s = None
    bounds = [(190, 0.17), (190, 0.17), (-400, 0)]
    while True:
        print("Please pick a serial device, enter to refresh, or q to exit:")
        devs = glob.glob('/dev/serial/by-id/*')
        for i in range(len(devs)):
            print(" %2d) %s" % (i, devs[i]))
        choice = input("# ").strip()
        print()

        if 'q' in choice.lower():
            print("goodbye.")
            os._exit(0)
        else:
            try:
                dev = devs[int(choice)]
            except:
                continue

            s = XY(dev, bounds)
            break
    print(s.status())

        

