import krpc

class Panel:
    """Create a panel and its components.

    Can add text to the panel.
    """
    def __init__(self, conn, panelSize, panelPosition,
                 defaultTextSize, defaultSpacing, title, titleSize):
        #Create the canvas and the panel
        self.canvas = conn.ui.add_canvas()
        self.panel = self.canvas.add_panel()

        #Initialise the panel szie and position
        self.panel.rect_transform.size = panelSize
        self.panel.rect_transform.position = panelPosition
        self.panelSize = panelSize

        #Regroup all the elements (text, buttons, ...) of the panel
        self.elements = []

        #Write the main title of the panel
        self.ui = conn.ui
        self.addText(line=title, size=titleSize,
                     position=(0,panelSize[1]/2 - titleSize/2))

        #Use a lineCount to count the number of lines writen in the panel.
        #Main title doesn't count as a line.
        self.lineCount = 0

        #Default size for  lines of text & vertical position of first line.
        self.defaultTextSize = defaultTextSize
        self.defaultSpacing = defaultSpacing
        self.firstLinePos = (self.panelSize[1] - 100)/2 - defaultTextSize/2

    def addText(self, line, size, anchor="middle_center", color=(0,0,0),
                font='Corbel Bold', position=(0,0)):
        text = self.panel.add_text(line)
        self.elements.append(text)

        if anchor == "middle_left":
            anchor = self.ui.TextAnchor.middle_left
        elif anchor == "middle_right":
            anchor = self.ui.TextAnchor.middle_right
        elif anchor == "middle_center":
            anchor = self.ui.TextAnchor.middle_center
        else:
            print("Invalid anchor name !")
            exit(0)

        text.rect_transform.position = position
        text.rect_transform.size = (4 * self.panelSize[0]/5,size)
        text.alignment = anchor
        text.font = font
        text.size = size
        text.color = tuple([c/255 for c in color])

    def addLine(self, line, color=(0,0,0)):
        self.lineCount += 1
        linePos = (0,self.firstLinePos - self.lineCount*self.defaultTextSize -\
                   self.lineCount*self.defaultSpacing)
        self.addText(line, size=self.defaultTextSize, anchor="middle_left",
                     position=linePos)

    def remove(self):
        self.panel.remove()
        self.canvas.remove()
        for elem in self.elements:
            elem.remove()

conn = krpc.connect(address='192.168.1.27')
vessel = conn.space_center.active_vessel
exitCondition = conn.add_stream(getattr,vessel.control,'throttle')

mainMenu = Panel(conn, (500,750), (0,0), 20, 25, 'Main Menu', 50)
for n in range(0,15):
    mainMenu.addLine("Hello, this is line n°" + str(n+1))

while exitCondition() == 0.0:
    pass

mainMenu.remove()
