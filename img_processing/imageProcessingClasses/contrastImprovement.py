#FROM COMPUTER SCIENCE LECTURE NOTES

__author__ = 'Ocean'
import cv2
import numpy

"""p328 in Comp. Sci. Graphics Lecture Notes"""

class OutOfBoundsException(Exception):

    def __init__(self, val):
        super(OutOfBoundsException, self).__init__(val)
        self.val = val
        self.printError(val)

    def printError(self, val):
        print ("EXCEPTION - OutOfBoundsException - Input Value out of range:\t" + str(self.val))


class contrastImprovement():


    def __init__(self, maxBlackVal=15, minWhiteVal=200):
        self.blackLim = maxBlackVal
        self.whiteLim = minWhiteVal

    @staticmethod
    def improveContrastVal(val, blackLim, whiteLim):
        if val < 0 or val > 255:
            print (val)
            raise OutOfBoundsException(val)
        else:
            #valid input

            #blacks stay black
            if val <= blackLim:
                #return black. 000 = black
                return 000
            elif val <= whiteLim:
                #return a value on the straight line joining the blackLim and whiteLim values
                grad = 255/(whiteLim - blackLim) #dy/dx

                temp = int(round(grad * (val - blackLim)))
                return temp
            else:
                #return white
                return 255

    @staticmethod
    def improveContrastGrayscale(img, blackLim = 15, whiteLim = 200):

        rows, cols = img.shape

        tempImg = numpy.empty([rows,cols],dtype=numpy.uint8)

        for r in range(rows):
            for c in range(cols):
                temp = contrastImprovement.improveContrastVal(img.item(r,c), blackLim, whiteLim)
                #print (str(img.item(r,c)) + "\t" + str(temp))
                tempImg.itemset(r,c, temp)

        return tempImg

    @staticmethod
    def improveContrastColor(img, blackLim = 15, whiteLim = 200):

        rows, cols, channels = img.shape

        tempImg = numpy.empty([rows,cols, channels],dtype=numpy.uint8)

        for r in range(rows):
            for c in range(cols):
                for i in range(channels):
                    temp = contrastImprovement.improveContrastVal(img.item(r,c, i), blackLim, whiteLim)
                    #print (str(img.item(r,c)) + "\t" + str(temp))
                    tempImg.itemset((r,c,i), temp)

        return tempImg

#==========TEST=========================================================#
# im1 = cv2.imread("C:\\Users\\Ocean\\Pictures\\football.jpg", cv2.IMREAD_GRAYSCALE)
# cv2.imshow("WITHOUT Contrast improvement", im1)
#
#
# for i in range(0,255,10):
#     contraster = contrastImprovement(15, i)
#     cont = contraster.improveContrastGrayscale(im1)
#     #print(cont)
#     cv2.imshow("With Contrast improvement",cont)
#     cv2.waitKey(0)

# im2 = cv2.imread("C:\\Users\\Ocean\\Pictures\\football.jpg")
# cv2.imshow("WITHOUT Contrast improvement", im2)
#
#
# for i in range(0,255,10):
#     contraster = contrastImprovement(15, i)
#     cont = contraster.improveContrastColor(im2)
#     #print(cont)
#     cv2.imshow("With Contrast improvement",cont)
#     cv2.waitKey(0)