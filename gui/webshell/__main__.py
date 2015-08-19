from waitress import serve
from flask import Flask
from mjpgstreamer import MjpgStreamer
from hw.ledcontrol.ledcontrol_p2 import LEDControl

app = Flask(__name__, static_url_path='/ui')
leds = LEDControl("/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_5543434383335181A060-if00")

@app.route("/")
def root():
    return '<meta http-equiv="refresh" content="0;URL=/ui/main.html">'

@app.route("/control/power/<onoff>")
def control_power(onoff):
    if onoff == "on" and not MjpgStreamer._started:
        MjpgStreamer.start()
        return 'started'
    elif onoff == "off" and MjpgStreamer._started:
        MjpgStreamer.stop()
        return 'stopped'
    return 'error'

@app.route("/control/led/<mode>/<setting>")
def control_led(mode, setting):
    if mode == "get":
        return str(leds.get_mode())
    elif mode == "set":
        leds.set_mode(setting)
        return 'Set!'
    elif mode == "toggle":
        leds.toggle()
        return str(leds.get_mode())
    return 'error'

MjpgStreamer.start() # Start camera by default
serve(app, host='0.0.0.0', port=9000)
