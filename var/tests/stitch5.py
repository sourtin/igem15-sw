#!/usr/bin/env python3
import lib.stitch2
from lib.canvas import Image, Rectangle, Vector
import numpy as np
import cv2
import os

imshow = lambda im: Image(None, im).show()

dir = "./var/stitch/tile9c/m/%s.jpg"
read = lambda f:cv2.imread(dir % f, cv2.IMREAD_COLOR)
ims = [read(f) for f in range(7)]

ctx = lib.stitch2.StitchContext()
ctx.features.grey().histeq()
stitcher = lib.stitch2.ReferenceStitcher(ctx, ims[2], ims[1:4])
im = stitcher.assemble()
os._exit(0)

h, w = im.shape[:2]
im2 = cv2.resize(im, (800, int(800*h/w)))
imshow(im2)
save = lambda fn: cv2.imwrite(fn, im)
os._exit(0)

