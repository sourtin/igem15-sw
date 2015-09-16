#!/usr/bin/env python3
import requests
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
        def _raw():
            return np.full((2048,1536,3), 127)

        if self.pos is None:
            raise Exception


    def match(self, x, y, w, h):
        if self.pos is None:
            return self.capture()
            self.pos = x+w//2, y+h//2

    def get_test(self, x, y, w, h):
        import hashlib
        m = hashlib.md5()
        m.update(("%d %d" % (x,y)).encode())
        d = m.digest()
        raw = np.full((h,w,3), list(d[:3]), dtype=np.uint8)
        return raw

    def get(self, x, y, w, h):
        return self.get_test(x, y, w, h)

