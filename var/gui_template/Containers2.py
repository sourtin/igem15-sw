from Tkinter import *
import ScanClasses2 as sc
import ScanClasses2
#================CONTAINER=CLASSES================================#


class ScanContainer(Frame):
    def __init__(self, parent, vars):
        Frame.__init__(self, parent)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._frames = {}

        for x in vars:
            self._frames[x] = eval("sc." + x + "(self)")
            #self._frames[x] = Frame(sc.MarchantiaScan(self))
            self._frames[x].grid(row=0, column=0, sticky="nsew")

        self.showFrame(vars[0])

    def showFrame(self, c):
        '''Show a frame for the given class'''
        self._frames[c].tkraise()

