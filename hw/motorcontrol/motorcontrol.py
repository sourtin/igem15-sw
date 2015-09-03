#!/usr/bin/env python3
import serial
import time


# such a hacky fix, todo: rewrite motors code
class MotorControl:
    def __init__(self, dev):
        self.dev = dev
        self._ser = serial.Serial(dev, 9600)

    def wait_for_fin(self):
        while True:
            line = self._ser.readline()
            try:
                if len(line) and "fin" in line:
                    return
            except:
                pass

    def move(self, x, y, z):
        if x is not None:
            self._move(0, int(x))
        if y is not None:
            self._move(1, int(y))
        if z is not None:
            self._move(2, int(z))

    def _move(self, axis, amount):
#        print('m%d%s%dg' % (axis, "+" if amount > 0 else "", amount))
        self._ser.write(('m%d%s%dg' % (axis, "+" if amount > 0 else "", amount)).encode())
        self._ser.flush()
        self.wait_for_fin()
        del self._ser
        self._ser = serial.Serial(self.dev, 9600)
#        time.sleep(1)

    def close(self):
        self._ser.close()

if __name__ == '__main__':
    import cmd
    import glob

    class MotorInterpreter(cmd.Cmd):
        """Nice shell for controlling the motors"""

        prompt = 'MovingQuickScope# '
        def __init__(self):
            cmd.Cmd.__init__(self)
            self.mot = None

        def emptyline(self):
            pass

        def do_load(self, port):
            """  load [serial]
                     Load an motor board.
                         [serial] - Connect to the file /dev/serial/by-id/[serial] """
            self.do_close()
            if port is "":
                port = "usb-Arduino__www.arduino.cc__0043_55434343833351813261-if00"
            try:
                self.mot = MotorControl("/dev/serial/by-id/"+str(port))
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
                     Close the comm channel with the motor control board"""
            if self.mot is not None:
                del self.mot
                self.mot = None
                print("Closed already open comm channel...")

        def do_EOF(self, line):
            self.do_close()
            print("*** Bye!")
            return True

        def serial_cmd(method):
            def checked_cmd(self, *args):
                if self.mot is None:
                    print("*** Load a motor board first! [load <n>] where n is the ttyACM number")
                    return
                return method(self, *args)
            return checked_cmd

        @serial_cmd
        def do_move(self, line):
            l = line.split()
            if(len(l) < 3):
                print("*** Usage: move x y z (Use - for no movement on an axis)")
                return
            l = [(int(a) if a is not "-" else None) for a in l]
            self.mot.move(l[0], l[1], l[2])
            pass

    MotorInterpreter().cmdloop()
