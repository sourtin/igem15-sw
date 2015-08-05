#!/usr/bin/env python3
import serial
import enum

class Axes(enum.Enum):
    """An enum that defines the three axes that can be moved in"""
    AXIS_X=0
    AXIS_Y=1
    AXIS_Z=2

class Shapeoko:
    """Python bindings to communicate to the Shapeoko via GCode"""

    def __init__(self, port):
        """ Start a serial comm channel with the shapeoko, pass it the device file as a string to connect to"""
        self.ser = serial.Serial(port, 115200)

    def move(self, vector):
        """Move the head in a vector all at once - vector should be a list [x,y,z]. Negative values indicate reverse movement"""
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
        """ Home the head in a certain number of axes. ax should be a list of enums of type Axes. If multiple axes are to be calibrated, the X axis is calibrated first, then Y, then Z."""
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
            self.ser.write(send.encode())
            self.ser.flush()

# Launch a command interpreter to test out shapeoku api
if __name__ == "__main__":
    import cmd
    class ShapeokoInterpreter(cmd.Cmd):
        prompt = 'Shapeoku# '
        def __init__(self):
            cmd.Cmd.__init__(self)
            self.shap = None

        def do_load(self, port):
            if self.shap is not None:
                self.shap.close()
                print("Closed already open comm channel...")
            try:
                self.shap = Shapeoko("/dev/ttyACM"+str(port))
                print("Opened comm channel")
            except:
                print("*** Error opening device")

        def do_home(self, axes):
            handled = 0
            args = []
            if "x" in axes:
                args.append(Axes.AXIS_X)
                handled = 1
            if "y" in axes:
                args.append(Axes.AXIS_Y)
                handled = 1
            if "z" in axes:
                args.append(Axes.AXIS_Z)
                handled = 1
            if handled is 0:
                print("*** Usage: home [xyz]")
                return
            if self.shap is None:
                print("*** Load a shapeoko first! [load <n>] where n is the ttyACM number")
                return
            print("Homing ", args)
            self.shap.home(args)

        def do_move(self, mov):
            l = mov.split()
            if(len(l) < 3):
                print("*** Usage: move x y z (Use 0 for no movement on an axis)")
                return
            if self.shap is None:
                print("*** Load a shapeoko comm channel first! [load <n>] where n is the ttyACM number")
                return
            l = [(a if a is not "0" else None) for a in l]
            print("Moving x=",l[0],", y=",l[1], ", z=", l[2])
            self.shap.move([ l[0] , l[1], l[2] ])

        def do_EOF(self, line):
            return True

    ShapeokoInterpreter().cmdloop()
