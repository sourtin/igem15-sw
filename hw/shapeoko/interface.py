#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from lib.hw import Stage, Status, Vector
from . import driver

class XY(Stage):
    def _intialise(self, device):
        print('hi')
        self.stati = {'ready': False, 'idle': False, 'calibrated': False}
        self.pos = Vector(0,0)
        self.heads = set()
        self.head = None

        self.shapeoko = driver.Shapeoko(device)
        self.calibrate()
        self.stati['ready'] = True
        self.stati['idle'] = True
        self._garcon.set()

    def calibrate(self):
        self.shapeoko.home([
            driver.Axes.X,
            driver.Axes.Y,
            driver.Axes.Z
        ])
        self.shapeoko.wait()

    def status(self):
        self.wait()
        return Status(position=self.pos, attachment=self.head, **self.stati)

    def register(self, head):
        self.heads.add(head)
        head.imporint(self)
        return head

    def list(self):
        return list(self.heads)

    def bounds(self):
        raise NotImplementedError

    def select(self, head):
        raise NotImplementedError

    def move(self, coord):
        raise NotImplementedError
        self.shapeoko.move([coord.x(), coord.y(), None])
        self.shapeoko.wait()

    def movez(self, z):
        raise NotImplementedError
        self.shapeoko.move([None, None, z])
        self.shapeoko.wait()

    def position(self):
        raise NotImplementedError


if __name__ == '__main__':
    import glob
    devs = glob.glob('/dev/ttyACM*')
    s = XY(devs[0])
    print(s.status())

        

