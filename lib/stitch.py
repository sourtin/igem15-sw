#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from lib.vector import Vector
from lib.canvas import Polygon
import math
import numpy as np
import cv2
orb = cv2.ORB_create()
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

class HomographyTest:
    def rotate(l, n):
        n = n % len(l)
        return l[n:] + l[:n]

    def angle(a, b):
        return math.atan2(a.wedge(b), a.dot(b))

    def cv2vec(cv):
        return [Vector(*b[0]) for b in cv]

    def coords_dirn(coords):
        centroid = Polygon(*coords).centroid()
        vecss = Polygon(*[vec-centroid for vec in coords]).lines()
        sign = lambda x:math.copysign(1, x)
        signs = [sign(HomographyTest.angle(a,b)) for a,b in vecss]
        return int((max(signs) + min(signs)) / 2)

    def coords_bounds(coords):
        rect = Polygon(*coords).rectangle()
        return rect.width, rect.height

    def test(hom, bounds, threshold=.1):
        # homography
        vecs0 = HomographyTest.cv2vec(bounds)
        boundz = cv2.perspectiveTransform(bounds, hom)
        vecs1 = HomographyTest.cv2vec(boundz)

        # are vecs0 and vecs1 both (counter)clockwise?
        sign0 = HomographyTest.coords_dirn(vecs0)
        sign1 = HomographyTest.coords_dirn(vecs1)
        if sign0 != sign1 or sign1 == 0:
            # not same points order/warped
            return False

        # size and angle-ish
        w0, h0 = HomographyTest.coords_bounds(vecs0)
        w1, h1 = HomographyTest.coords_bounds(vecs1)
        thresh = lambda a,b: abs((a-b)/a) < threshold
        return thresh(w0, w1) and thresh(h0, h1)

class Tile:
    def __init__(self, image):
        self.meta = image
        self.image = image.cv()
        self.neighbours = {key:{
            'tile': None, 
            'coord': None,
            'bounds': None,
            'hom': None,
        } for key in ['h','j','k','l']}
        self.abs = {}
        h, w = self.image.shape[:2]
        self.bounds = np.float32([[0,0], [0,h], [w,h], [w,0]]).reshape(-1,1,2)
        pts = np.float32([[0,0],[0,h],[w,h],[w,0]]).reshape(-1,1,2)

    def meet_neighbour(self, dirn, tiles, coord):
        x, y = coord
        w, h = tiles.shape
        if 0 <= x < w and 0 <= y < h:
            self.neighbours[dirn]['tile'] = tiles[coord]
            self.neighbours[dirn]['coord'] = coord

    def meet_neighbours(self, coord, tiles):
        x, y = coord
        self.meet_neighbour('h', tiles, (x-1, y))
        self.meet_neighbour('j', tiles, (x, y+1))
        self.meet_neighbour('k', tiles, (x, y-1))
        self.meet_neighbour('l', tiles, (x+1, y))

    def homography_rel(self, dirn, process):
        neighbour = self.neighbours[dirn]
        if neighbour['hom'] is None:
            # compute homography only when requested
            im1 = process(neighbour['tile'].image)
            im2 = process(self.image)

            kp2, des2 = orb.detectAndCompute(im2, None)
            kp1, des1 = orb.detectAndCompute(im1, None)
            matches = sorted(bf.match(des1, des2), key=lambda m:m.distance)[:15]
            pts_src = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1,1,2)
            pts_dst = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1,1,2)
            M, _ = cv2.findHomography(pts_src, pts_dst, cv2.RANSAC, 5.0)
            neighbour['hom'] = M if HomographyTest.test(M, self.bounds) else False
        return neighbour['hom']

