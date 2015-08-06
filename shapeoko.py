#!/usr/bin/env python3
import serial
import enum

class Axes(enum.Enum):
    """An enum that defines the three axes that can be moved in"""
    X=0 # abscissa
    Y=1 # ordinate
    Z=2 # applicate

class Shapeoko:
    """Python bindings to communicate to the Shapeoko via GCode"""

    def __init__(self, port):
        """ Start a serial comm channel with the shapeoko.
            Pass it the device file as a string to connect to"""
        self.ser = serial.Serial(port, 115200)
        self._speed = 10000

    def gcode(self, code):
        self.ser.write((str(code)+"\r\n").encode())
        self.ser.flush()

    def speed(self, set):
        self._speed = int(set)

    def move(self, vector):
        """ Move the head to a position.
                vector should be a list [x,y,z]."""

        names = ["X", "Y", "Z"]

        sv = [(names[i]+str(int(a)) if a is not None else "") for i, a in enumerate(vector)]

        send = "G0 "+' '.join(sv)

        print(send+" F"+str(self._speed)+"\r\n")
        self.ser.write((send+" F"+str(self._speed)+"\r\n").encode())
        self.ser.flush()

    def home(self, ax):
        """ Home the head in a certain number of axes.
                ax should be a list of enums of type Axes.
            If multiple axes are to be calibrated, the X axis is calibrated first, then Y, then Z."""
        for a in ax:
            self.ser.write(("G28 "+a.name+"\r\n").encode())
        self.ser.write("G0 X0 Y0 Z0")
        self.ser.flush()

    def close(self):
        self.ser.close()
        self.ser = None


# Launch a command interpreter to test out shapeoku api
if __name__ == "__main__":
    import cmd
    import glob

    class ShapeokoInterpreter(cmd.Cmd):
        prompt = 'Shapeoko# '
        def __init__(self):
            cmd.Cmd.__init__(self)
            self.shap = None

        def emptyline(self):
            pass

        def do_load(self, port):
            """  load [ttydev]
                     Load a shapeoko.
                         [ttydev] - Connect to the file /dev/ttydev """
            self.do_close()
            try:
                self.shap = Shapeoko("/dev/"+str(port))
                print("Opened comm channel")
            except Exception as e:
                print("*** Error opening device: %s" % e)

        def complete_load(self, text, line, begidx, endidx):
            return [a[begidx:] for a in glob.glob("/dev/ttyACM*")]

        def do_close(self, *args):
            """  close
                     Close the comm channel with the shapeoko"""
            if self.shap is not None:
                self.shap.close()
                self.shap = None
                print("Closed already open comm channel...")

        def serial_cmd(method):
            def checked_cmd(self, *args):
                if self.shap is None:
                    print("*** Load a shapeoko first! [load <n>] where n is the ttyACM number")
                    return
                return method(self, *args)
            return checked_cmd

        def help_home(self):
            print("home [xyz]\n\
    Home the axes passed as an argument.\n\
        Usage: home x - Home x axis\n\
            home xy - Home x axis and y axis\n\
            home yz - Home y axis and z axis\n\
            home xyz - Home all axes\n\
            home zy - Home y axis and z axis")

        @serial_cmd
        def do_home(self, axes):
            handled = 0
            args = []
            if "x" in axes:
                args.append(Axes.X)
                handled = 1
            if "y" in axes:
                args.append(Axes.Y)
                handled = 1
            if "z" in axes:
                args.append(Axes.Z)
                handled = 1
            if handled is 0:
                print("*** Usage: home [xyz]")
                return
            print("Homing ", args)
            try:
                self.shap.home(args)
            except:
                print("*** Error sending homing command")

        def help_move(self):
            print("move x y z\n\
    Move the head simultaneously in [x,y,z].\n\
    Must pass all three arguments, use - for no movement\n\
        Usage: move 100 0 0 = move to (100,0,0)\n\
               move 100 100 - = move to (100,100) in x and y direction\n\
        The firmware should prevent overdriving the motors.")

        @serial_cmd
        def do_move(self, mov):
            l = mov.split()
            if(len(l) < 3):
                print("*** Usage: move x y z (Use - for no movement on an axis)")
                return
            l = [(a if a is not "-" else None) for a in l]
            print("Moving x=",l[0],", y=",l[1], ", z=", l[2])
            try:
                self.shap.move([ l[0] , l[1], l[2] ])
            except:
                print("*** Error sending move command")

        @serial_cmd
        def do_send(self, code):
            if code.strip() is "":
                print("*** Usage: send [g-code]")
                return
            try:
                self.shap.gcode(code)
                print("Sent ", code)
            except:
                print("*** Error sending g-code")

        @serial_cmd
        def do_speed(self, set):
            if set.strip() is "":
                print("*** Usage: speed [speed in mm/sec]")
                return
            self.shap.speed(set)
            print("Set speed to ", set)

        def do_EOF(self, line):
            self.do_close()
            print("*** Bye!")
            return True

    ShapeokoInterpreter().cmdloop()
