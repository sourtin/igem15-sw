import serial
import time
import glob

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
        try:
            if "connected" in ser.readline().decode("utf-8"):
                print("Established")
                _ser = ser
                return
        except:
            pass

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
    global _led
    _ser.write(("l%db" % mode).encode())
    _led = mode

@hotplug
def get_led_mode():
    global _led
    _ser.write('a'.encode())
    mode = int.from_bytes(_ser.read(), byteorder='big')
    if _led is not mode:
        set_led_mode(_led)
        _ser.write('a'.encode())
        _led = int.from_bytes(_ser.read(), byteorder='big')
    return _led

@hotplug
def toggle_led():
    set_led_mode(int(get_led_mode()) + 1)

@hotplug
def move_motor(axis, amount):
    _pos[axis] += amount
    _ser.write(('m%d%s%dg' % (axis, "+" if amount > 0 else "", amount)).encode())

def calibrate_motors(vals):
    global _pos
    _pos = vals

def get_pos(axis):
    return _pos[axis]

_ser = None
_led = 0
_pos = [0, 0, 0]
reconnect()
