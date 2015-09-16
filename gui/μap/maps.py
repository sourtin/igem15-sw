#!/usr/bin/env python3
import requests
import requests.auth
import numpy as np
import cv2

limits = {
    'caps': 200 * 1048576,
    'stitching': 32 * 1048576
}

class MicroMaps:
    def __init__(self):
        self.pos = None
        self.caps = []

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

    def capture(self, x=None, y=None):
        def _request(url):
            return requests.get("https://pigem:9000" + url, verify=False,
                    auth=requests.auth.HTTPBasicAuth('admin', 'test')).content

        def _raw():
            return cv2.imread("/home/vil/net/capture_stream.png", cv2.IMREAD_COLOR)
            png = _request("/_webshell/capture_stream/")
            data = np.fromstring(png, dtype=np.uint8)
            return cv2.imdecode(data, cv2.IMREAD_COLOR)

        def _motor(axis, amount):
            _request("/_webshell/control/motor/%d/%d" % (axis, amount))

        if self.pos is None:
            im = _raw()
            h, w = im.shape[:2]
            self.pos = x-128, y-128 # 128 is a magic number hack
                                    # for consistency in the algorithm
            cap = (x-w//2,y-h//2), im
            self.caps.append(cap)
            return cap

        else:
            # plot a trajectory and follow it
            # align as we go to fix for real world
            raise Exception

    def match(self, x, y, w, h):
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
        return [cap for cap in self.caps if rect_in_rect(cap)]

    def get_test(self, x, y, w, h):
        import hashlib
        m = hashlib.md5()
        m.update(("%d %d" % (x,y)).encode())
        d = m.digest()
        raw = np.full((h,w,3), list(d[:3]), dtype=np.uint8)
        return raw

    def get(self, x, y, w, h):
        canvas = np.full((h,w,3), 0, dtype=np.uint8)
        for (x0, y0), cap in self.match(x, y, w, h):
            region = cap[y-y0:y-y0+h,x-x0:x-x0+w,:]
            canvas = np.maximum.reduce([canvas, region])
        return canvas

