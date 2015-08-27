from werkzeug.contrib.fixers import ProxyFix
from flask import Flask

import sys
sys.path.append("/home/pi/igem15-sw/")

from gui.webshell.mjpgstreamer import MjpgStreamer
from hw.ledcontrol.ledcontrol_p2 import LEDControl

app = Flask(__name__)
leds = None

def init_leds():
    global leds
    try:
        leds = LEDControl("/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_5543434383335181A060-if00")
    except:
        leds = None
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
    return MjpgStreamer.captureImg()

@app.route("/control/reload/")
def reload():
    global leds
    if leds != None:
        leds.close()
    init_leds()
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

#MjpgStreamer.start() # Start camera by default

app.wsgi_app = ProxyFix(app.wsgi_app)
init_leds()

if __name__ == '__main__':
    app.run('0.0.0.0', 9001, debug=True)