class Stitch:
    def __init__(self, images, process=lambda x:x):
        self.process = process
        self.images = images
        self.tiles = np.empty(images.shape, object)
        for c in np.ndindex(self.tiles.shape):
            self.tiles[c] = Tile(images[c])
        for c in np.ndindex(self.tiles.shape):
            self.tiles[c].meet_neighbours(c, self.tiles)
        
    def _homographies(self, here, there):
        if here == there:
            return [np.eye(3)]
        xh, yh = here
        xt, yt = there
        dirns = []

        if xt > xh: dirns.append('l')
        if xt < xh: dirns.append('h')
        if yt > yh: dirns.append('j')
        if yt < yh: dirns.append('k')

        neighbours = self.tiles[here].neighbours
        homs = []
        for dirn in dirns:
            hom1 = self.tiles[here].homography_rel(dirn, self.process)
            if hom1 is not False:
                for hom2 in self._homographies(neighbours[dirn]['coord'], there):
                    if hom2 is not False:
                        homs.append(hom1.dot(hom2))
        return homs

    def homography(self, ref, there):
        if ref not in self.tiles[there].abs:
            homs = self._homographies(ref, there)
            assert len(homs)
            hom = np.mean(np.array(homs), axis=0)
            self.tiles[there].abs[ref] = hom
        return self.tiles[there].abs[ref]

    def bounds(self, ref):
        bounds = [self.tiles[ref].bounds]
        for c in np.ndindex(self.tiles.shape):
            try:
                hom = self.homography(ref, c)
                prel = self.tiles[c].bounds
                pabs = cv2.perspectiveTransform(prel, hom)
                bounds.append(pabs)
            except:
                pass

        pts = np.concatenate(tuple(bounds), axis=0)
        [xmin, ymin] = np.int32(pts.min(axis=0).ravel() - 0.5)
        [xmax, ymax] = np.int32(pts.max(axis=0).ravel() + 0.5)
        return (xmin, xmax), (ymin, ymax)

    def warp(self, ref, ht, size, there):
        try:
            hom = self.homography(ref, there)
            im = self.tiles[there].image
            return cv2.warpPerspective(im, ht.dot(hom), size)
        except Exception as e:
            print("Missing homography for image %r wrt %r!" % (there,ref))
            w, h = size
            return np.full((h,w,3), 0, dtype=np.uint8)

    def assemble(self, ref=None):
        if ref is None:
            w, h = self.tiles.shape
            ref = w//2, h//2

        (xmin, xmax), (ymin, ymax) = self.bounds(ref)
        ht = np.array([[1,0,-xmin], [0,1,-ymin], [0,0,1]])
        size = xmax-xmin, ymax-ymin

        warp = lambda c: self.warp(ref, ht, size, c)
        im = None
        for c in np.ndindex(self.tiles.shape):
            # have to do one by one to save memory
            im = warp(c) if im is None else np.maximum.reduce([im,warp(c)])
        return im

def preprocess_clahe(images):
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    def colourhe(im):
        im2 = cv2.cvtColor(im, cv2.COLOR_BGR2YCrCb)
        im2[:,:,0] = clahe.apply(im2[:,:,0])
        return cv2.cvtColor(im2, cv2.COLOR_YCrCb2BGR)
    from lib.canvas import Image
    for c in np.ndindex(images.shape):
        images[c] = Image(None,colourhe(images[c].cv()))
    return images

def stitch(images, process=lambda x:x):
    return Stitch(images, process).assemble()
    return Stitch(np.matrix(images)).assemble()

def stitch_hsv(images, component=1):
    return stitch(images, lambda im:cv2.cvtColor(im, cv2.COLOR_BGR2HSV)[:,:,component])

def stitch_grey(images):
    return stitch(images, lambda im:cv2.cvtColor(im, cv2.COLOR_BGR2GRAY))

def stitch_clahe(images, he=1, colour=False):
    # if colour, first optimise the Y component of YCrCb via histogram equalisation
    # then, do one of three single component equalisers:
    #  0) nothing
    #  1) convert to greyscale
    #  2) convert to hsv and select v

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    def colourhe(im):
        if colour:
            im2 = cv2.cvtColor(im, cv2.COLOR_BGR2YCrCb)
            im2[:,:,0] = clahe.apply(im2[:,:,0])
            return cv2.cvtColor(im2, cv2.COLOR_YCrCb2BGR)
        else:
            return im

    def greyhe(im):
        return clahe.apply(cv2.cvtColor(im, cv2.COLOR_BGR2GRAY))
    def valhe(im):
        return clahe.apply(cv2.cvtColor(im, cv2.COLOR_BGR2HSV)[:,:,2])
    def idhe(im):
        return im
    hes = [idhe, greyhe, valhe]

    return stitch(images, lambda im:hes[he](colourhe(im)))

