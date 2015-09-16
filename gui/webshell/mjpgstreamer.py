import os
import threading
import subprocess
import picamera
import time, datetime
import traceback
import re
import uuid
import fnmatch
import urllib

class MjpgStreamer:
    iso = "400"

    @staticmethod
    def touch(fname, times=None):
        with open(fname, 'a'):
            os.utime(fname, times)

    @staticmethod
    def is_running(process):
        s = subprocess.Popen(["ps", "axw"], stdout=subprocess.PIPE, universal_newlines=True)
        for x in s.stdout:
            if re.search(process, x):
                return True
        return False

    @staticmethod
    def prunedir(dir, level = 52428800): # level = 50M by default
        files = MjpgStreamer.returnold(dir)
        size = 0
        rm = []
        for f in files:
            size += os.path.getsize(f)
            #print("%s - %s / %s" % (f, size, level))
            if(size > level):
                rm.append(f)
                os.remove(f)
        return "Removed: %s" % rm

    @staticmethod
    def returnold(folder):
        matches = []
        for root, dirnames, filenames in os.walk(folder):
            for filename in fnmatch.filter(filenames, '*'):
                matches.append(os.path.join(root, filename))
        return sorted(matches, key=os.path.getmtime)

    @staticmethod
    def _start():
        os.chdir("/home/pi/igem15-sw/contrib/mjpg-streamer/mjpg-streamer-experimental/")
        subprocess.call(['/bin/bash', '/home/pi/igem15-sw/contrib/mjpg-streamer/mjpg-streamer-experimental/run.sh', MjpgStreamer.iso])

    @staticmethod
    def start():
        # start mjpg-streamer
        if not MjpgStreamer.is_running("mjpg_streamer") and not os.path.isfile("/tmp/igemcam-lock"):
            threading.Thread(target=MjpgStreamer._start).start()

    @staticmethod
    def stop():
        # stop mjpg-streamer
        subprocess.call(["killall", "-9", "mjpg_streamer"])

    @staticmethod
    def captureImg(user):
        MjpgStreamer.touch("/tmp/igemcam-lock")
        MjpgStreamer.stop()
        os.makedirs("/home/pi/igem15-sw/captured", exist_ok=True)
        os.chdir("/home/pi/igem15-sw/captured")
        os.makedirs(user, exist_ok=True)
        fname = str(datetime.datetime.now())
        uid = str(uuid.uuid4())
        with picamera.PiCamera() as camera:
            camera.resolution = (2048, 1536)
            camera.exposure_mode = 'night'
            camera.start_preview()
            time.sleep(0.1)
            camera.capture('%s/%s.%s.jpg' % (user.replace('/', ''), fname, uid))
        os.remove("/tmp/igemcam-lock")
        MjpgStreamer.start()
        return '/captured/%s/%s.%s.jpg' % (user.replace('/', ''), fname, uid)

    @staticmethod
    def captureSnap(user):
        os.makedirs("/home/pi/igem15-sw/captured", exist_ok=True)
        os.chdir("/home/pi/igem15-sw/captured")
        os.makedirs(user, exist_ok=True)
        fname = str(datetime.datetime.now())
        uid = str(uuid.uuid4())

        url = 'http://localhost:9002/?action=snapshot'
        urllib.request.urlretrieve(url, '%s/%s.%s.jpg' % (user.replace('/', ''), fname, uid))
        return '/captured/%s/%s.%s.jpg' % (user.replace('/', ''), fname, uid)
