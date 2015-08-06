#!/usr/bin/env
from hw.shapeoko import Shapeoko, Axes
from interface.vector import Vector
from math import pi
import time
import glob

if __name__ == '__main__':
    com = glob.glob('/dev/ttyACM*')[0]
    print(com)
    stage = Shapeoko(com)
    time.sleep(2)
    stage.home([Axes.X, Axes.Y, Axes.Z])

    origin = Vector(100,100)
    radius = 80
    d2r = lambda deg: deg * pi / 180
    move = lambda v: stage.move([v.x(), v.y(), None])

    time.sleep(15)
    
    move(origin)
    for deg in range(0, 360, 15):
        point = origin + Vector.from_polar(radius, d2r(deg))
        move(point)
        time.sleep(4)

    stage.close()
    time.sleep(60)

