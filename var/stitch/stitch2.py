#!/usr/bin/env python3

import cv2
import numpy as np

def display(im):
    ih, iw = im.shape[:2]
    sh = 700
    sw = int(iw * sh / ih)
    sm = cv2.resize(im, (sw, sh))

    cv2.imshow('im', sm)
    cv2.waitKey(0)

def warpTwoImages(img1, img2, H):
    '''warp img2 to img1 with homograph H'''
    h1,w1 = img1.shape[:2]
    h2,w2 = img2.shape[:2]
    pts1 = np.float32([[0,0],[0,h1],[w1,h1],[w1,0]]).reshape(-1,1,2)
    pts2 = np.float32([[0,0],[0,h2],[w2,h2],[w2,0]]).reshape(-1,1,2)
    pts2_ = cv2.perspectiveTransform(pts2, H)
    pts = np.concatenate((pts1, pts2_), axis=0)
    [xmin, ymin] = np.int32(pts.min(axis=0).ravel() - 0.5)
    [xmax, ymax] = np.int32(pts.max(axis=0).ravel() + 0.5)
    t = [-xmin,-ymin]
    Ht = np.array([[1,0,t[0]],[0,1,t[1]],[0,0,1]]) # translate

    result = cv2.warpPerspective(img2, Ht.dot(H), (xmax-xmin, ymax-ymin))
    result[t[1]:h1+t[1],t[0]:w1+t[0]] = img1
    return result

im1 = cv2.imread("tiles/11.jpg", cv2.IMREAD_COLOR)
im2 = cv2.imread("tiles/12.jpg", cv2.IMREAD_COLOR)

#display(im1)
#display(im2)

orb = cv2.ORB_create()
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

FLANN_INDEX_KDTREE = 0
index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
search_params = dict(checks = 50)
flann = cv2.FlannBasedMatcher(index_params, search_params)

kp1, des1 = orb.detectAndCompute(im1, None)
kp2, des2 = orb.detectAndCompute(im2, None)

matches = bf.match(des1, des2)
matches = sorted(matches, key=lambda m:m.distance)[:15]

#display(im3)

dst_pts = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1,1,2)
src_pts = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1,1,2)
M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

display(warpTwoImages(im1, im2, M))



