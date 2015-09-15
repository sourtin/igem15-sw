#!/usr/bin/env python3
import lib.stitch
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
ctx.post.histeq_clr()
stitcher = lib.stitch2.ReferenceStitcher(ctx, ims[2], (1000,1000))

for im in ims[1:4]:
    (x,y), im_ = stitcher.align(im)
    h, w = im_.shape[:2]
    print(x,y,w,h)


im = stitcher.assemble()
#os._exit(0)

h, w = im.shape[:2]
im2 = cv2.resize(im, (int(400*w/h), 400))
imshow(im2)
save = lambda fn: cv2.imwrite(fn, im)
os._exit(0)

