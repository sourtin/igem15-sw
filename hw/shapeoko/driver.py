#!/usr/bin/env python3
import re
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

    def __init__(self, device, rate=115200, speed=9000, verbose=False, autocalibrate=False):
        self.device = device
        self.rate = rate
        self._speed = speed
        self.verbose = verbose
        self.autocalibrate = autocalibrate
        self.last = None

        self.queue = queue.Queue()
        self.thread = threading.Thread(target=self.main)
        self.thread.daemon = True
        self.thread.start()
        self._com = None

    def main(self):
        SerialException = serial.serialutil.SerialException
        while True:
            try:
                with serial.Serial(self.device, self.rate, timeout=1) as com:
                    self._com = com
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

        prequeue = queue.Queue()
        if self.autocalibrate:
            prequeue.put(("G28 XYZ", threading.Event(), [False], 30))
            if self.last:
                pos = "X{x:f} Y{y:f} Z{z:f} F8000".format(**self.last)
                prequeue.put(("G1 %s" % pos, threading.Event(), [False], 30))

        while com.isOpen():
            q = self.queue if prequeue.empty() else prequeue

            try:
                cmd, event, status, timeout = q.get(True, 1)
            except queue.Empty:
                while True:
                    line = com.readline()
                    try:
                        if len(line) and self.verbose:
                            print(line[:-1].decode())
                        elif not len(line):
                            break
                    except:
                        pass
                continue

            try:
                com.write(("%s\r\n" % cmd).encode())
                com.flush()
                if self.verbose:
                    print("Sent: %s" % cmd)

                beginning = time.time()
                while True:
                    line = com.readline()

                    # verbose logging and command stati
                    try:
                        msg = line[:-1].decode()
                        if len(msg) and self.verbose:
                            print(msg)
                        status[1].append(msg)
                    except:
                        pass

                    # command complete
                    if line[:2] == b'ok':
                        status[0] = True
                        break

                    # command timed out
                    if time.time() > beginning + timeout:
                        break
            finally:
                q.task_done()
                event.set()

    # do command and block until ok
    def do(self, cmd, timeout=30, nopos=False):
        status = [False]
        event = threading.Event()
        self.queue.put((cmd, event, status, timeout))
        event.wait(timeout)

        if not nopos and self.autocalibrate:
            self.last = self.position()

        return status[0]

    # block on command until complete
    def do_wait(self, cmd, timeout=30, nopos=False):
        beginning = time.time()
        status = self.do(cmd, timeout, nopos=nopos)
        self.wait(beginning + timeout - time.time())
        return status

    # return command information
    def do_get(self, cmd, timeout=30, nopos=False):
        status = [False, []]
        event = threading.Event()
        self.queue.put((cmd, event, status, timeout))
        event.wait(timeout)
        self.wait(timeout)

        if not nopos and self.autocalibrate:
            self.last = self.position()

        return status[0], status[1]

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

    # read current stepper-estimated position
    def position(self, timeout=30, count=False):
        status, data = self.do_get("M114", timeout, nopos=True)
        def parse(line):
            try:
                a, b = line.lower().split('count')
                pattern = re.compile(r"([a-z]):\s*([-+]?[0-9]+\.[0-9]+)")
                matches = re.findall(pattern, b if count else a)
                return dict((axis, float(pos)) for axis,pos in matches)
            except:
                return None
        parsed = [p for p in map(parse, data) if p is not None]
        return parsed[-1] if len(parsed) else {}

    def wait(self, timeout=30):
        return self.do("M400", nopos=True)

    def kill(self):
        try:
            for _ in range(3):
                print("EMERGENCY STOP!!!")
                self._com.write(b'M112\r\n')
                self._com.flush()
                time.sleep(1)
        finally:
            os._exit(1)


if __name__ == '__main__':
    import cmd
    import glob
    import signal

    class ShapeokoInterpreter(cmd.Cmd):
        prompt = 'Shapeoko# '
        def __init__(self):
            cmd.Cmd.__init__(self)
            self.shap = None
            signal.signal(signal.SIGINT, self.do_kill)

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
            devices = [a[len(prefix):] for a in glob.glob(prefix + "*")]
            beg = line.partition(' ')[2].strip()
            off = len(beg) - len(text)
            return [a[off:] for a in devices if a.startswith(beg)]

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

        @serial_cmd
        def do_pos(self, *args):
            pos = self.shap.position()
            print(pos)

        @serial_cmd
        def do_kill(self, *args):
            self.shap.kill()

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
 
