from werkzeug.contrib.fixers import ProxyFix
from flask import Flask
from flask import request

import sys
sys.path.append("/home/pi/igem15-sw/")

from gui.webshell.mjpgstreamer import MjpgStreamer
from hw.ledcontrol.ledcontrol import LEDControl
from hw.motorcontrol.motorcontrol import MotorControl

app = Flask(__name__)
leds = None
mots = None

def init_leds():
    global leds
    try:
        leds = LEDControl("/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_5543434383335181A060-if00")
    except:
        leds = None
        pass

def init_mots():
    global mots
    try:
        mots = MotorControl("/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_55434343833351813261-if00")
    except:
        print("error connecting motors")
        mots = None
        pass

@app.route("/")
def root():
    return '<meta http-equiv="refresh" content="0;URL=/webshell/main.html">'

@app.route("/control/power/<onoff>")
def control_power(onoff):
    if onoff == "on":# and not MjpgStreamer._started:
        MjpgStreamer.start()
        return 'started'
    elif onoff == "off":# and MjpgStreamer._started:
        MjpgStreamer.stop()
        return 'stopped'
    return 'error'

@app.route("/capture/")
def capture():
    return MjpgStreamer.captureImg(request.authorization.username)

@app.route("/prune/")
def prune():
    return MjpgStreamer.prunedir("/home/pi/igem15-sw/captured/%s" % request.authorization.username)

@app.route("/pruneall/")
def pruneall():
    if request.authorization.username == "admin":
        return MjpgStreamer.prunedir("/home/pi/igem15-sw/captured/", 524288000)
    else:
        return "Error - cannot delete other user's data unless you are admin"

@app.route("/control/reload/")
def reload():
    global leds
    if leds != None:
        leds.close()
    init_leds()
    return 'done'

@app.route("/control/reload_motors/")
def reload_mots():
    global mots
    if mots != None:
        mots._ser.close()
        del mots
    init_motors()
    return 'done'

@app.route("/control/led/<mode>/<setting>")
def control_led(mode, setting):
    global leds

    if leds is None:
        return 'No LED control board connected'

    if mode == "get":
        return str(leds.get_mode())
    elif mode == "set":
        leds.set_mode(setting)
        return 'Set!'
    elif mode == "toggle":
        leds.toggle()
        return str(leds.get_mode())
    return 'error'

@app.route("/control/motor/<axis>/<amount>")
def control_mot(axis, amount):
    global mots

    if mots is None:
        return 'No Motor control board connected'

    mots._move(int(axis), int(amount))
    return 'done'

#MjpgStreamer.start() # Start camera by default

app.wsgi_app = ProxyFix(app.wsgi_app)
init_leds()
init_mots()

if __name__ == '__main__':
    app.run('0.0.0.0', 9001, debug=True)
