import serial
import time

class LEDControl:
    def __init__(self, dev):
        self._ser = serial.Serial(dev, 9600)
        self._ser.write(chr(1))
        self._ser.flush()
        time.sleep(1.5)

    def set_mode(self, mode):
        self._ser.write(chr(int(mode)))
        self._ser.flush()

    def get_mode(self):
        self._ser.write('A')
        self._ser.flush()
        return ord(self._ser.read())

    def toggle(self):
        self.set_mode(int(self.get_mode()) + 1)

if __name__ == '__main__':
    import cmd
    import glob

    class LEDInterpreter(cmd.Cmd):
        """Nice shell for controlling the LEDs and hence microscope operating modes"""

        prompt = 'QuickScope# '
        def __init__(self):
            cmd.Cmd.__init__(self)
            self.led = None

        def emptyline(self):
            pass

        def do_load(self, port):
            """  load [serial]
                     Load an led board.
                         [serial] - Connect to the file /dev/serial/by-id/[serial] """
            self.do_close()
            if port is "":
                port = "usb-Arduino__www.arduino.cc__0043_5543434383335181A060-if00"
            try:
                self.led = LEDControl("/dev/serial/by-id/"+str(port))
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
                     Close the comm channel with the LED control board"""
            if self.led is not None:
                del self.led
                self.led = None
                print("Closed already open comm channel...")

        def do_EOF(self, line):
            self.do_close()
            print("*** Bye!")
            return True

        def serial_cmd(method):
            def checked_cmd(self, *args):
                if self.led is None:
                    print("*** Load a led board first! [load <n>] where n is the ttyACM number")
                    return
                return method(self, *args)
            return checked_cmd

        @serial_cmd
        def do_set(self, mode):
            self.led.set_mode(int(mode))

        @serial_cmd
        def do_blink(self, line):
            while True:
                time.sleep(1)
                self.led.toggle()

        @serial_cmd
        def do_toggle(self, line):
            self.led.toggle()

        @serial_cmd
        def do_get(self, line):
            print("Mode: %s" % str(self.led.get_mode()))

    LEDInterpreter().cmdloop()
