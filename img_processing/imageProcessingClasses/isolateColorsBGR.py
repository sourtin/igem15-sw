#ISOALTE COLOURS USING BGR COLOUR SCHEME

__author__ = 'ohd96'

import cv2
import numpy

class isolateColorsBGR():

    def __init__(self):
        pass

    @staticmethod
    def isolateMarchantiaGreen(img, lowGreen = [60,100,60], highGreen = [100,130,116]):

        """create numpy arrays for the GREEN boundaries"""
        lower = numpy.array(lowGreen, dtype = "uint8")
        upper = numpy.array(highGreen, dtype = "uint8")

        """find the colours within the specified boundaries. Return the output"""
        #return cv2.inRange(img, lower, upper)

        """Apply the mask and return it."""
        mask = cv2.inRange(img, lower, upper)
        return cv2.bitwise_and(img, img, mask = mask)

#=======TEST========================================================================================================#

img = cv2.imread("E:\\Shared OS folder\\iGEM\Images\\Focused Marchantia\\focusedMarchantia3\\focusedMarchantia_small.jpg", cv2.IMREAD_COLOR)
imgColor = isolateColorsBGR.isolateMarchantiaGreen(img)
cv2.imwrite("colorTesting.jpg", imgColor)