#!/usr/bin/env python3
import requests
import numpy as np
import cv2

class MicroMaps:
    def __init__(self):
        pass

    def get_test(self, x, y, w, h):
        import hashlib
        m = hashlib.md5()
        m.update(("%d %d" % (x,y)).encode())
        d = m.digest()
        raw = np.full((h,w,3), list(d[:3]), dtype=np.uint8)
        return raw

    def get(self, x, y, w, h):
        return self.get_test(x, y, w, h)

