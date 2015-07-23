#Second GUI test - nicer layout than First test

"""

    Abbreviations:
    Everything starts with a prefix specifying location.
        m = Main
        u = Upper
        b = Bottom
        l = Left
        r = Right
        
        so - ml = Main Left
           - ur = Upper Right
           
    Next, everything is specified by its type
        B = Button
        F = frame
        Rb = Radio button
        Op = Option Menu

    Finally, any further details - e.g.:
        ulFScreen - screening frame in upper left quadrant
        

    var = variable (singular)
    vars = variables (plural)   <-- store of all possible items
    val = value (singular)      <-- currently selected item
    vals = values (plural)

"""

from Tkinter import *
import ScanClasses2 as sc
import Containers2

class App:
    
    def __init__(self, master):
        self.createConstVariables()
        self.createWidgets(master)
        self.initialiseWidgets()
        

    #==============CREATE============================================================================================#
    def createWidgets(self, master):
        #Topmost frame is called the container. It holds everything
        self.mainContainer = Frame(master)
        
        #Inside the container there are two main frames.
        #These are the only frames inside the container
        self.mlF = Frame(self.mainContainer)
        self.mrF = Frame(self.mainContainer)
        
        #Create the Scan and Screen frames to go in the top left and top right of main frames respectively
        self.ulFScan = None
        self.urFScreen = Frame(self.mrF)

        #Create option menus for Scan and Screen in upper left and upper right main frames respectively
        self.ulOpScan = None # will be of type OptionMenu
        self.urOpScreen = None # will be of type OptionMenu


        #Create buttons to switch between Scan and Screen frames
        self.ulBScanGo = None
        self.urBScreenGo = None

        
    #==============INITIALISE========================================================================================#
    def initialiseWidgets(self):
        #Container
        self.mainContainer.pack()

        #Main Frame Left and Right
        rowWidth = 10
        colWidth = 10
        self.mlF.grid(row = 0, column = 0, rowspan = rowWidth, columnspan = colWidth)
        self.mrF.grid(row = 0, column = colWidth, rowspan = rowWidth, columnspan = colWidth)

        #Option Menus for Scan and Screen
        #=======SCAN============#
        self.ulOpScanVal = StringVar()
        self.ulOpScanVal.set(self.ulOpScanVars[0])
        self.ulOpScan = apply(OptionMenu, (self.mlF, self.ulOpScanVal) + tuple(self.ulOpScanVars))
        self.ulOpScan.grid(row = 0, column = 0, columnspan = 2)
        #=======SCREEN==========#
        self.urOpScreenVal = StringVar()
        self.urOpScreenVal.set(self.urOpScreenVars[0])
        self.urOpScreen = apply(OptionMenu, (self.mrF, self.urOpScreenVal) + tuple(self.urOpScreenVars))
        self.urOpScreen.grid(row = 0, column = 0, columnspan = 3, sticky = N)

        #Scan Window container (and thus frames)
        self.ulFScan = Containers2.ScanContainer(self.mlF, self.ulOpScanVars)
        self.ulFScan.grid(row = 1)

        #Go buttons for Scan and Screen frame selection
        self.ulBScanGo = Button(self.mlF, text = "Go!", command = lambda:self.ulFScan.showFrame(self.ulOpScanVal.get()))
        self.ulBScanGo.grid(row = 0, column = 2)
        

    #==============CONSTANTS=========================================================================================#
    def createConstVariables(self):

        #have some sort of method to get all possible variables for this
        self.ulOpScanVars = getScans()
        self.urOpScreenVars = [
            "Screen for gfp",
            "Screen for yfp",
            "Screen for rfp"
        ]

#==================OTHER=METHODS=====================================================================================#

def getScans():
    #get THIS class file
    txtFile = open("C:\\Temporary\\Python Projects\\GUI_SecondTest\\src\\ScanClasses2.py", "r")
    string = txtFile.read()
    lines = string.split("\n")
    lines.reverse()
    output = []
    for l in lines:
        if "class" in l and "(" in l:
            output.append( l[ l.index("class")+6 : l.index("(") ] )

    return output

root = Tk()
root.title("GUI_SECOND_TEST_1")
frame1 = App(root)
root.mainloop()