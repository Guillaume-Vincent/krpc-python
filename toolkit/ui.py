import krpc

class Panel:
    """Define a panel and its components.

    """
    def __init__(self, conn, panelSize, panelPosition, panelName):
        self.panelSize = panelSize
        self.panelPosition = panelPosition
        self.panelName = panelName

        self.canvas = conn.ui.add_canvas()
        self.panel = self.canvas.add_panel()
        self.elements = []

        self.panel.rect_transform.size = self.panelSize
        self.panel.rect_transform.position = self.panelPosition

    def addLine(self, line, color=(0,0,0), size=20, font='Corbel Bold',
                position=(0,0),anchor='middle_center',style='normal'):
        text = self.panel.add_text(line)
        self.elements.append(text)

        text.rect_transform.position = position
        text.rect_transform.size = size
        text.font = font
        text.size = size
        text.style = style
        text.color = tuple([c/256 for c in color])

    def remove(self):
        self.panel.remove()
        self.canvas.remove()
        for elem in self.elements:
            elem.remove()

def mainMenuUI(conn):
    """Create the UI of the main menu.

    """
    mainMenu = Panel(conn, (500,750), (0,0), 'Main Menu')

conn = krpc.connect(address='192.168.1.27')
vessel = conn.space_center.active_vessel
exitCondition = conn.add_stream(getattr,vessel.control,'throttle')

UI = mainMenuUI(conn)

while exitCondition() == 0.0:
    pass

for elem in UI:
    elem.remove()
