#!/usr/bin/env python3
from lib.stitch import Tile, Stitch
from lib.canvas import Image, Rectangle, Vector
import numpy as np
import cv2
import os

dir = "./var/tiles/"
files = os.listdir(dir)
ims = np.empty((4,4), object)
for file in files:
    x = int(file[0])
    y = int(file[1])
    im = cv2.imread(dir + file, cv2.IMREAD_COLOR)
    h, w = im.shape[:2]
    rect = Rectangle(Vector(0,0), 0, 1., h/w)
    ims[x, y] = Image(rect, im)
"""dir = "./var/stitch/tiles/"
files = os.listdir(dir)
ims = np.empty((2,3), object)
for file in files:
    x = int(file[0])
    y = int(file[1])
    im = cv2.imread(dir + file, cv2.IMREAD_COLOR)
    h, w = im.shape[:2]
    rect = Rectangle(Vector(0,0), 0, 1., h/w)
    ims[x, y] = Image(rect, im)"""#whiteboard

amalgam = Stitch(ims)
print(amalgam.bounds((1,1)))
im = amalgam.assemble()
h, w = im.shape[:2]
im2 = cv2.resize(im, (500, int(500*h/w)))
Image(None, im2).show()
save = lambda fn: cv2.imwrite(fn, im)

