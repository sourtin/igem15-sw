#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
import cv2
orb = cv2.ORB_create()
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

class Tile:
    def __init__(self, image):
        self.image = image
        self.neighbours = {key:{
            'image': None, 
            'bounds': None,
            'h': {
                'relative': None,
                'candidates': [],
                'absolute': None,
            },
        } for key in ['h','j','k','l']}

    def meet_neighbour(self, dirn, images, coord):
        x, y = coord
        w, h = images.shape
        if 0 <= x < w and 0 <= y < h:
            self.neighbours[dirn]['image'] = images[coord]

    def meet_neighbours(self, coord, images):
        x, y = coord
        self.meet_neighbour('h', images, (x-1, y))
        self.meet_neighbour('j', images, (x, y+1))
        self.meet_neighbour('k', images, (x, y-1))
        self.meet_neighbour('l', images, (x+1, y))

    def homography_rel(self, dirn):
        neighbour = self.neighbours[dirn]
        if neighbour['h']['relative'] is None:
            # compute homography only when requested
            kp1, des1 = orb.detectAndCompute(self.image.cv(), None)
            kp2, des2 = orb.detectAndCompute(neighbour['image'].cv(), None)
            matches = sorted(bf.match(des1, des2), key=lambda m:m.distance)[:15]
            pts_src = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1,1,2)
            pts_dst = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1,1,2)
            M, _ = cv2.findHomography(pts_src, pts_dst, cv2.RANSAC, 5.0)
            N, _ = cv2.findHomography(pts_dst, pts_src, cv2.RANSAC, 5.0)
            print(M);print(N);print(M.dot(N));print(N.dot(M))
            neighbour['h']['relative'] = M
        return neighbour['h']['relative']

    def homography_abs(self, dirn, g):
        pass

def stitch(images, reference=None):
    """stitch together:
        images: matrix of Image objects
        reference: coords of Image to use as ref,
                   or None to choose centre
        """

    tiles = np.empty(images.shape, object)
    for x, y in np.ndindex(tiles.shape):
        tiles[x, y] = Tile(images[x, y])
        tiles[x, y].meet_neighbours((x, y), images)

    return tiles


