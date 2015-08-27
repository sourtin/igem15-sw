import os
import threading
import subprocess
import picamera
import time, datetime
import traceback
import re
import uuid

class MjpgStreamer:
    _started = False

    @staticmethod
    def is_running(process):
        s = subprocess.Popen(["ps", "axw"], stdout=subprocess.PIPE, universal_newlines=True)
        for x in s.stdout:
            if re.search(process, x):
                return True
        return False

    @staticmethod
    def _start():
        os.chdir("/home/pi/igem15-sw/contrib/mjpg-streamer/mjpg-streamer-experimental/")
        MjpgStreamer._started = True
        os.system('/home/pi/igem15-sw/contrib/mjpg-streamer/mjpg-streamer-experimental/run.sh')
        MjpgStreamer._started = False

    @staticmethod
    def start():
        # start mjpg-streamer
        if not MjpgStreamer.is_running("mjpg_streamer"):
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
        uid = str(uuid.uuid4())
        with picamera.PiCamera() as camera:
            camera.resolution = (1024, 768)
            camera.start_preview()
            time.sleep(0.1)
            camera.capture('%s.%s.jpg' % (fname, uid))
        MjpgStreamer.start()
        return '/captured/%s.%s.jpg' % (fname, uid)

