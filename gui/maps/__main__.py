#!/usr/bin/env python3
from werkzeug.contrib.fixers import ProxyFix
from flask import Flask, Response, send_from_directory
import numpy as np
import cv2

# werkzeug hack
import sys
sys.path.append('/home/pi/igem15-sw')

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

@app.route("/")
def redir():
    return Response('<meta http-equiv="refresh" content="0;URL=/maps/">')

from gui.maps.micro import MicroMaps
maps_live = MicroMaps()
maps_im = {}

native_z = 8
w, h = 256, 256
def tile(maps, x, y, z):
    global native_z, w, h
    x, y, z = int(x), int(y), int(z)
    factor = 1 << (native_z - z)
    xs = (factor * x, factor * (x+1))
    ys = (factor * y, factor * (y+1))

    im = np.full((h,w,3), 0, dtype=np.uint8)
    for x in range(*xs):
        ww = w // factor
        for y in range(*ys):
            hh = h // factor
            raw = maps.get(x*w, y*h, w, h)
            thumb = cv2.resize(raw, (ww, hh))

            xx = x-xs[0]
            yy = y-ys[0]
            im[yy*hh:(yy+1)*hh,xx*ww:(xx+1)*ww] = thumb

    _, buf = cv2.imencode('.png', im)
    return Response(buf.tostring(), mimetype='image/png')

@app.route('/tile/<x>/<y>/<z>')
def live(x, y, z):
    global maps_live
    return tile(maps_live, x, y, z)

@app.route('/im/<user>/<im>/tile/<x>/<y>/<z>')
def custom(user, im, x, y, z):
    global maps_im
    root = '/home/pi/igem15-sw/captured/%s'

    user = user.replace('/', '')
    im = im.replace('/', '')
    if user.startswith('.') or im.startswith('.'):
        return "go away 5<r1p7 k1dd13"

    subpath = '%s/%s' % (user, im)
    if subpath not in maps_im:
        maps_im[subpath] = MicroMaps(root % subpath)
    return tile(maps_im[subpath], x, y, z)

if __name__ == '__main__':
    app.run('0.0.0.0', 9004, debug=True)

