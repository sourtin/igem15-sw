#!/usr/bin/env python2
from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response

from PIL import Image
import StringIO

def redir(request):
    return Response('<meta http-equiv="refresh" content="0;URL=/ui/main.html">')

def tile(request):
    img_filename = "ui/stage.jpg"
    im = Image.open(img_filename)
    assert isinstance(im, Image.Image)

    w, h = im.size

    mintilesize = int(max(w, h) / 512)
    maxzoomlevel = int(math.log(mintilesize, 2))

    #print im.size

    z=int(request.matchdict['z'])
    x=int(request.matchdict['x'])
    y=int(request.matchdict['y'])

    tilesize =  w / int(2**(z))

    numxtiles = int(w / tilesize)
    numytiles = int(h / tilesize)

    x = x % numxtiles
    y = y % numytiles

    im = im.crop([x * tilesize, y*tilesize,(x+1)*tilesize, (y+1)*tilesize])

    output = StringIO.StringIO()

    im.resize([256, 256]).save(output, format='png')

    contents = output.getvalue()
    output.close()
    return Response(contents, content_type="image/png")

import openslide
def andromeda(request):
    path = "/tmp/andromeda.tif"
    im = openslide.OpenSlide(path)
    im.close()


if __name__ == '__main__':
    config = Configurator()
    config.add_static_view(name='ui', path='ui/')

    config.add_route('root', '/')
    config.add_view(redir, route_name='root')

    config.add_route('tile', '/tile/{x}/{y}/{z}')
    config.add_view(tile, route_name='tile')

    app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 8080, app)
    server.serve_forever()
