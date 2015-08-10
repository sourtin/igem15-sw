#!/usr/bin/env python3
import threading
import serial
import sys
import glob

try:
    ser = serial.Serial(sys.argv[1], 115200)
except (FileNotFoundError, serial.serialutil.SerialException, IndexError):
    dev = glob.glob("/dev/ttyACM*")
    ser = serial.Serial(dev[0], 115200, timeout=1)

def cat():
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
t = threading.Thread(target=cat)
t.daemon = True
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

ser.close()

