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

class Andromeda(object):
    def __init__(self, path):
        import openslide
        self.im = openslide.OpenSlide(path)
        assert isinstance(self.im, openslide.Openslide)

    def get(self, request):
        z=int(request.matchdict['z'])
        x=int(request.matchdict['x'])
        y=int(request.matchdict['y'])

        with BytesIO() as out:
            self.im.read_region((0,0), 8, (256,256)).save(out, format='png')
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

