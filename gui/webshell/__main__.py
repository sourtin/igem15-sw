from werkzeug.contrib.fixers import ProxyFix
from flask import Flask
from flask import request

import sys
sys.path.append("/home/pi/igem15-sw/")

from gui.webshell.mjpgstreamer import MjpgStreamer
from gui.webshell.timelapser import Timelapser
from hw.ledmotorcontrol import driver

tl = ['', 0, 0]
tlThread = None
app = Flask(__name__)

@app.route("/timelapse/set/<delay>/<times>")
def timelapse(delay, times):
    global tl, tlThread
    if tl[0] == '':
        pass # todo: notify user their timelapse was interrupted by another user

    tl = [request.authorization.username, int(delay), int(times)]
    # stop thread
    if tlThread is not None:
        tlThread.stop()
        tlThread.join()
    # start thread
    tlThread = Timelapser(tl)
    tlThread.start()
    return 'Timelapse set'

@app.route("/timelapse/get/")
def get_if_timelapse():
    global tlThread, tl
    if tlThread.stopped():
         del tlThread
         tlThread = None
         tl = ['', 0, 0]
    return json.dumps(tl)

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
    driver.move_motor(int(axis), int(amount))
    return 'done'

app.wsgi_app = ProxyFix(app.wsgi_app)

if __name__ == '__main__':
    app.run('0.0.0.0', 9001, debug=True)
