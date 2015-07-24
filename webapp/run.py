from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response

def redir(request):
    return Response('<meta http-equiv="refresh" content="0;URL=/ui/main.html">')

def tile(request):
    return Response(request.matchdict['x'] + "," + request.matchdict['y'] + "," + request.matchdict['z'])

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
