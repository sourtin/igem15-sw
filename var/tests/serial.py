#!/usr/bin/env python3
import traceback
import threading
import serial
import os
import sys
import glob

"""very simple serial rw interface;
   connects to the first serial device it finds (or
   a cli-specified one in $1) and will print every
   line received and send any lines you enter until
   ^D is entered."""

try:
    ser = serial.Serial(sys.argv[1], 115200)
except (FileNotFoundError, serial.serialutil.SerialException, IndexError):
    devs = glob.glob("/dev/ttyACM*")
    if not len(devs):
        print("No devices found!")
        exit()
    ser = serial.Serial(devs[0], 115200, timeout=1)

def cat():
    """this thread simply prints any lines received over com"""
    while True:
        try:
            line = ser.readline()
            if len(line):
                try:
                    print(line.decode()[:-1])
                except:
                    print("unreadable")
        except (TypeError, serial.serialutil.SerialException):
            print("shit man")
            ser.close()
            break
    print("disconnected!")
    ser.close()
    os._exit(1)
t = threading.Thread(target=cat)
t.daemon = True #no zombies
t.start()

while True:
    try:
        cmd = str(input())
        ser.write((cmd + '\r\n').encode())
        ser.flush()
    except EOFError:
        print("\n")
        print("bye!")
        break
    except KeyboardInterrupt:
        print()
        continue
    except:
        print(traceback.format_exc())
        continue

ser.close()

