#This file contains the POINT, and IMAGE classes that may prove useful for storing each sample in an image.

#OPENCV CONTOURING METHOD IS MORE EFFICIENT. USE THAT!!

#This uses the marching around edges idea.
#It will scan across the image until it hits a black pixel. Then it will walk around the perimeter of the sample until it reaches the start again.

"""
Version 2   - Have a boundary/walking algorithm implemented

Version 3   - Uses a simple "< blackCriteria" test rather than making an array of booleans to hold all values. Should reduce overhead.
            - Removed unused commented out code and removed 'pixel' thresholding methods.

Version 4   - Implemented a slightly different walking method. Will now count corner-connected pixels as the same object and will continue to walk around these.

Version 5   - Adding only pixels within the bounding array to the ignore list - not all pixels within a square that bounds the array.

Version 6   - Adding boundary conditions
"""

__author__ = 'Ocean'
import cv2
import numpy
import time


#===================IMAGE=CLASS=======================================================================================#

class image:

    def __init__(self, colourImageInput):
        self.imgGreyscale = cv2.cvtColor(colourImageInput, cv2.COLOR_BGR2GRAY)
        self.rows, self.cols = self.imgGreyscale.shape
        self.points = point.findPointsBoundary(self.imgGreyscale)
        self.noPoints = len(self.points)

    def createImageOfPoints(self):
        newImg = numpy.empty((self.rows, self.cols))
        newImg.fill(255)

        for pt in self.points:
            newImg.itemset(pt.center, 0)

        return newImg

    def createImageOfBoundary(self):
        newImg = numpy.empty((self.rows, self.cols))
        newImg.fill(255)

        for pt in self.points:
            for (i,j) in pt.coordinateArray:
                newImg.itemset((i,j), 0)

        return newImg






#===================POINT=CLASS=======================================================================================#

class point:
    def __init__(self, coordinateArrayInput, centerInput):
        self.coordinateArray = coordinateArrayInput
        self.center = centerInput





