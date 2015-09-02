#SPLIT IMAGE COLOURS INTO THE 3 CORRESPONDING BGR COLOURS

__author__ = 'Ocean'

"""

COLOUR SCHEME IS "BLUE GREEN RED" IN THAT ORDER

BLUE = 0
GREEN = 1
RED = 2

"""


import cv2
import numpy
from tkinter import *


class channelSplitGUI():

    def __init__(self, master, inputImage):

        #"master" is our main container - it will hold the checkbuttons

        #create image variables

        self.image = inputImage
        self.rows, self.cols, self.channels = self.image.shape
        self.img = inputImage.copy() #apparently numpy does deep copies


        #Create 3 Checkbuttons for channel control
        #each check button requires a tkinter variable
        checkButtonRedVal = BooleanVar(value = True)
        self.checkButtonRed = Checkbutton(
            master,
            text = "Red",
            variable = checkButtonRedVal,
            command = lambda:self.channelControl(self.img, checkButtonRedVal.get(), 2) #2 is RED in BGR
            )

        #each check button requires a tkinter variable
        checkButtonBlueVal = BooleanVar(value = True)
        self.checkButtonBlue = Checkbutton(
            master,
            text = "Blue",
            variable = checkButtonBlueVal,
            command = lambda:self.channelControl(self.img, checkButtonBlueVal.get(), 0) #0 is BLUE in BGR
            )

        #each check button requires a tkinter variable
        checkButtonGreenVal = BooleanVar(value = True)
        self.checkButtonGreen = Checkbutton(
            master,
            text = "Green",
            variable = checkButtonGreenVal,
            command = lambda:self.channelControl(self.img, checkButtonGreenVal.get(), 1) #1 is GREEN in BGR
            )

        """Add all Checkbuttons to the main (container) frame"""

        self.checkButtonRed.pack()
        self.checkButtonGreen.pack()
        self.checkButtonBlue.pack()

        cv2.imshow("Original Image", self.image)
        cv2.imshow("Edited Image", self.img)


    def channelControl(self, img, checkButtonVal, colorChannel):
        if(checkButtonVal): #set values to original
            for r in range(self.rows):
                for c in range(self.cols):
                    img.itemset((r,c,colorChannel), self.image.item(r,c,colorChannel))
        else: #set all values to zero
            for r in range(self.rows):
                for c in range(self.cols):
                    img.itemset((r,c,colorChannel),000)
        cv2.destroyWindow("Edited Image")
        cv2.imshow("Edited Image", img)
        cv2.waitKey(1)
        return img
#==============TEST====================================================================================#

# im1 = cv2.imread("C:\\Users\\Ocean\\Pictures\\football.jpg") #only ever used on coloured images
#
#
# root = Tk()
# root.title("Channel Selecter GUI")
# frame1 = channelSplitGUI(root, im1)
# root.mainloop()