#!/usr/bin/env python3
from hw.virtual import XY, Σ, Μ, Pen, Layer, Vector
from lib.canvas import Rectangle, Polygon, Canvas
from lib.workspace import Workspace

"""test the virtual xy stage with three heads:
      σ, an overhead camera
      μ, a microscope
      p, a pen
   the cameras are given a gigapixel image of andromeda,
   to set this up follow these instructions from the
   README.md:

       place `andromeda.tif` ([a gigapixel image of andromeda](https://www.spacetelescope.org/images/heic1502a/), make sure to convert to a pyramidal tif using `vips tiffsave /path/to/original.tif /tmp/andromeda.tif --tile --tile-width=256 --tile-height=256 --pyramid`; you may use the 40K tif rather than the proprietary psb version) in `/tmp`

   it will then load this image using openslide, setup
   two layers -- one zoomed out for the overhead camera
   and one intermediately zoomed in for the microscope
   to simulate approximate camera resolution (?)

   we will then enqueue 6 arbitrary points using queue
   optimisation; then we create a canvas object and
   display all the images using feh

   finally you are free to control the stage yourself,
   just run the test using the interactive flag
   (this should automatically be applied if you use
    test.py in the repository root :P)"""

if __name__ == '__main__':
    import pprint
    pp = pprint.PrettyPrinter(indent=4).pprint

    import openslide
    im = openslide.OpenSlide('/tmp/andromeda.tif')

    # coordinate system
    side = 1.
    iw, ih = im.dimensions
    factor = max(iw, ih) / side
    w, h = map(lambda v: v/factor, im.dimensions)

    # zoom levels
    z_σ = im.level_count // 2
    z_μ = 0

    # hardware
    virtual = XY(w, h)
    σ = virtual.register(Σ(Layer(im, z_σ, side)))
    μ = virtual.register(Μ(Layer(im, z_μ, side), (2592,1944)))
    p = virtual.register(Pen())
    ws = Workspace(virtual)

    # test queuing
    ws.optimise_queue(True)
    ws.pause()
    imcb = lambda im:im.show()
    ws.enqueue(σ, [Vector(0,0)], lambda _:print(0), {}, {})
    ws.enqueue(μ, [Vector(0.1065,0.1432)], lambda _:print(1), {'a':1}, {})
    ws.enqueue(μ, [Vector(0.2789,0.2809)], lambda _:print(2), {'a':2}, {})
    ws.enqueue(μ, [Vector(0.1012,0.2544)], lambda _:print(3), {'a':2}, {})
    ws.enqueue(μ, [Vector(0.1065,0.1432)], lambda _:print(4), {'a':2}, {})
    ws.enqueue(μ, [Vector(0.2789,0.2809)], lambda _:print(5), {'a':1}, {})
    ws.enqueue(μ, [Vector(0.1012,0.2544)], lambda _:print(6), {'a':1}, {})
    ws.play()

    # test canvas
    μ.calibrate()
    ws.optimise_queue(False)
    poly = Rectangle(Vector(0.05,0.05), Vector(0,1), 0.15, 0.1)
    canvas = Canvas(ws, {'a':1}, poly, 5e-6, 900, 100)
    canvas.wait(False)
    ws.optimise_queue(True)

    # print images
    print()
    for x,r,im in canvas.images:
        print("Image %r at %r:" % (x,r))
        im.show()


