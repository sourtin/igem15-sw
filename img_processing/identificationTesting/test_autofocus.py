import os
import picamera
import picamera.array
import cv2
import time
import numpy as np
import dwt

while(1):
	with picamera.PiCamera() as camera:
	    camera.start_preview()
	    time.sleep(0.1)
	    with picamera.array.PiRGBArray(camera) as stream:
	        camera.capture(stream, format = 'bgr')
	        image = cv2.cvtColor(stream.array, cv2.COLOR_BGR2GRAY)

	Y = dwt.nleveldwt(3,image)
    print(dwt.focus_score(Ys[1:]))
