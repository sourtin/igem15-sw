import os
import threading
import subprocess
import picamera
import time

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
        print("____start___")
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
        with picamera.PiCamera() as camera:
            camera.resolution = (1024, 768)
            camera.start_preview()
            time.sleep(0.1)
            camera.capture('foo.jpg')
        MjpgStreamer.start()
        return '<img src="/captured/foo.jpg">'

