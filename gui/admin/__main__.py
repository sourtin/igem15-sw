from werkzeug.contrib.fixers import ProxyFix
from flask import Flask
import re, json

app = Flask(__name__)

def admin(u):
    if u == "admin":
        return True
    else:
        return False

@app.route("/")
def root():
    return '<meta http-equiv="refresh" content="0;URL=/admin/index.html">'

@app.route("/set/<user>/<pw>")
def set(user, pw):
    pattern = re.compile('[\W_]+')"  
    user = pattern.sub('', user)

    lines = [line.rstrip('\n') for line in open('../../nginx/server.htpasswd')]
    lines_dis = [line.rstrip('\n') for line in open('../../nginx/server.htpasswd.disabled')]
    users = [line.split(":")[0] for line in lines]
    users_dis = [line.split(":")[0] for line in lines_dis]

    if user in users_dis:
        lines[users_dis.index(user)] = user+":"+pw
    elif user in users:
        lines[users.index(user)] = user+":"+pw
    else
        lines.append(user+":"+pw)

    fo = open("../../nginx/server.htpasswd", "w")
    fo.writelines(lines)
    fo.close()
    fo = open("../../nginx/server.htpasswd.disabled", "w")
    fo.writelines(lines)
    fo.close()

@app.route("/del/<user>")
def rem(user):
    return 'error'

@app.route("/enable/<user>")
def enable(user):
    return 'error'

@app.route("/disable/<user>")
def disable(user):
    return 'error'

@app.route("/get/")
def get():
    lines = [line.rstrip('\n') for line in open('../../nginx/server.htpasswd')]
    lines = [line.split(":")[0]]
    return json.dumps(lines)

@app.route("/get_disabled/")
def get():
    lines = [line.rstrip('\n') for line in open('../../nginx/server.htpasswd.disabled')]
    lines = [line.split(":")[0]]
    return json.dumps(lines)

app.wsgi_app = ProxyFix(app.wsgi_app)

if __name__ == '__main__':
    app.run('0.0.0.0', 9003)
