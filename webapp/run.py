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
    x=int(request.matchdict['x']) * 256
    y=int(request.matchdict['y']) * 256
    output = StringIO.StringIO()
    im.crop((x, y, x+256, y+256)).save(output, format='png')
    contents = output.getvalue()
    output.close()
    return Response(contents, content_type="image/png")


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
