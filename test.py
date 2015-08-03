#!/usr/bin/env python3
from virtual import XY, Σ, Μ, Pen, Layer, Vector
from interface.canvas import Rectangle, Polygon, Canvas
from interface.workspace import Workspace

if __name__ == '__main__':
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

    virtual = XY(w, h)
    σ = virtual.register(Σ(Layer(im, z_σ, side)))
    μ = virtual.register(Μ(Layer(im, z_μ, side), (2592,1944)))
    p = virtual.register(Pen())
    ws = Workspace(virtual)
    ws.optimise_queue(True)

    """
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
    """

    poly = Rectangle(Vector(0.05,0.05), Vector(0,1), 0.15, 0.1)
    canvas = Canvas(ws, {'a':1}, poly, 5e-6, 900, 100)

    import pprint
    pp = pprint.PrettyPrinter(indent=4).pprint


