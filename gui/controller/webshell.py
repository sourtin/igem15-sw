from waitress import serve
from flask import Flask
from mjpgstreamer import MjpgStreamer

app = Flask(__name__, static_url_path='/webshell')

@app.route("/")
def root():
    return '<meta http-equiv="refresh" content="0;URL=/webshell/main.html">'

@app.route("/control/power/<onoff>")
def control_power(onoff):
    if onoff == "on" and not MjpgStreamer._started:
        MjpgStreamer.start()
        return 'started'
    elif onoff == "off" and MjpgStreamer._started:
        MjpgStreamer.stop()
        return 'stopped'
    return 'error'

if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=9000)
