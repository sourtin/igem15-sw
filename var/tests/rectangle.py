#!/usr/bin/env python3
from hw.shapeoko import XY
from lib.vector import Vector
from lib.canvas import Rectangle, Polygon, Canvas
from lib.workspace import Workspace
from lib.hw import Head

"""Based on the needle test, this actually is designed to use a pen and
   draw the same square ad infinitum. Ideally use a very fine-tip pen
   and some non-blotting paper (e.g. tracing???)

   the square should be about a 5cm side

   after calibration, the head will lift up about 4mm to let you position
   the pen, the pen will then be lowered by 4mm whilst drawing the square
   and lifted afterwards"""

class Needle(Head):
    """A Needle head for the shapeoko, moves through a series of
       supplied points and then stabs at the last point"""

    def __init__(self):
        self.stati = {'ready': False, 'idle': False, 'calibrated': True}
        self.parent = None

    def imprint(self, parent):
        self.parent = parent
        pstat = parent.status()
        if pstat.ready and pstat.calibrated:
            self.stati['ready'] = True
            self.stati['idle'] = True
            _, _, (z0, z1, _) = parent._bounds
            self.zs = z0, z0*0.95 + z1*0.05
            # by default, the needle down position is the calibration
            # point, and the up position is 5% above

    def calibrate(self):
        pass

    def status(self):
        pos = self.parent.position() if self.parent is not None else None
        attached = (self == self.parent.head) if self.parent is not None else None
        return Status(position=pos, attached=attached, **self.stati)

    def config(self, down=None, up=None):
        """change the down and up heights"""
        if down and up:
            self.zs = down, up
        return dict(zip(['down', 'up'], self.zs))

    def act(self, cb, coords, **kwargs):
        """move along the path given by coords and
           stab at the end"""

        self.parent.select(self)
        down, up = self.zs

        self.parent.movez(up)
        for coord in coords:
            self.parent.move(coord)

        down, up = self.zs
        self.parent.movez(down)
        self.parent.movez(up)

        cb(True)



if __name__ == '__main__':
    import os
    import glob
    import time
    import pprint
    import random
    import threading
    pp = pprint.PrettyPrinter(indent=4).pprint

    shapeoko = None
    bounds = [(0, 190, 0.1717), (0, 190, 0.1717), (-400, 0, 0.1)]
    while True:
        print("Please pick a serial device, enter to refresh, or q to exit:")
        devs = glob.glob('/dev/serial/by-id/*')
        for i in range(len(devs)):
            print(" %2d) %s" % (i, devs[i]))
        choice = input("$ ").strip()
        print()

        if 'q' in choice.lower():
            print("goodbye.")
            os._exit(0)
        else:
            try:
                dev = devs[int(choice)]
            except:
                continue

            shapeoko = XY(dev, bounds)
            break
    print(shapeoko.status())
    ε = shapeoko.register(XY.Empty())
    ν = shapeoko.register(Needle())
    shapeoko.head = ε
    shapeoko.head = ν
    ws = Workspace(shapeoko)
    ws.optimise_queue(False)

    down = -400
    up = -385
    done = threading.Event()
    ws.enqueue(ν, [Vector(0,0)], lambda _:done.set(), {'down': up, 'up': up}, {})
    done.wait()
    input("Ready? ")

    while True:
        ws.enqueue(ν, [Vector(0,0), Vector(0,0.05), Vector(0.05,0.05), Vector(0.05,0)], lambda _:None, {'down': down, 'up': down}, {})



