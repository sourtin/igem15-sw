from werkzeug.contrib.fixers import ProxyFix
from flask import Flask
from flask import request
import re, json
import string, random
#from crypt import crypt
import os, subprocess

app = Flask(__name__)

def admin(u):
    if u == "admin":
        return True
    else:
        return False

def md5_password(password):
    return subprocess.check_output(['openssl', 'passwd', '-apr1', password]).decode('utf-8').strip()

@app.route("/")
def root():
    return '<meta http-equiv="refresh" content="0;URL=/admin/index.html">'

@app.route("/set/<user>/<pw>")
def set(user, pw):
    if request.authorization.username != "admin":
        return 'Not authorized'

    pattern = re.compile('[\W_]+')
    user = pattern.sub('', user)
    #pw = crypt(pw, ''.join(random.choice(string.ascii_letters + string.digits + '/.')for x in range(2)) )
    pw = md5_password(pw)

    lines = [line for line in open('nginx/server.htpasswd')]
    lines_dis = [line for line in open('nginx/server.htpasswd.disabled')]
    users = [line.split(":")[0] for line in lines]
    users_dis = [line.split(":")[0] for line in lines_dis]

    if user in users_dis:
        lines_dis[users_dis.index(user)] = user+":"+pw+"\n"
    elif user in users:
        lines[users.index(user)] = user+":"+pw+"\n"
    else:
        lines.append(user+":"+pw+"\n")

    fo = open("nginx/server.htpasswd", "w")
    fo.writelines(lines)
    fo.close()
    fo = open("nginx/server.htpasswd.disabled", "w")
    fo.writelines(lines_dis)
    fo.close()
    os.system("pyenv/bin/nginx -p nginx -c nginx.conf -s reload")
    return 'OK'

@app.route("/del/<user>")
def rem(user):
    if request.authorization.username != "admin":
        return 'Not authorized'

    if user == "admin":
        return 'Not allowed'

    lines = [line for line in open('nginx/server.htpasswd')]
    lines_dis = [line for line in open('nginx/server.htpasswd.disabled')]
    users = [line.split(":")[0] for line in lines]
    users_dis = [line.split(":")[0] for line in lines_dis]

    if user in users:
        del lines[users.index(user)]
    if user in users_dis:
        del lines_dis[users_dis.index(user)]

    fo = open("nginx/server.htpasswd", "w")
    fo.writelines(lines)
    fo.close()
    fo = open("nginx/server.htpasswd.disabled", "w")
    fo.writelines(lines_dis)
    fo.close()
    os.system("pyenv/bin/nginx -p nginx -c nginx.conf -s reload")

    return 'ok'

@app.route("/enable/<user>")
def enable(user):
    if request.authorization.username != "admin":
        return 'Not authorized'

    lines = [line for line in open('nginx/server.htpasswd')]
    lines_dis = [line for line in open('nginx/server.htpasswd.disabled')]
    users = [line.split(":")[0] for line in lines]
    users_dis = [line.split(":")[0] for line in lines_dis]

    if user in users_dis:
        i = users_dis.index(user)
        l = lines_dis[i]
        lines.append(l)
        del lines_dis[i]
    
    fo = open("nginx/server.htpasswd", "w")
    fo.writelines(lines)
    fo.close()
    fo = open("nginx/server.htpasswd.disabled", "w")
    fo.writelines(lines_dis)
    fo.close()
    os.system("pyenv/bin/nginx -p nginx -c nginx.conf -s reload")

    return 'kool'

@app.route("/disable/<user>")
def disable(user):
    if request.authorization.username != "admin":
        return 'Not authorized'

    lines = [line for line in open('nginx/server.htpasswd')]
    lines_dis = [line for line in open('nginx/server.htpasswd.disabled')]
    users = [line.split(":")[0] for line in lines]
    users_dis = [line.split(":")[0] for line in lines_dis]

    if user in users:
        i = users.index(user)
        l = lines[i]
        lines_dis.append(l)
        del lines[i]
    
    fo = open("nginx/server.htpasswd", "w")
    fo.writelines(lines)
    fo.close()
    fo = open("nginx/server.htpasswd.disabled", "w")
    fo.writelines(lines_dis)
    fo.close()
    os.system("pyenv/bin/nginx -p nginx -c nginx.conf -s reload")

    return 'sure thang'

@app.route("/get/")
def get():
    if request.authorization.username != "admin":
        return 'Not authorized'

    lines = [line.rstrip('\n') for line in open('nginx/server.htpasswd')]
    lines = [line.split(":")[0] for line in lines]
    return json.dumps(lines)

@app.route("/get_disabled/")
def get_dis():
    if request.authorization.username != "admin":
        return 'Not authorized'

    lines = [line.rstrip('\n') for line in open('nginx/server.htpasswd.disabled')]
    lines = [line.split(":")[0] for line in lines]
    return json.dumps(lines)

app.wsgi_app = ProxyFix(app.wsgi_app)

if __name__ == '__main__':
    app.run('0.0.0.0', 9003, debug=True)
