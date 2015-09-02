#ISOALTE COLOURS USING HSV COLOUR SCHEME

__author__ = 'ohd96'

import cv2
import numpy

class isolateColorsHSV():

    def __init__(self):
        pass

    @staticmethod
    def isolateMarchantiaGreen(img):

        #play around with these two values to get different colour isolations
        lower_green_threshold = 20
        upper_green_threshold = 70

        imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        lower_green = numpy.array([lower_green_threshold,50,50], dtype = numpy.uint8)
        upper_green = numpy.array([upper_green_threshold, 255, 255], dtype = numpy.uint8)

        mask = cv2.inRange(imgHSV, lower_green, upper_green)

        return cv2.bitwise_and(img, img, mask = mask)


#===========TEST================================================================#

# img1 = cv2.imread("marchantia4.jpg", cv2.IMREAD_COLOR)
# img1_updated = isolateColors.isolateMarchantiaGreen(img1)
# cv2.imwrite("testImg.jpg", img1_updated)
# cv2.waitKey(0)
