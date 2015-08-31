"""Dececting key points in images"""

import numpy
import cv2
from matplotlib import pyplot as plt

"""Load Image"""
img = cv2.imread("focusedMarchantia1.jpg", cv2.IMREAD_COLOR)

"""Initialise detector"""
orb = cv2.ORB_create()

"""find keypoints"""
kp = orb.detect(img, None)

"""Compute descriptors with orb"""
kp, des = orb.compute(img, kp)

"""Draw only keypoints location, not size or orientation"""
img2 = img.copy()
cv2.drawKeypoints(img,kp,img2,color=(255,0,0), flags=0)
plt.imshow(img2), plt.show()

#=============================================================================================================================#
"""Matching up key points in two images"""

import numpy
import cv2
from matplotlib import pyplot as plt

"""Load Images"""
img1 = cv2.imread("small crop.jpg", cv2.IMREAD_GRAYSCALE)
img2 = cv2.imread("focusedMarchantia1.jpg", cv2.IMREAD_GRAYSCALE)

"""Initialise detector"""
orb = cv2.ORB_create()

"""find keypointsand compute"""
kp1, des1 = orb.detectAndCompute(img1, None)
kp2, des2 = orb.detectAndCompute(img2, None)


# bf = cv2.BFMatcher()
# matches = bf.knnMatch(des1,des2, k=2)
# (img1a, img1b) = img1.shape
# (img2a, img2b) = img2.shape
# (a,b) = (img1a +img2a, img1b +img2b)
# img3 = numpy.empty((a,b,3))
#
# good = []
# for m,n in matches:
#     if m.distance < 0.75*n.distance:
#         good.append([m])
#
# # cv2.drawMatchesKnn expects list of lists as matches.
# cv2.drawMatchesKnn(img1,kp1,img2,kp2,good,img3)
#
#
# cv2.imshow("test", img3)
# cv2.waitKey()



"""create BFMatcher object""" #BF == brute force
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

"""Match descriptors"""
matches = bf.match(des1, des2)

"""Sort them in the order of their distance"""
matches = sorted(matches, key = lambda x: x.distance)

(img1a, img1b) = img1.shape
(img2a, img2b) = img2.shape
(a,b) = (img1a +img2a, img1b +img2b)

"""Draw first 10 matches"""
img3 = numpy.zeros((a,b))
img3.fill(255)
img3 = cv2.drawMatches(img1, kp1, img2, kp2, matches, img3, (255,0,0), (0,255,0), None, 2)

#cv2.drawMatches(img1, kp1, img2,kp2,matches[:10], img3,matchColor=(0,255,0), flags=2)
#plt.imshow(img3), plt.show()
plt.imshow(img3), plt.show()
# cv2.imshow("testImg", img3)
# cv2.waitKey()

