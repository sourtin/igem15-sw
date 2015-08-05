#!/usr/bin/env python3
import serial
from enum import Enum

class Axes(Enum):
    AXIS_X=0
    AXIS_Y=1
    AXIS_Z=2

class Shapeoko:
    def __init__(self, port):
        self.ser = serial.Serial(port, 115200)

    def move(self, vector):
        send = "G0 "
        if(vector[0] is not None):
            send += "X"+str(vector[0])+" "
        if(vector[1] is not None):
            send += "Y"+str(vector[1])+" "
        if(vector[2] is not None):
            send += "Z"+str(vector[2])+" "
        self.ser.write((send+"\r\n").encode())
        self.ser.flush()

    def home(self, ax):
        for a in ax:
            # abscissa
            if(a == Axes.AXIS_X):
                self.ser.write("G28 X\r\n".encode())
                self.ser.flush()
            # ordinate
            elif(a == Axes.AXIS_Y):
                self.ser.write("G28 Y\r\n".encode())
                self.ser.flush()
            # applicate
            elif(a == Axes.AXIS_Z):
                self.ser.write("G28 Z\r\n".encode())
                self.ser.flush()

if __name__ == "__main__":
    import cmd
    class ShapeokoInterpreter(cmd.Cmd):
        prompt = '[Shapeoko v1] '
        def __init__(self):
            cmd.Cmd.__init__(self)
            self.shap = None

        def do_load(self, port):
            self.shap = Shapeoko("/dev/ttyACM"+str(port))

        def do_home(self, axes):
            if self.shap is None:
                print("*** Load a shapeoko first! [load <n>] where n is the ttyACM number")
                return
            args = []
            if "x" in axes:
                args.append(Axes.AXIS_X)
            if "y" in axes:
                args.append(Axes.AXIS_Y)
            if "z" in axes:
                args.append(Axes.AXIS_Z)
            print("Homing ", args)
            self.shap.home(args)

        def do_move(self, mov):
            l = mov.split()
            if(len(l) < 3):
                print("*** Please give me three arguments! (x,y,z) [Use 0 for no movement on an axis)")
                return
            if self.shap is None:
                print("*** Load a shapeoko first! [load <n>] where n is the ttyACM number")
                return
            l = [(a if a is not "0" else None) for a in l]
            self.shap.move([ l[0] , l[1], l[2] ])

        def do_EOF(self, line):
            return True

    ShapeokoInterpreter().cmdloop()
