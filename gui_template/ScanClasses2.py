from Tkinter import *
from abc import abstractmethod, ABCMeta

TITLE_FONT = ("Helvetica", 18, "bold")

#class ScanMethod [Frame):
#    @abstractmethod
 #   def scan(self):
 #       #do somehting
 #       pass

#================SCAN=CLASSES================================#

class MarchantiaScan(Frame):

    def __init__(self, parent):
        Frame.__init__(self, parent)

        titleLabel = Label(self, text = "Marchantia Scan", font = TITLE_FONT)
        titleLabel.grid(row = 0, column = 0, columnspan = 3)

        button1 = Button(self, text = "Scan")
        button1.grid(row = 1, column = 0)

        button2 = Button(self, text = "Get old scan")
        button2.grid(row = 1, column = 1)

        button3 = Button(self, text = "Another Button")
        button3.grid(row = 1, column = 2)

class FluorescenceScan(Frame):

    def __init__(self, parent):
        Frame.__init__(self, parent)
        titleLabel = Label(self, text = "Fluorescence Scan", font = TITLE_FONT)
        titleLabel.grid(row = 0, column = 0, columnspan = 3)

        button1 = Button(self, text = "Scan")
        button1.grid(row = 1, column = 0)

        button2 = Button(self, text = "Get old scan")
        button2.grid(row = 1, column = 1)

class ColonyScan(Frame):

    def __init__(self, parent):
        Frame.__init__(self, parent)
        titleLabel = Label(self, text = "Colony Scan", font = TITLE_FONT)
        titleLabel.grid(row = 0, column = 0, columnspan = 3)

        button1 = Button(self, text = "Scan")
        button1.grid(row = 1, column = 0)

        button2 = Button(self, text = "Get old scan")
        button2.grid(row = 1, column = 1)
