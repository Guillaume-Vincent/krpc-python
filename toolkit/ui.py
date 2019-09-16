import krpc

def mainMenuUI(conn):
    """Create the UI of the main menu.

    Return all the elements of the UI for future deletion.
    """
    #Create canvas and panel
    canvas = conn.ui.add_canvas()
    panel = canvas.add_panel()

    #Adjust the size of the panel
    rect = panel.rect_transform
    rect.size = (400, 750)

    #All the different lines that will be writen in the panel
    # TODO: Static & dynamic ?
    # TODO: Funcion to better handle text creation
    linesList = ["Main Menu"]

    textList = []
    for line in linesList:
        textList.append(panel.add_text(line))

    textList[0].font = 'Corbel Bold'
    textList[0].color = (0,0,0)
    textList[0].size = 33
    textList[0].alignment = conn.ui.TextAnchor.lower_center
    textList[0].rect_transform.position = (0,rect.size[1]/2-textList[0].size/2)

    return (canvas,panel,textList)

conn = krpc.connect(address='192.168.1.27')
vessel = conn.space_center.active_vessel
exitCondition = conn.add_stream(getattr,vessel.control,'throttle')

UI = mainMenuUI(conn)

while exitCondition() == 0.0:
    pass

for elem in UI:
    elem.remove()
