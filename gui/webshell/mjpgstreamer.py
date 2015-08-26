import os
import threading
import subprocess
import picamera
import time, datetime
#import traceback

class MjpgStreamer:
    _started = False

    @staticmethod
    def _start():
        os.system("killall mjpg_streamer")
        os.chdir("/home/pi/igem15-sw/contrib/mjpg-streamer/mjpg-streamer-experimental/")
        MjpgStreamer._started = True
        os.system('/home/pi/igem15-sw/contrib/mjpg-streamer/mjpg-streamer-experimental/run.sh')
        MjpgStreamer._started = False

    @staticmethod
    def start():
        # start mjpg-streamer
        #traceback.print_stack()
        threading.Thread(target=MjpgStreamer._start).start()

    @staticmethod
    def stop():
        # stop mjpg-streamer
        os.system("killall mjpg_streamer")
        MjpgStreamer._started = False

    @staticmethod
    def captureImg():
        MjpgStreamer.stop()
        os.chdir("/home/pi/igem15-sw/captured")
        fname = str(datetime.datetime.now())
        with picamera.PiCamera() as camera:
            camera.resolution = (1024, 768)
            camera.start_preview()
            time.sleep(0.1)
            camera.capture('%s.jpg' % fname)
        MjpgStreamer.start()
        return '/captured/%s.jpg' % fname

