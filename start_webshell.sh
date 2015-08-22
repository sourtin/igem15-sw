#!/bin/bash
#python -m gui.webshell
source pyenv/bin/activate
pyenv/bin/gunicorn -w 4 -b 127.0.0.1:9001 gui.webshell.__main__:app &
pyenv/bin/gunicorn -w 4 -b 127.0.0.1:9003 gui.admin.__main__:app &
pyenv/bin/nginx -p nginx -c nginx.conf
