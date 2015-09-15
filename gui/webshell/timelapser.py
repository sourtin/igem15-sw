import threading
import time

import sys
sys.path.append("/home/pi/igem15-sw/")

from gui.webshell.mjpgstreamer import MjpgStreamer

class Timelapser(threading.Thread):
    def __init__(self, tl):
        super(Timelapser, self).__init__()
        self._stop = threading.Event()
        self._times = tl[2]+1
        self._delay = tl[1]
        self._garçon = 0
        self._user = tl[0]

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def run(self):
        while not self.stopped() and self._times > 0:
            if self._garçon == 0:
                self._times -= 1
                self._garçon = self._delay
                try:
                    MjpgStreamer.captureImg(self._user)
                except:
                    print("Exception taking picture...")
            self._garçon -= 1
            #print("delay=%d, waiter=%d" % (self._delay, self._garçon))
            time.sleep(1)
        self.stop()
