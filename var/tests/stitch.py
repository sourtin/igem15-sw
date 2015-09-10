#!/usr/bin/env python3
from lib.stitch import Tile, Stitch
from lib.canvas import Image, Rectangle, Vector
import numpy as np
import cv2
import os

imshow = lambda im: Image(None, im).show()

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

print(ims.shape)
ims = ims[:2,:2]
print(ims.shape)

im = ims[0,0].cv()
im = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)[:,:,2]
edges = cv2.Canny(im, 100, 200)
#im = cv2.imread('test2.png')
h, w = im.shape[:2]
s = 300
im = cv2.resize(im, (s, int(s*h/w)))

def nothing(_):
    pass
cv2.namedWindow('edge')
cv2.createTrackbar('min','edge',0,255,nothing)
cv2.createTrackbar('max','edge',0,255,nothing)
while True:
    if cv2.waitKey(1)&0xFF == 27:
        break
    min = cv2.getTrackbarPos('min','edge')
    max = cv2.getTrackbarPos('max','edge')
    edges = cv2.Canny(im, min, max)
    cv2.imshow('edge', im)

cv2.waitKey(0)



os._exit(0)

amalgam = Stitch(ims)
print(amalgam.bounds((1,1)))
im = amalgam.assemble()
h, w = im.shape[:2]
im2 = cv2.resize(im, (500, int(500*h/w)))
imshow(im2)
save = lambda fn: cv2.imwrite(fn, im)

