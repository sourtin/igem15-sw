#!/usr/bin/env python3
from lib.stitch import TileStitcher, StitchContext
from lib.canvas import Image, Rectangle, Vector
import numpy as np
import cv2
import os

imshow = lambda im: Image(None, im).show()

dir = "./var/stitch/tile%s/" % input("Which? ")
files = os.listdir(dir)
w = max(int(file[0]) for file in files) + 1
h = max(int(file[1]) for file in files) + 1
print(h,w)
ims = np.empty((w,h), object)
for file in files:
    x = int(file[0])
    y = int(file[1])
    im = cv2.imread(dir + file, cv2.IMREAD_COLOR)
    h, w = im.shape[:2]
    rect = Rectangle(Vector(0,0), 0, 1., h/w)
    ims[x, y] = Image(rect, im)

print(ims)
ctx = StitchContext()
ctx.features.grey().histeq()
stitcher = TileStitcher(ctx, ims)
im = stitcher.assemble()

h, w = im.shape[:2]
im2 = cv2.resize(im, (800, int(800*h/w)))
im3 = cv2.resize(im, (1,1))
imshow(im2)
imshow(im3)
save = lambda fn: cv2.imwrite(fn, im)
#os._exit(0)

