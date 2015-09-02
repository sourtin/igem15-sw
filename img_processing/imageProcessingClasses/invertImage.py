__author__ = 'Ocean'

import cv2
import numpy


class invertImage():

    def __init__(self):
        pass

    @staticmethod
    def invertGrayscale(img):

        return 255 - img

        # rows, cols = img.shape
        # tempImg = numpy.empty([rows,cols],dtype=numpy.uint8)
        # print(tempImg)
        #
        # #do inversion
        # for r in range(rows):
        #     for c in range(cols):
        #         #t = 1 - img.item(r,c)/255
        #         t = 255 - img.item(r,c)
        #         tempImg.itemset(r,c,t)
        #
        # return tempImg

    @staticmethod
    def invertColor(img):

        return 255 - img

# im1 = cv2.imread("C:\\Users\\Ocean\\Pictures\\football.jpg", cv2.IMREAD_GRAYSCALE)
# cv2.imshow("NON-Inverted", im1)
# print (im1)
# inverter = invertImage()
#
# inv = inverter.invertGrayscale(im1)
# print(inv)
# cv2.imshow("Inverted",inv)
# cv2.waitKey(0)

# im2 = cv2.imread("C:\\Users\\Ocean\\Pictures\\football.jpg")
# cv2.imshow("NON-Inverted", im2)
# print (im2)
# inverter = invertImage()
#
# inv = inverter.invertColor(im2)
# print(inv)
# cv2.imshow("Inverted",inv)
# cv2.waitKey(0)

