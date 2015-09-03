#Marchantia Identification using thresholding and colour detection.
#GUI with variable sliders built in.

import cv2
import numpy
from contrastImprovement import contrastImprovement as contImprov
from isolateColorsBGR import isolateColorsBGR as isoCol
from tkinter import *
import bdct

"""load image"""
imgOriginal = cv2.imread("C:\\Users\\RAK\\Documents\\iGEM\\Software\\focusedMarchantia_small.jpg", cv2.IMREAD_COLOR)

# print(imgOriginal)

"""Set upper threshold limit for slider"""
upperThresholdLimit = 255

"""DO thresholding. Takes a colour image and returns a greyscale image"""
def threshold(blackCriteria, image):
    """"""
    """Convert to grayscale for use in openCV Thresholding"""
    imgEdit = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    """Improve contrast""" #OPTIMISED FOR SMALL MARCHANTIA
    #imgEdit = contImprov.improveContrastGrayscale(imgEdit, 105, 125)
    #print(imgEdit.dtype, imgEdit.shape)
    
    
    """ Carry out the BDCT method """
    imgEdit = bdct.bdct(img=imgEdit)
    cv2.imshow('bdct',imgEdit)

    """Do openCV Thresholding"""
    _, imgEdit = cv2.threshold(imgEdit, float(blackCriteria), 255, cv2.THRESH_BINARY_INV)

    return imgEdit


"""DO colour isolation. Takes a colour image and returns a greyscale image"""
def colour(image, thresholdVal, thresholdWidth = 10):
    """"""
    """Set lower and upper bounds of green colour - based on sample marchantia photos"""
    lowerGreenBound = [49,100,90]
    upperGreenBound = [100,130,116]
    """Get difference between corresponding values in upper and lower green values"""
    difference = [a - b for a,b in zip(upperGreenBound, lowerGreenBound)]

    """Get increase in value for each threshold unit increase"""
    difference = [ a/upperThresholdLimit for a in difference]

    """Get increases in value from default lower bound"""
    increase = [a*thresholdVal for a in difference]

    """Get centered points"""
    centered = [a+b for a,b in zip(lowerGreenBound, increase)]

    """Get lower and upper bounds for green screening"""
    lowerBound = [a - thresholdWidth for a in centered]
    upperBound = [a + thresholdWidth for a in centered]

    """Isolate green colour in marchantia"""
    imgEdit = isoCol.isolateMarchantiaGreen(imgOriginal, lowerBound, upperBound)

    """Make greyscale"""
    imgEdit = cv2.cvtColor(imgEdit, cv2.COLOR_BGR2GRAY)

    return imgEdit


"""Do thresholding/colour isolation and contouring"""
def go(blackCriteria = 30, kernelVal = 20, type = "threshold", image = imgOriginal.copy()):
    """"""
    print("Threshold value: " + str(blackCriteria))
    print("Threshold type:" + type)

    """Do openCV Thresholding"""
    if(type == "threshold"): #Equality testing I hope!
        imgEdit = threshold(blackCriteria, image)
    elif(type == "colour"):
        imgEdit = colour(image, float(blackCriteria))
    else:
        print("ERROR - INCORRECT ARGUMENT. DEFAULT IS THRESHOLD")
        imgEdit = threshold(blackCriteria, image)

    """perform openCV Contouring"""
    kernel = numpy.ones((kernelVal,kernelVal),numpy.float32)/25
    imgEdit = cv2.filter2D(imgEdit,-1,kernel)
    conImage, contours, hierarchy = cv2.findContours(imgEdit, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    """Display number of samples found"""
    print("Found " + str(len(contours)) + " points.")
    print("")

    """draw boxes around ORIGINAL image's samples"""
    imgOriginalBoxes = imgOriginal.copy()
    cv2.drawContours(imgOriginalBoxes,contours, -1, (0,0,255))

    cv2.imshow("image", imgEdit)




"""Save everything"""
def save(blackCriteria = 30, kernelVal = 20, type = "threshold", image = imgOriginal.copy()):

    if(type == "threshold"): #Equality testing I hope!
        imgEdit = threshold(blackCriteria, image)
    elif(type == "colour"):
        imgEdit = colour(image, float(blackCriteria))
    else:
        print("ERROR - INCORRECT ARGUMENT. DEFAULT IS THRESHOLD")
        imgEdit = threshold(blackCriteria, image)

    """perform openCV Contouring"""
    kernel = numpy.ones((kernelVal,kernelVal),numpy.float32)/25
    imgEdit = cv2.filter2D(imgEdit,-1,kernel)
    conImage, contours, hierarchy = cv2.findContours(imgEdit, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    """draw boxes around ORIGINAL image's samples"""
    imgOriginalBoxes = imgOriginal.copy()
    cv2.drawContours(imgOriginalBoxes,contours, -1, (0,0,255))

    cv2.imwrite("red_contoured_image.jpg", imgOriginalBoxes)

    print("Image Saved")

"""=========================Tkinter gui================================================================================"""
"""Create main frame"""
master = Tk()

"""Create Threshold type radio buttons"""
radioVal = StringVar()
Radiobutton(master, text = "Threshold", variable = radioVal, value = "threshold", command = lambda:go(slider.get(), kernelSlider.get(), radioVal.get())).pack(anchor = W)
Radiobutton(master, text = "Colour", variable = radioVal, value = "colour", command = lambda:go(slider.get(), kernelSlider.get(), radioVal.get())).pack(anchor = W)
radioVal.set("threshold")

"""Create kernel slider"""
kernelSlider = Scale(master, from_=1, to=50, label = "kernel", command=lambda x:go(slider.get(), int(x), radioVal.get()), orient=HORIZONTAL)
kernelSlider.set(20)
kernelSlider.pack()

"""Create threshold slider"""
slider = Scale(master, from_=1, to=upperThresholdLimit, label = "threshold", command=lambda x:go(x, kernelSlider.get(), radioVal.get()), orient=HORIZONTAL)
slider.set(50)
slider.pack()

"""Create save button"""
Button(master, text='Save', command=lambda:save(slider.get(), kernelSlider.get(), radioVal.get())).pack()

"""Run tkinter frame"""
cv2.namedWindow("image", flags = cv2.WINDOW_NORMAL)
mainloop()

cv2.waitKey(0)