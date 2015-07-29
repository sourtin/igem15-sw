#!/usr/bin/env python3
from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response

from PIL import Image
from io import BytesIO
import math

def redir(request):
    return Response('<meta http-equiv="refresh" content="0;URL=/ui/main.html">')

def tile(request):
    img_filename = "ui/stage.jpg"
    im = Image.open(img_filename)
    assert isinstance(im, Image.Image)

    w, h = im.size

    mintilesize = int(max(w, h) / 512)
    maxzoomlevel = int(math.log(mintilesize, 2))

    z=int(request.matchdict['z'])
    x=int(request.matchdict['x'])
    y=int(request.matchdict['y'])

    tilesize =  int(w / (1<<z))

    numxtiles = int(w / tilesize)
    numytiles = int(h / tilesize)

    x = x % numxtiles
    y = y % numytiles

    im = im.crop([x * tilesize, y*tilesize,(x+1)*tilesize, (y+1)*tilesize])

    with BytesIO() as output:
        im.resize([256, 256]).save(output, format='png')
        return Response(output.getvalue(), content_type="image/png")

def translate(im, origin, wrap=False):
    ox, oy = origin
    w, h = im.size
    tr = Image.new('RGBA', (w, h))

    for x in range(w):
        for y in range(h):
            nx = (x + ox) % w if wrap else x + ox
            ny = (y + oy) % h if wrap else y + oy
            if 0 <= nx < w and 0 <= ny < h:
                tr.putpixel((nx, ny), im.getpixel((x, y)))
    return tr

def map(im_size, tile_size):
    ceil_odd = lambda x: 1 + 2*math.ceil((x - 1)/2)
    iw, ih = im_size
    tw, th = tile_size
    nx = ceil_odd(iw / tw)
    ny = ceil_odd(ih / th)

    mw = nx * tw #:
    mh = ny * th #tile bounding box
    bx = (nx - 1)//2 #:
    by = (ny - 1)//2 #tile coord bounds
    ox = (mw - iw)//2 #:
    oy = (mh - ih)//2 #origin

    return lambda x,y: (tw*(x + bx) - ox, th*(y + by) - oy)

def render_tile(im, origin, z, size):
    x, y = origin
    x_ = 0 if x<0 else x #:
    y_ = 0 if y<0 else y #>0
    xt = x_ - x #:
    yt = y_ - y #translation

    x_ <<= z
    y_ <<= z
    print((x_,y_), z, size, xt, yt)
    return translate(im.read_region((x_,y_), z, size), (xt, yt))



class Andromeda(object):
    def __init__(self, path):
        import openslide
        self.im = openslide.OpenSlide(path)
        self.tile = 256, 256
        assert isinstance(self.im, openslide.OpenSlide)

    def get(self, request):
        im = self.im
        dims = im.level_dimensions
        dimn = len(dims) - 1


        z = dimn - int(request.matchdict['z'])
        x = int(request.matchdict['x'])
        y = int(request.matchdict['y'])

        print(x, y, z, dims[z])
        mapper = map(dims[z], self.tile)

        with BytesIO() as out:
            render_tile(self.im, mapper(x,y), z, self.tile).save(out, format='png')
            return Response(out.getvalue(), content_type="image/png")

if __name__ == '__main__':
    config = Configurator()
    config.add_static_view(name='ui', path='ui/')

    config.add_route('root', '/')
    config.add_view(redir, route_name='root')

    config.add_route('tile', '/tile/{x}/{y}/{z}')
    config.add_view(tile, route_name='tile')

    andromeda = Andromeda("/tmp/andromeda.tif")
    config.add_route('andromeda', '/andromeda/{x}/{y}/{z}')
    config.add_view(andromeda.get, route_name='andromeda')

    app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 8080, app)
    server.serve_forever()

