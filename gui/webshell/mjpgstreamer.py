import os
import threading
import subprocess

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
        threading.Thread(target=MjpgStreamer._start).start()
        pass

    @staticmethod
    def stop():
        # stop mjpg-streamer
        os.system("killall mjpg_streamer")
        MjpgStreamer._started = False
        pass

