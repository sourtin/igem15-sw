from werkzeug.contrib.fixers import ProxyFix
from flask import Flask
from flask import request
import json

import sys
sys.path.append("/home/pi/igem15-sw/")

from gui.webshell.mjpgstreamer import MjpgStreamer
import gui.webshell.locker
from gui.webshell.timelapser import Timelapser
from hw.ledmotorcontrol import driver

tlThread = None

app = Flask(__name__)

@app.route("/timelapse/set/<delay>/<times>")
def timelapse(delay, times):
    global tlThread

    if gui.webshell.locker.lockobj[0] != request.authorization.username and not gui.webshell.locker.lock(request.authorization.username, "timelapse"):
        return 'Webshell locked by %s for %s' % (gui.webshell.locker.lockobj[0], gui.webshell.locker.lockobj[1])

    # stop thread
    if tlThread is not None:
        tlThread.stop()
        tlThread.join()
    # start thread
    tlThread = Timelapser([request.authorization.username, int(delay), int(times)])
    tlThread.start()
    return 'Timelapse set'

@app.route("/timelapse/get/")
def get_if_timelapse():
    global tlThread
    if tlThread is not None:
        return json.dumps(tlThread.tl)
    else:
        return json.dumps(['', 0, 0])

## todo: move to seperate module
@app.route("/zstack/<amount>/<times>")
def zstack(amount, times):
    imgs = []
    for _ in xrange(int(times)):
        imgs.append(MjpgStreamer.captureImg(request.authorization.username))
        driver.move_motor(2, int(amount))
    # todo:
    # apply z stack algorithm to images
    # save image
    # return image file
    # for now, link to the captured images and let user do it themselves
    ret = ''
    for a in imgs:
        ret += '<a href="'+a+'">'+a+'</a><br/>'
    return ret

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

@app.route("/snap/")
def snap():
    return MjpgStreamer.captureSnap(request.authorization.username)

@app.route("/prune/")
def prune():
    return MjpgStreamer.prunedir("/home/pi/igem15-sw/captured/%s" % request.authorization.username)

@app.route("/pruneall/")
def pruneall():
    if request.authorization.username == "admin":
        return MjpgStreamer.prunedir("/home/pi/igem15-sw/captured/", 524288000)
    else:
        return "Error - cannot delete other user's data unless you are admin"

@app.route("/iso/set/<set>")
def iso_set(set):
    MjpgStreamer.iso = str(int(set))
    return 'set iso, restart stream to see'

@app.route("/iso/get/")
def iso_get():
    return MjpgStreamer.iso

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
    driver.move_motor(int(axis), int(amount))
    return 'done'

app.wsgi_app = ProxyFix(app.wsgi_app)

if __name__ == '__main__':
    app.run('0.0.0.0', 9001, debug=True)