#---------Boundary----------------------------------------------------------------------------------------------------#

    @staticmethod
    def findPointsBoundary(greyscaleImage):

        img = greyscaleImage
        rows, cols = img.shape

        blackCriteria = 60; #value below which pixels are counted as black. Everything above is discounted.

        #THIS ALGORITHM TESTS NUMBERS AGAINST blackCriteria DIRECTLY RATHER THAN CREATE A BOOL ARRAY OF TRUE AND FALSE.
        #THIS SHOULD REDUCE SPACE AND TIME OVERHEADS.

        #list of points to return
        pointArray = []

        #create ignore list - very small overhead. 0.0005seconds
        ignoreList = numpy.empty((rows,cols))
        ignoreList.fill(False)

        #run through all pixels
        for i in range(rows):
            for j in range(cols):

                #check ignore list and pass if pixel is in list
                if ignoreList.item(i,j):
                    pass
                else:
                    #look for next set value
                    if img.item(i,j) < blackCriteria:
                        boundaryArray, (imin, imax), (jmin, jmax) = point.contourScan(img, ignoreList, blackCriteria, i, j)

                        center = point.getCenterOfBoundary(boundaryArray)
                        pointArray.append(point(boundaryArray, center))

        return pointArray




    #Scan to find the boudary of a "point" from a given starting position
    @staticmethod
    def contourScan(imgBool, ignoreList, blackCriteria, iInitial, jInitial):

        #Global coordinate system is the one used for imgBool indexes - (i,j)
        #Local coordinate system is the one used when scanning the 4 neighbouring pixels.
        #   - local coordinate system is (a,b) and is such that your 'direction of motion' along a pixel edge is always up.
        #   - because of this, various rotations are needed to go to and from the global and local coordinate systems.
        #   - this system is used because there are then only 3 pixel cases needed to fully trace the boundary.

        #create i and j counters and initialise them to the second point on bounding surface
        i = iInitial - 1
        j = jInitial

        #create motion variables - value is motion JUST executed - will always start by moving upwards
        motionLeft = False; motionRight = False; motionUp = True; motionDown = False;

        #create local neighbours
        neighbour = numpy.empty(4)
        neighbour.fill(False)

        #initialise array to return
        boundingArray = []

        #Add first element to bounding array
        boundingArray.append((iInitial, jInitial))

        #Add first line to ignoreList
        jTemp = jInitial #for temporarily incrementing the j value
        while imgBool.item(iInitial, jTemp) < blackCriteria: #while current item is set, add it to the ignoreList
            ignoreList.itemset((iInitial,jTemp), True)
            jTemp += 1

        imin, imax, jmin, jmax = i, i, j, j;

        #Until we reach the starting point:
        while not (i == iInitial and j == jInitial):

            if(i < imin):
                imin = i
            elif(i > imax):
                imax = i
            if(j<jmin):
                jmin = j
            elif(j > jmax):
                jmax = j
            #set the neighbour array
            #ROTATIONS TAKEN INTO ACCOUNT - now facing 'up'
            point.rotateLocalAxisAndSetNeighbourArray(neighbour, imgBool, blackCriteria, i, j, motionLeft, motionRight, motionUp, motionDown)

            #Assert: neighbour(2) should always be False - Bottom left should always be unset
            #        neighbour(3) should always be True - Bottom right should always be set

            if neighbour.item(0) < blackCriteria: #if top left element set
                #if top left element IS set, top right element is now irrelevant
                #append pixel we're moving along to bounding array
                if(motionUp):
                    boundingArray.append((i, j-1))
                elif(motionRight):
                    boundingArray.append((i,j))
                elif(motionLeft):
                    boundingArray.append((i+1, j-1))
                elif(motionDown):
                    boundingArray.append((i+1, j))

                #local coordinate system increments
                a = 0; b = -1;

            else: #top left element NOT set
                if neighbour.item(1) < blackCriteria: #if top right element set
                    #straight ahead
                    #append current pixel to bounding array
                    if(motionUp):
                        boundingArray.append((i,j))
                    elif(motionDown):
                        boundingArray.append((i+1,j-1))
                    elif(motionRight):
                        boundingArray.append((i+1, j))
                    elif(motionLeft):
                        boundingArray.append((i, j-1))
                    else:
                        print("ERROR 5")

                    #local coordinate system increments
                    a = -1; b = 0;


                else: #if top right element NOT set and top left NOT set
                    #turn right
                    #NO APPEND OF boundingArray


                    #local coordinate system increments
                    a = 0; b = 1;

            #global coordinate system increments
            iIncrement, jIncrement = point.rotateIncrements(a,b,motionLeft, motionRight, motionUp, motionDown)

            #update ignoreList
            if(iIncrement == -1): #if you're about to move UP
                jTemp = j #for temporarily incrementing the j value
                if (i,jTemp) == (73,81):
                    print("WHILE LOOP - HIT INNER BOUNDARY FOR IGNORELIST")
                while imgBool.item(i, jTemp) < blackCriteria: #while current item is set, add it to the ignoreList
                    ignoreList.itemset((i,jTemp), True)
                    jTemp += 1

            #increment global indices - i.e. move to your new position
            i += iIncrement
            j += jIncrement

            #the iIncrement and jIncrement values hold the same information as the motionLeft etc... values, but as numbers not bools

            if(iIncrement == 1):
                motionDown = True; motionLeft = False; motionRight = False; motionUp = False;
            elif (iIncrement == -1):
                motionUp = True; motionLeft = False; motionRight = False; motionDown = False;
            elif(jIncrement == 1):
                motionRight = True; motionLeft = False; motionUp = False; motionDown = False;
            elif(jIncrement == -1):
                motionLeft = True; motionRight = False; motionUp = False; motionDown = False;
            else:
                print("ERROR 4")

        return boundingArray, (imin, imax), (jmin, jmax)



    #Rotation Instructions for index increments
    @staticmethod
    def rotateIncrements(a,b,motionLeft, motionRight, motionUp, motionDown):

        if(motionLeft):
            #moving left. Therefore previously rotated right.
            #must therefore NOW rotate LEFT

            #On rotating left, i's increment is b's, j's increment is negative a's

            iIncrement = -b;
            jIncrement = a;

            return (iIncrement, jIncrement)

        elif(motionRight):
            #moving right. Therefore previously rotated left.
            #must therefore NOW rotate RIGHT

            #On rotating right, i's increment is negative b's, and j's increment is a's increment

            iIncrement = b;
            jIncrement = -a;

            return (iIncrement, jIncrement)

        elif(motionUp):
            #moving up. Therefore previously NO rotation.
            #therefore NO rotation now needed

            return (a,b)

        elif(motionDown):
            #moving down. Therefore previously rotated 180 degrees.
            #must therefore NOW rotate 180 degrees

            #On rotating 180 degrees, i increments are negative a's, and j's increments are the negative of b's

            iIncrement = -a;
            jIncrement = -b;

            return (iIncrement, jIncrement)

        else:
            print("ERROR 3")






    #set the neighbour array in the contourScan method
    @staticmethod
    def rotateLocalAxisAndSetNeighbourArray(neighbour, imgBool, blackCriteria, i, j, motionLeft, motionRight, motionUp, motionDown):
        if(motionRight):
            neighbour.itemset(0, imgBool.item(i,j))
            neighbour.itemset(1, imgBool.item(i+1,j))
            neighbour.itemset(2, imgBool.item(i,j-1))
            neighbour.itemset(3, imgBool.item(i+1,j-1))
        elif(motionDown):
            neighbour.itemset(0, imgBool.item(i+1,j))
            neighbour.itemset(1, imgBool.item(i+1,j-1))
            neighbour.itemset(2, imgBool.item(i,j))
            neighbour.itemset(3, imgBool.item(i,j-1))
        elif(motionLeft):
            neighbour.itemset(0, imgBool.item(i+1,j-1))
            neighbour.itemset(1, imgBool.item(i,j-1))
            neighbour.itemset(2, imgBool.item(i+1,j))
            neighbour.itemset(3, imgBool.item(i,j))
        elif(motionUp):
            neighbour.itemset(0, imgBool.item(i,j-1))
            neighbour.itemset(1, imgBool.item(i,j))
            neighbour.itemset(2, imgBool.item(i+1,j-1))
            neighbour.itemset(3, imgBool.item(i+1,j))

        else:
            print("Major ERROR!!!: ERROR 1")



        #Assert: neighbour[3] should always be set to True
        if (not neighbour.item(3) < blackCriteria) or (neighbour.item(2) < blackCriteria):
            print("Huge Error!!!: ERROR 2")
            #DEBUGGING
            print(neighbour)
            print(i,j)
            print("")




    #get the center of given contour boundary
    @staticmethod
    def getCenterOfBoundary(boundaryArray):
        return boundaryArray[0]


#=======TEST=IMAGE=LOADING========================================================================================#
# start_time = time.time()
# img1 = cv2.imread("testImage4.jpg")
#
# #some pre-image processing
# #kernel = numpy.ones((10,10), numpy.uint8)
# # img1 = cv2.morphologyEx(img1, cv2.MORPH_CLOSE, kernel)
# # img1 = cv2.morphologyEx(img1, cv2.MORPH_OPEN, kernel)
# # img1 = cv2.morphologyEx(img1, cv2.MORPH_CLOSE, kernel)
# # img1 = cv2.morphologyEx(img1, cv2.MORPH_OPEN, kernel)
# # cv2.imshow("test",img1)
# # cv2.waitKey(0)
#
# image1 = image(img1)
# print("Found " + str(image1.noPoints) + " points.")
#
#
# end_time = time.time()
# elapsed_time = end_time - start_time
# print("Elapsed Time: " + str(elapsed_time))
# ptImg = image1.createImageOfBoundary()
# cv2.imwrite("ptImgBoundary.bmp", ptImg)
#
# # cv2.imshow("image Title", ptImg)
# # cv2.waitKey(0)


