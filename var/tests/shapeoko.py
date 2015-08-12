#!/usr/bin/env python3
from hw.shapeoko import XY
from lib.vector import Vector
from lib.canvas import Rectangle, Polygon, Canvas
from lib.workspace import Workspace

if __name__ == '__main__':
    import os
    import glob
    import time
    import pprint
    import random
    pp = pprint.PrettyPrinter(indent=4).pprint

    shapeoko = None
    bounds = [(0, 190, 0.17), (0, 190, 0.17), (-400, 0, 0.1)]
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
    shapeoko.head = ε
    ws = Workspace(shapeoko)

    # test queuing
    ws.optimise_queue(True)
    ws.pause()
    imcb = lambda im:im.show()
    ws.enqueue(ε, [Vector(0,0)], lambda _:print(0), {}, {})
    ws.enqueue(ε, [Vector(0.05,0.05)], lambda _:print(1), {}, {})
    ws.enqueue(ε, [Vector(0.06,0.05)], lambda _:print(2), {}, {})
    ws.enqueue(ε, [Vector(0.05,0.04)], lambda _:print(3), {}, {})
    ws.enqueue(ε, [Vector(0.08,0.08)], lambda _:print(4), {}, {})
    ws.enqueue(ε, [Vector(0.05,0.05)], lambda _:print(5), {}, {})
    ws.enqueue(ε, [Vector(0.02,0.05)], lambda _:print(6), {}, {})
    ws.play()

    time.sleep(2)
    ws.wait()
    num = input("How many random coordinates? ")

    random.seed()
    uni = random.uniform
    rcoord = lambda:Vector(uni(0,0.1), uni(0,0.1))
    ws.enqueue(ε, [rcoord() for i in range(int(num))], lambda _:None, {}, {})


