#!/usr/bin/env python3
import os
import serial
import threading
import queue
import traceback
import time

class Shapeoko(object):
    class Axes:
        x='X'
        y='Y'
        z='Z'

    def __init__(self, device, rate=115200, speed=9000, verbose=False):
        self.device = device
        self.rate = rate
        self._speed = speed
        self.verbose = verbose
        self.queue = queue.Queue()
        self.thread = threading.Thread(target=self.main)
        self.thread.daemon = True
        self.thread.start()

    def main(self):
        SerialException = serial.serialutil.SerialException
        while True:
            try:
                with serial.Serial(self.device, self.rate, timeout=1) as com:
                    self.loop(com)
            except (FileNotFoundError, TypeError, SerialException):
                print("Shapeoko connection error...")
                time.sleep(1)
            except Exception as e:
                print("Unknown error whilst trying to connect to the Shapeoko...")
                print(traceback.format_exc())
                print()
                time.sleep(10)

    def loop(self, com):
        time.sleep(1) # allow to startup
        print("Connected to Shapeoko")
        while com.isOpen():
            cmd, event, status, timeout = self.queue.get()
            try:
                com.write(("%s\r\n" % cmd).encode())
                com.flush()
                if self.verbose:
                    print("Sent: %s" % cmd)

                beginning = time.time()
                while True:
                    line = com.readline()

                    # verbose logging
                    if len(line) and self.verbose:
                        print(line[:-1].decode())

                    # command complete
                    if line[:2] == b'ok':
                        status[0] = True
                        break

                    # command timed out
                    if time.time() > beginning + timeout:
                        break
            finally:
                self.queue.task_done()
                event.set()

    # do command and block until ok
    def do(self, cmd, timeout=30):
        status = [False]
        event = threading.Event()
        self.queue.put((cmd, event, status, timeout))
        event.wait(timeout)
        return status[0]

    # block on command until complete
    def do_wait(self, cmd, timeout=30):
        beginning = time.time()
        status = self.do(cmd, timeout)
        self.do("M400", beginning + timeout - time.time())
        return status

    # block on a sequence of commands until all complete
    def do_seq(self, *cmds, timeout=30):
        status = True
        for cmd in ("M400",) + cmds + ("M400",):
            status &= self.do(cmd, timeout)
            if not status:
                break
        return status

    # change speed (mm min^-1)
    def speed(self, value):
        # shapeoko doesn't like it when the
        # speed is over 9000! (no, really)
        self._speed = min(9000, value)

    # calibrate axes
    def home(self, *axes, timeout=30):
        cmd = "G28 %s" % ''.join(axes)
        return self.do(cmd, timeout)

    # move head
    def move(self, x=None, y=None, z=None, timeout=30):
        symbols = ['X', 'Y', 'Z', 'F']
        params = [x, y, z, self._speed]
        args = ' '.join('%c%f' % (symbol,param) for symbol,param in
                    zip(symbols,params) if param is not None)
        return self.do_wait("G1 %s" % args, timeout)

if __name__ == '__main__':
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
            """  load [serial]
                     Load a shapeoko.
                         [serial] - Connect to the file /dev/serial/by-id/[serial] """
            self.do_close()
            try:
                self.shap = Shapeoko("/dev/serial/by-id/"+str(port), verbose=True)
            except Exception as e:
                print("*** Error opening device: %s" % e)

        def complete_load(self, text, line, begidx, endidx):
            prefix = "/dev/serial/by-id/"
            devices = [a[len(prefix):] for a in glob.glob(preifx + "*")]
            print(devices)
            return [a[begidx:] for a in devices]

        def do_close(self, *args):
            """  close
                     Close the comm channel with the shapeoko"""
            if self.shap is not None:
                del self.shap
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
            Axes = Shapeoko.Axes
            handled = 0
            args = []
            if "x" in axes:
                args.append(Axes.x)
                handled = 1
            if "y" in axes:
                args.append(Axes.y)
                handled = 1
            if "z" in axes:
                args.append(Axes.z)
                handled = 1
            if handled is 0:
                print("*** Usage: home [xyz]")
                return
            print("Homing ", args)
            try:
                self.shap.home(*args)
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
            l = [(float(a) if a is not "-" else None) for a in l]
            print("Moving x=",l[0],", y=",l[1], ", z=", l[2])
            try:
                self.shap.move(l[0] , l[1], l[2])
            except:
                print("*** Error sending move command")

        @serial_cmd
        def do_send(self, code):
            if code.strip() is "":
                print("*** Usage: send [g-code]")
                return
            try:
                self.shap.do(code)
            except:
                print("*** Error sending g-code")

        @serial_cmd
        def do_speed(self, set):
            if set.strip() is "":
                print("*** Usage: speed [speed in mm min^-1]")
                return
            self.shap.speed(float(set))
            print("Set speed to ", set)

        def do_EOF(self, line):
            self.do_close()
            print("*** Bye!")
            return True

        @serial_cmd
        def do_figure(self, *args):
            self.shap.do_seq("G28 XY", "G1 Y40 F%d"%self.shap._speed, "G3 X80 I40", "G2 I40", "G3 X0 I-40")

        def help_figure(self):
            print("figure\n\
    Draw a figure of 8 in an 80x160 box.")

    ShapeokoInterpreter().cmdloop()
 
