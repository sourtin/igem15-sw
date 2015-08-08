import serial
import time

ser = serial.Serial("/dev/ttyACM0", 9600)
#ser.open()
while True:
    ser.write("\x01")
    ser.flush()
    time.sleep(1)
    ser.write("\x00")
    ser.flush()
    time.sleep(1)
