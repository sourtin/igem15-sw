import os
import picamera
import picamera.array
import cv2
import time

with picamera.PiCamera() as camera:
    camera.start_preview()
    time.sleep(0.1)
    with picamera.array.PiRGBArray(camera) as stream:
        camera.capture(stream, format = 'gray')
        image = stream.array

print(image.dtype, image.shape)