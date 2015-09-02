#DOES NOT WORK WELL. DO NOT USE!!

__author__ = 'ohd96'
import numpy as np
import cv2

image = cv2.imread("E:\\Shared OS folder\\iGEM\Images\\Focused Marchantia\\focusedMarchantia1\\focusedMarchantia1.jpg", cv2.IMREAD_COLOR)
output = image.copy()
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# detect circles in the image
circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1.35 , minDist = 1, minRadius = 0, maxRadius = 2000)

# ensure at least some circles were found
if circles is not None:
	# convert the (x, y) coordinates and radius of the circles to integers
	circles = np.round(circles[0, :]).astype("int")

	# loop over the (x, y) coordinates and radius of the circles
	for (x, y, r) in circles:
		# draw the circle in the output image, then draw a rectangle
		# corresponding to the center of the circle
		cv2.circle(output, (x, y), r, (0, 255, 0), 4)
		cv2.rectangle(output, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)

	# show the output image
	cv2.imwrite("circles_output.jpg", np.hstack([image, output]))
	print("Found " + str(len(circles)))