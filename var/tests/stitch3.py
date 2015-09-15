#!/usr/bin/env python3
from lib.stitch import TileStitcher, StitchContext
from lib.canvas import Image, Rectangle, Vector
import numpy as np
import cv2
import os

dir = "./var/stitch/tile2/"
imshow = lambda im: Image(None, im).show()
def imread(file):
    x = int(file[0])
    y = int(file[1])
    im = cv2.imread(dir + file, cv2.IMREAD_COLOR)
    h, w = im.shape[:2]
    rect = Rectangle(Vector(0,0), 0, 1., h/w)
    return Image(rect, im)

ims = np.empty((2,1), object)
ims[0,0] = imread("10.jpg")
ims[1,0] = imread("20.jpg")

print(ims)
ctx = StitchContext()
ctx.features.hsv(1)
stitcher = TileStitcher(ctx, ims)
im = stitcher.assemble()
#im = stitch_hsv(ims, 1)

h, w = im.shape[:2]
im = cv2.resize(im, (1200, int(1200*h/w)))
imshow(im)
save = lambda fn: cv2.imwrite(fn, im)
os._exit(0)

