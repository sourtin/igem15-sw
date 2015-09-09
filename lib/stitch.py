#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
import cv2
orb = cv2.ORB_create()
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

def homography_test(H, bounds):
    return True

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

    def homography_rel(self, dirn):
        neighbour = self.neighbours[dirn]
        if neighbour['hom'] is None:
            # compute homography only when requested
            im1 = neighbour['tile'].image
            im2 = self.image
            #im1 = cv2.cvtColor(im1, cv2.COLOR_BGR2HSV)[:,:,1]
            #im2 = cv2.cvtColor(im2, cv2.COLOR_BGR2HSV)[:,:,1]
            #im1 = cv2.cvtColor(im1, cv2.COLOR_BGR2HSV)[:,:,(1,2,2)]
            #im2 = cv2.cvtColor(im2, cv2.COLOR_BGR2HSV)[:,:,(1,2,2)]
            #im1 = cv2.cvtColor(im1, cv2.COLOR_HSV2BGR)
            #im2 = cv2.cvtColor(im2, cv2.COLOR_HSV2BGR)

            kp2, des2 = orb.detectAndCompute(im2, None)
            kp1, des1 = orb.detectAndCompute(im1, None)
            matches = sorted(bf.match(des1, des2), key=lambda m:m.distance)[:15]
            pts_src = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1,1,2)
            pts_dst = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1,1,2)
            M, _ = cv2.findHomography(pts_src, pts_dst, cv2.RANSAC, 5.0)
            neighbour['hom'] = M if homography_test(M, self.bounds) else False
        return neighbour['hom']

class Stitch:
    def __init__(self, images):
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
        print(here, there, dirns)

        neighbours = self.tiles[here].neighbours
        return [self.tiles[here].homography_rel(dirn).dot(hom)
                    for dirn in dirns
                        for hom in self._homographies(neighbours[dirn]['coord'], there)
                            if hom is not False]

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
            hom = self.homography(ref, c)
            prel = self.tiles[c].bounds
            pabs = cv2.perspectiveTransform(prel, hom)
            bounds.append(pabs)

        pts = np.concatenate(tuple(bounds), axis=0)
        [xmin, ymin] = np.int32(pts.min(axis=0).ravel() - 0.5)
        [xmax, ymax] = np.int32(pts.max(axis=0).ravel() + 0.5)
        return (xmin, xmax), (ymin, ymax)

    def warp(self, ref, ht, size, there):
        hom = self.homography(ref, there)
        im = self.tiles[there].image
        return cv2.warpPerspective(im, ht.dot(hom), size)

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

def stitch(images):
    return Stitch(images).assemble()
    return Stitch(np.matrix(images)).assemble()

