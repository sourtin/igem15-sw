import serial
import time
import glob

def hotplug(f):
    def decor(self, *args):
        if self._ser is None:
            self.reconnect()
        try:
            ret = f(self, *args)
            self._ser.flush()
            return ret
        except:
            self.close()
        return None
    return decor

class HWControl:
    def __init__(self):
        self._ser = None
        self.reconnect()

    def reconnect(self):
        self.close()
        for dev in glob.glob("/dev/serial/by-path/*"):
            ser = serial.Serial(dev, 9600, timeout=1)
            if "connected" in self._ser.readline().decode("utf-8"):
                self._ser = ser
                return

    def close(self):
        try:
            self._ser.close()
        except:
            pass
        self._ser = None

    @hotplug
    def set_led_mode(self, mode):
        self._ser.write(("l%db" % mode).encode())

    @hotplug
    def get_led_mode(self):
        self._ser.write('a'.encode())
        return int.from_bytes(self._ser.read(), byteorder='big')

    @hotplug
    def toggle_led(self):
        self.set_mode(int(self.get_mode()) + 1)

    @hotplug
    def move(self, axis, step):
        self._ser.write(('m%d%s%dg' % (axis, "+" if amount > 0 else "", amount)).encode())

