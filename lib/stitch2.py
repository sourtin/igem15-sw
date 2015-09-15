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
        if hom is None:
            return None

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

class TileStitcher:
    """Stitch a matrix of Image objects"""

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

    def __init__(self, context, images):
        self.context = context
        self.tiles = np.empty(images.shape, object)
        for c in np.ndindex(self.tiles.shape):
            images[c].data = context.pre(images[c].data)
            self.tiles[c] = TileStitcher.Tile(images[c])
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
            hom1 = self.tiles[here].homography_rel(dirn, self.context.features)
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
            im = self.context.post(self.tiles[there].image)
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

class ReferenceStitcher:
    def __init__(self, context, ref, ims):
        """ref, im should be cv ims"""
        self.context = context
        self.ref = context.pre(ref)
        self.ims = [{'im': context.pre(im)} for im in ims]
        self.kdr = orb.detectAndCompute(context.features(self.ref), None)

    def boundss(self):
        def bounds(im):
            h, w = im['im'].shape[:2]
            return np.float32([[0,0], [0,h], [w,h], [w,0]]).reshape(-1,1,2)
        for im in self.ims:
            im['bounds'] = bounds(im)

    def homs(self):
        def hom(im):
            kpr, desr = self.kdr
            kpi, desi = orb.detectAndCompute(self.context.features(im['im']), None)
            matches = sorted(bf.match(desi, desr), key=lambda m:m.distance)[:15]
            pts_src = np.float32([kpi[m.queryIdx].pt for m in matches]).reshape(-1,1,2)
            pts_dst = np.float32([kpr[m.trainIdx].pt for m in matches]).reshape(-1,1,2)
            H, _ = cv2.findHomography(pts_src, pts_dst, cv2.RANSAC, 5.0)
            return H if HomographyTest.test(H, im['bounds']) else None
        for im in self.ims:
            im['h'] = hom(im)
        self.ims = [im for im in self.ims if im['h'] is not None]

    def inboundss(self):
        def inbounds(im):
            boundc = cv2.perspectiveTransform(im['bounds'], im['h'])
            bounds = HomographyTest.cv2vec(boundc)
            xmin, xmax = sorted([x for x,_ in bounds])[1:3]
            ymin, ymax = sorted([y for _,y in bounds])[1:3]
            inbs = [Vector(xmin, ymin), Vector(xmax, ymin),
                    Vector(xmax, ymax), Vector(xmin, ymax)]
            poly = Polygon(*bounds)

            cv2v = HomographyTest.cv2vec
            if not all(poly.contains(inb) for inb in inbs):
                inbs = None
            print([(int(x),int(y)) for x,y in bounds])
            return inbs, (int(xmax-xmin), int(ymax-ymin))
        for im in self.ims:
            im['inbounds'], im['inshape'] = inbounds(im)
            print(im['inshape'])
            print()
        self.ims = [im for im in self.ims if im['inbounds'] is not None]

    def assemble(self):
        self.boundss()
        self.homs()
        self.inboundss()
        print(len(self.ims))

class StitchContext:
    class Processor:
        def __init__(self, clahe):
            self.clahe = clahe
            self.f = lambda im:im

        def __call__(self, im):
            return self.f(im)

        def reset(self):
            self.f = lambda im:im

        def grey(self):
            f = self.f
            self.f = lambda im: cv2.cvtColor(f(im), cv2.COLOR_BGR2GRAY)
            return self

        def hsv(self, component=2):
            f = self.f
            self.f = lambda im: cv2.cvtColor(f(im), cv2.COLOR_BGR2HSV[:,:,component])
            return self

        def histeq_clr(self):
            def he_colour(im):
                im2 = cv2.cvtColor(im, cv2.COLOR_BGR2YCrCb)
                im2[:,:,0] = self.clahe.apply(im2[:,:,0])
                return cv2.cvtColor(im2, cv2.COLOR_YCrCb2BGR)
            f = self.f
            self.f = lambda im: he_colour(f(im))
            return self

        def histeq(self):
            f = self.f
            self.f = lambda im: self.clahe.apply(f(im))
            return self

    def __init__(self):
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        self.pre = StitchContext.Processor(clahe)
        self.features = StitchContext.Processor(clahe)
        self.post = StitchContext.Processor(clahe)

