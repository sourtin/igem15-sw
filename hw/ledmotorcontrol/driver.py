import serial
import time
import glob
import sys

def hotplug(f):
    def decor(*args):
        if _ser is None:
            reconnect()
        try:
            ret = f(*args)
            _ser.flush()
            return ret
        except:
            close()
            raise
        return None
    return decor

def reconnect():
    global _ser
    close()
    for dev in glob.glob("/dev/serial/by-path/*"):
        ser = serial.Serial(dev, 9600, timeout=2)
        ser.setDTR(False)
        time.sleep(0.1)
        ser.setDTR(True)
        if "connected" in ser.readline().decode("utf-8"):
            print("Established")
            _ser = ser
            return

def close():
    global _ser
    try:
        _ser.close()
    except:
        pass
    del _ser
    _ser = None

@hotplug
def set_led_mode(mode):
    _ser.write(("l%db" % mode).encode())

@hotplug
def get_led_mode():
    _ser.write('a'.encode())
    return int.from_bytes(_ser.read(), byteorder='big')

@hotplug
def toggle_led():
    set_led_mode(int(get_led_mode()) + 1)

@hotplug
def move(axis, amount):
    _ser.write(('m%d%s%dg' % (axis, "+" if amount > 0 else "", amount)).encode())

_ser = None
reconnect()
