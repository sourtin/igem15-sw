# Ports used by the microscopy package:
* 0.0.0.0:9000 - nginx (web-accessible)
* localhost:9001 - gunicorn for webshell
* localhost:9002 - mjpg-streamer
* localhost:9003 - gunicorn for admin panel
* localhost:9004 - tileserver for micromaps

# Key

localhost:x means the port is bound to the loopback network driver and is inaccessible over a network.

0.0.0.0:x means the port is bound to all network interfaces and is accessible over a network
