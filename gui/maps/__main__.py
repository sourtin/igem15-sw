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
    return Response('<meta http-equiv="refresh" content="0;URL=/maps/main.html">')

native_z = 8
w, h = 256, 256
@app.route('/tile/<x>/<y>/<z>')
def tile(x, y, z):
    import time
    start = time.time()
    global native_z, w, h, maps
    x, y, z = int(x), int(y), int(z)
    #y = (1 << z) - y
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
    print(time.time() - start)
    return Response(buf.tostring(), mimetype='image/png')

if __name__ == '__main__':
    from gui.maps.micro import MicroMaps
    maps = MicroMaps()
    app.run('0.0.0.0', 9005, debug=True)

