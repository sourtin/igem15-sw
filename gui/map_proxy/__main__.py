#!/usr/bin/env python3
from werkzeug.contrib.fixers import ProxyFix
from flask import Flask, Response, send_from_directory
import requests
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

@app.route("/")
def redir():
    return Response('<meta http-equiv="refresh" content="0;URL=/maps/main.html">')

@app.route('/<path:path>')
def proxy(path):
    req = requests.get("http://127.0.0.1:9005/%s" % path)
    return Response(req.content, mimetype=req.headers['content-type'])

if __name__ == '__main__':
    app.run('0.0.0.0', 9004, debug=True)

