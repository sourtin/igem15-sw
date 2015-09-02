#OPENCV THRESHOLDING IS MORE EFFICIENT. USE THAT!!

__author__ = 'ohd96'

import numpy

class threshold():

    def __init__(self):
        pass

    @staticmethod
    def run(img, thresholdValue):
        rows, cols = img.shape

        outputImg = numpy.array((rows,cols))
        outputImg.fill(255)

        for r in range(rows):
            for c in range(cols):
                if img.item(r,c) < thresholdValue:
                    outputImg.itemset((r,c), 0)

