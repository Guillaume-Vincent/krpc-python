"""Quick python script designed to run every mission one by one."""

import krpc
from time import sleep
from toolkit.ui import Panel


def setUpPanel(missionNumber):
    """Create a panel to display text and buttons."""
    # Panel Settings
    panelSize = (500, 250)
    panelPosition = (0, 250)
    defaultTextSize = 20
    defaultSpacing = 25
    title = 'Mission Control'
    titleSize = 50

    # Panel Creation
    MC = Panel(conn, panelSize, panelPosition, defaultTextSize,
               defaultSpacing, title, titleSize)
    MC.panel.rect_transform.position = (
        -MC.canvas.rect_transform.size[0]/2+panelSize[0]/2,
        MC.canvas.rect_transform.size[1]/2-panelSize[1]/2-50)

    # Add line of text
    MC.addLine("ESS-0" + str(missionNumber) + " on the launchpad ?")

    # Add check button
    button1Size = (80, 1.6*MC.defaultTextSize)
    button1Pos = (80, MC.firstLinePos - MC.lineCount*MC.defaultTextSize - MC.lineCount*MC.defaultSpacing)
    MC.addButton("Button1", "CHECK", button1Size, button1Pos)

    # Wait for check button to be clicked
    button1 = MC.buttons["Button1"]
    button1.text.color = (0.8, 0, 0)
    check1Status = conn.add_stream(getattr, button1, 'clicked')
    while check1Status() is False:
        pass
    check1Status.remove()
    button1.text.color = (0, 0.8, 0)

    # Add launch button
    button2Size = (MC.panel.rect_transform.size[0]/2, 80)
    button2Pos = (0, -MC.panel.rect_transform.size[1]/4)
    MC.addButton("Button2", "LAUNCH", button2Size, button2Pos)

    # Wait for launch button to be clicked
    button2 = MC.buttons["Button2"]
    button2.text.color = (0.8, 0, 0)
    check2Status = conn.add_stream(getattr, button2, 'clicked')
    while check2Status() is False:
        pass
    check2Status.remove()
    button2.text.color = (0, 0.8, 0)

    # Remove panel
    MC.remove()


conn = krpc.connect(name="Mission Control")

for missionNumber in range(1, 8):  # 7 vessels to launch
    setUpPanel(missionNumber)
    sleep(1)
    if missionNumber == 1:
        exec(open("ESS-01.py").read())
    else:
        exec(open("ESS-02.py").read())
