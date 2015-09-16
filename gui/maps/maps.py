#!/usr/bin/env python3
from lib.vector import Vector
from lib.stitch import ReferenceStitcher, StitchContext
import requests
import requests.auth
import numpy as np
import cv2
import time
import json

limits = {
    'caps': 200 * 1048576,
    'stitching': 32 * 1048576,
    'xmin': float('-inf'),
    'xmax': float('+inf'),
    'ymin': float('-inf'),
    'ymax': float('+inf')
}

factors = {
    'signx': -1,
    'signy': +1,
    # rots / metre movement
    # 500 rots ~ 110e-6 metres
    'rot': 500/(110e-6),
}

context = StitchContext(limits['stitching'])
context.features.hsv(1).histeq()
requests.packages.urllib3.disable_warnings()

class MicroMaps:
    def __init__(self):
        self.pos = None
        self.caps = []
        self.dims = None, None
        self._fov = None

    def prune(self):
        if self.pos is None:
            return
        def score(cap):
            (xc, yc), _ = cap
            (xr, yr) = self.pos
            return (xc-xr)**2 + (yc-yr)**2
        self.caps.sort(key=score)
        while sum(im.nbytes for _,im in self.caps) > limits['caps']:
            self.caps.pop()

    def fov(self):
        if self._fov is None:
            with open('/home/vil/igem/srv/sw/gui/portal/webshell/fov.json', 'r') as f:
                w, h = json.loads(f.read())
                self._fov = w*1e-6, h*1e-6
        return self._fov

    def update_bounds(self, opos, dpos):
        """based on the amount we managed to move, see if
           we were in fact able to; if not, assume we've
           reached the boundaries
                opos -- old position
                dpos -- desired position
                self.pos -- 'actual' position"""

        ox, oy = opos
        dx, dy = dpos
        nx, ny = self.pos
        w, h = self.dims

        threshold = 0.5
        # only need one condition as signs cancel
        if abs(dx - ox) > 0 and (nx - ox) / (dx - ox) < threshold:
            if dx > ox:
                limits['xmax'] = nx + w
            else:
                limits['xmin'] = nx
            print("rebounded x %r %r %r" % (ox,dx,nx))
        if False and abs(dy - oy) > 0 and (ny - oy) / (dy - oy) < threshold:
            if dy > oy:
                limits['ymax'] = ny + h
            else:
                limits['ymin'] = ny
            print("rebounded y %r %r %r" % (oy,dy,ny))

        print("bounds (%r < x < %r) (%r < y < %r)" %
                (limits['xmin'], limits['xmax'],
                    limits['ymin'], limits['ymax']))

    """ pixels, metres, rots """
    def px2m(self, pixels):
        wp, hp = self.dims
        wm, hm = self.fov()
        factor = 0.5 * (wm/wp + hm/hp)
        return pixels * factor
    def m2px(self, metres):
        wp, hp = self.dims
        wm, hm = self.fov()
        factor = 0.5 * (wp/wm + hp/hm)
        return pixels * factor
    def m2rot(self, metres):
        return factors['rot'] * metres
    def rot2m(self, rots):
        return rots / factors['rot']
    def px2rot(self, pixels):
        return self.m2rot(self.px2m(pixels))
    def rot2px(self, rots):
        return self.m2px(self.rot2m(rots))
    """ end conversions """

    def capture(self, x=None, y=None):
        def _request(url):
            return requests.get("https://pigem:9000" + url, verify=False,
                    auth=requests.auth.HTTPBasicAuth('admin', 'test')).content

        def _raw():
            #return cv2.imread("/home/vil/net/capture_stream.png", cv2.IMREAD_COLOR)
            png = _request("/_webshell/capture_stream/")
            data = np.fromstring(png, dtype=np.uint8)
            return cv2.imdecode(data, cv2.IMREAD_COLOR)

        def _motor(axis, amount):
            amount = int(amount)
            print(axis, amount)
            #return
            _request("/_webshell/control/motor/%d/%d" % (axis, amount))

        if self.pos is None:
            im = _raw()
            h, w = im.shape[:2]
            self.dims = w, h
            self.pos = x-w//2, y-h//2
            cap = self.pos, im
            self.caps.append(cap)
            return cap

        else:
            # early alpha; image stitching is not very reliable
            # so we will avoid adding other images
            # perhaps improve upon cv2.bfmatcher? (see lib.stitch)
            return None

            x0, y0 = self.pos
            δx = factors['signx'] * self.px2rot(x - x0)
            δy = factors['signy'] * self.px2rot(y - y0)
            _motor(0, δx)
            _motor(1, δy)

            import time
            time.sleep(2)
            print('waited!!')

            # wait for completion!?
            self.pos = x, y
            self.prune()

            # image stitching bad, try overlaying?
            """ the hackiest hack that ever hacked
                will not work well even slightly
                what am I even doing with my life """
            cap = (x, y), _raw()
            self.caps.append(cap)
            return cap
            # this did not work well .. as expected

            self.pos = x0, y0
            im = _raw()
            cap = None
            for pos, ref in self.caps:
                cand = ReferenceStitcher(context, ref, pos).align(im)
                if cand is not None:
                    self.pos = cand[0]
                    self.caps.append(cand)
                    cap = cand
                    print('capped', self.pos)

            self.update_bounds((x0, y0), (x, y))
            return cap

    def match(self, x, y, w, h, timeout=15):
        def rect_in_rect(cap):
            (xc1, yc1), im = cap
            hc, wc = im.shape[:2]
            xr1, yr1 = x, y
            xr2, yr2 = x+w, y+h
            xc2, yc2 = xc1+wc, yc1+hc

            return (xc1 <= xr1 <= xr2 <= xc2 and
                    yc1 <= yr1 <= yr2 <= yc2)

        if self.pos is None:
            self.capture(x, y)
        matches = [cap for cap in self.caps if rect_in_rect(cap)]
        start = time.time()
        while not len(matches) and (time.time() - start) < timeout:
            # calculate suitable trajectory to target
            ww, hh = self.dims
            ori = Vector(*self.pos)
            dst = Vector(x, y) - Vector(ww/2, hh/2)
            vec = dst - ori
            δ = vec.normalise() * (ww/2)
            xx, yy = ori + (vec if vec.r() < δ.r() else δ)

            print(ori, dst, (x,y), δ)

            new = self.capture(xx, yy)
            if new is None:
                break
            elif rect_in_rect(new):
                matches.append(new)
        return matches

    def get_test(self, x, y, w, h):
        import hashlib
        m = hashlib.md5()
        m.update(("%d %d" % (x,y)).encode())
        d = m.digest()
        raw = np.full((h,w,3), list(d[:3]), dtype=np.uint8)
        return raw

    def get(self, x, y, w, h):
        canvas = np.full((h,w,3), 0, dtype=np.uint8)
        if (limits['xmin'] <= x and x+w <= limits['xmax'] and
                limits['ymin'] <= y and y+h <= limits['ymax']):
            for (x0, y0), cap in self.match(x, y, w, h):
                region = cap[y-y0:y-y0+h,x-x0:x-x0+w,:]
                canvas = np.maximum.reduce([canvas, region])
        return canvas

