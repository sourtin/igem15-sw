from werkzeug.contrib.fixers import ProxyFix
from flask import Flask
from flask import request

import sys
sys.path.append("/home/pi/igem15-sw/")

from gui.webshell.mjpgstreamer import MjpgStreamer
from hw.ledmotorcontrol import driver

app = Flask(__name__)

@app.route("/")
def root():
    return '<meta http-equiv="refresh" content="0;URL=/webshell/main.html">'

@app.route("/control/power/<onoff>")
def control_power(onoff):
    if onoff == "on":
        MjpgStreamer.start()
        return 'started'
    elif onoff == "off":
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

@app.route("/control/led/<mode>/<setting>")
def control_led(mode, setting):
    error = "No LED board connected"

    if mode == "get":
        r = driver.get_led_mode()
        return str(r) if r is not None else error
    elif mode == "set":
        driver.set_led_mode(int(setting))
        return 'Set!'
    elif mode == "toggle":
        driver.toggle_led()
        r = driver.get_led_mode()
        return str(r) if r is not None else error
    return 'error'

@app.route("/control/motor/<axis>/<amount>")
def control_mot(axis, amount):
    driver.move(int(axis), int(amount))
    return 'done'

app.wsgi_app = ProxyFix(app.wsgi_app)

if __name__ == '__main__':
    app.run('0.0.0.0', 9001, debug=True)
