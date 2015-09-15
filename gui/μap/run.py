#!/usr/bin/env python3
from werkzeug.contrib.fixers import ProxyFix
from flask import Flask, request, send_from_directory, Response

from PIL import Image
import numpy as np
import cv2
from io import BytesIO
import math

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

@app.route("/")
def redir(request):
    return Response('<meta http-equiv="refresh" content="0;URL=/ui/main.html">')

@app.route('/ui/<path:path>')
def send_js(path):
    return send_from_directory('ui', path)

native_z = 8
@app.route('/tile/<x>/<y>/<z>')
def tile(x, y, z):
    global native_z
    x, y, z = int(x), int(y), int(z)
    factor = 1 << (native_z - z)
    xs = (factor * x, factor * (x+1))
    ys = (factor * y, factor * (y+1))

    tile = np.full((256,256,3),255,np.uint8)
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(tile,'xs:%d,%d'%xs,(50,80), font, 1,(255,127,127),2,cv2.LINE_AA)
    cv2.putText(tile,'ys:%d,%d'%ys,(50,130), font, 1,(255,127,127),2,cv2.LINE_AA)
    cv2.putText(tile,'z: %d'%z,(50,180), font, 1,(255,127,127),2,cv2.LINE_AA)
    cv2.rectangle(tile,(1,1),(255,255),(0,255,0),3)
    _, buf = cv2.imencode('.png', tile)
    return Response(buf.tobytes(), mimetype='image/png')


#class Andromeda(object):
#    def __init__(self, path):
#        import openslide
#        self.im = openslide.OpenSlide(path)
#        self.tile = 256, 256
#
#         # calculate bounding tiles for outermost zoom
#         iw, ih = self.im.level_dimensions[-1]
#         tw, th = self.tile
#         self.nx = math.ceil(0.5 * iw / tw)
#         self.ny = math.ceil(0.5 * ih / th)
#
#         # offsets
#         iw, ih = self.im.dimensions
#         self.zmax = self.im.level_count - 1
#         bw = 2 * (self.nx << self.zmax) * tw
#         bh = 2 * (self.ny << self.zmax) * th
#         self.ox = int((bw - iw)/2)
#         self.oy = int((bh - ih)/2)
#
#     def map(self, x, y, z):
#         # translate tile coords to level 0
#         tw, th = self.tile
#         x = ((x*tw) << z) - self.ox
#         y = ((y*th) << z) - self.oy
#
#         # calculate translation parameters if necessary
#         x_ = 0 if x<0 else x
#         y_ = 0 if y<0 else y
#         xt = x_ - x
#         yt = y_ - y
#
#         # translate level 0 coordss to level z
#         xt >>= z
#         yt >>= z
#
#         # pull from the tiff and translate if necessary
#         pil = self.im.read_region((x_, y_), z, self.tile)
#         return translate(pil, (xt, yt))
#
#     def get(self, request):
#         # get x,y,z coords
#         z = int(request.matchdict['z'])
#         z_ = self.zmax - int(request.matchdict['z'])
#         x = int(request.matchdict['x'])
#         y = int(request.matchdict['y'])
#
#         # transform x,y into bounding tiles calculated earlier
#         # so that we can centre everything nicely...
#         x += self.nx << z
#         y += self.ny << z
#
#         # generate 256x256 .png for leaflet.js
#         with BytesIO() as out:
#             self.map(x, y, z_).save(out, format='png')
#             return Response(out.getvalue(), content_type="image/png")

#    config.add_route('tile', '/tile/{x}/{y}/{z}')
#    config.add_view(tile, route_name='tile')

#    andromeda = Andromeda("/tmp/andromeda.tif")
#    config.add_route('andromeda', '/andromeda/{x}/{y}/{z}')
#    config.add_view(andromeda.get, route_name='andromeda')



if __name__ == '__main__':
    app.run('0.0.0.0', 8080, debug=True)
