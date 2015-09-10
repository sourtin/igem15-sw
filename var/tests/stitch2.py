#!/usr/bin/env python3
from lib.stitch import stitch
from lib.canvas import Image, Rectangle, Vector
import numpy as np
import cv2
import os

imshow = lambda im: Image(None, im).show()

dir = "./var/stitch/tile%s/" % input("Which? ")
files = os.listdir(dir)
ims = np.empty((2,2), object)
for file in files:
    x = int(file[0])
    y = int(file[1])
    im = cv2.imread(dir + file, cv2.IMREAD_COLOR)
    h, w = im.shape[:2]
    rect = Rectangle(Vector(0,0), 0, 1., h/w)
    ims[x, y] = Image(rect, im)

print(ims)
im = stitch(ims)
h, w = im.shape[:2]
im = cv2.resize(im, (1200, int(1200*h/w)))
imshow(im)
save = lambda fn: cv2.imwrite(fn, im)
os._exit(0)

