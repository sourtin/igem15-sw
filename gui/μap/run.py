#!/usr/bin/env python3
from werkzeug.contrib.fixers import ProxyFix
from flask import Flask, Response, send_from_directory
import numpy as np
import cv2

# werkzeug hack
import sys
sys.path.append('/home/vil/igem/srv/sw')

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

@app.route("/")
def redir():
    return Response('<meta http-equiv="refresh" content="0;URL=/ui/main.html">')

@app.route('/ui/<path:path>')
def send_js(path):
    return send_from_directory('/home/vil/igem/srv/sw/gui/μap/ui', path)

native_z = 8
w, h = 256, 256
@app.route('/tile/<ratio>/<x>/<y>/<z>')
def tile(ratio, x, y, z):
    global native_z, w, h, maps
    ratio = float(ratio)
    x, y, z = int(x), int(y), int(z)
    factor = 1 << (native_z - z)
    xs = (factor * x, factor * (x+1))
    ys = (factor * y, factor * (y+1))
    wr = int(w * ratio)
    hr = int(h * ratio)

    im = np.full((hr,wr,3), 0, dtype=np.uint8)
    for x in range(*xs):
        ww = wr // factor
        for y in range(*ys):
            hh = hr // factor
            raw = maps.get(x*w, y*h, w, h)
            thumb = cv2.resize(raw, (ww, hh))

            xx = x-xs[0]
            yy = y-ys[0]
            im[yy*hh:(yy+1)*hh,xx*ww:(xx+1)*ww] = thumb

    _, buf = cv2.imencode('.png', im)
    return Response(buf.tobytes(), mimetype='image/png')

if __name__ == '__main__':
    from gui.μap.maps import MicroMaps
    maps = MicroMaps()
    app.run('0.0.0.0', 8080, debug=True)

