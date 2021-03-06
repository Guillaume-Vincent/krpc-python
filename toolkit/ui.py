"""Regroup all functions related to creating and managing the in-game UI."""


class Panel:
    """Used to create a panel and its components."""

    def __init__(self, conn, panelSize, panelPosition,
                 defaultTextSize, defaultSpacing, title, titleSize):
        """Set up and create the panel."""
        # Create the canvas and the panel
        self.canvas = conn.ui.add_canvas()
        self.panel = self.canvas.add_panel()

        # Initialise the panel szie and position
        self.panel.rect_transform.size = panelSize
        self.panel.rect_transform.position = panelPosition
        self.panelSize = panelSize

        # Regroup all the elements (text, buttons, ...) of the panel
        self.elements = []

        # Dictionary for the buttons and for the input fields of the panel
        self.buttons = {}
        self.fields = {}

        # Write the main title of the panel
        self.title = title
        self.ui = conn.ui
        self.addText(line=self.title, size=titleSize,
                     position=(0, panelSize[1]/2 - titleSize/2))

        # Use a lineCount to count the number of lines writen in the panel.
        # Main title doesn't count as a line.
        self.lineCount = 0

        # Default size for  lines of text & vertical position of first line.
        self.defaultTextSize = defaultTextSize
        self.defaultSpacing = defaultSpacing
        self.firstLinePos = (self.panelSize[1] - 100)/2 - defaultTextSize/2

    def addText(self, line, size, anchor="middle_center", color=(0, 0, 0),
                font='Corbel Bold', position=(0, 0)):
        """Add a new text element to the panel.

        Args:
        -line : the line of text that is to be added
        -size : the font size used for the text
        -anchor : alignment of the text (default : "middle_center")
        -color : color of the text, RGB values up to 255 (default : (0,0,0))
        -font : font used for the text (default : 'Corbel Bold')
        -position : position of the center of the text zone (default : (0,0))

        """
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
        text.rect_transform.size = (4 * self.panelSize[0]/5, size)
        text.alignment = anchor
        text.font = font
        text.size = size
        text.color = tuple([c/255 for c in color])

    def addButton(self, name, text, size, position):
        """Add a button to the panel.

        Args:
        -name : identifier for the button
        -text : text written inside the button
        -size : size of the button
        -position : position of the button

        """
        button = self.panel.add_button(text)
        self.buttons[name] = button

        button.rect_transform.size = size
        button.rect_transform.position = position

    def addInputField(self, name, size, position):
        """Add an input field to the panel.

        Args:
        -name : identifier for the field
        -size : size of the field
        -position : position of the field

        """
        inputField = self.panel.add_input_field()
        self.fields[name] = inputField

        inputField.rect_transform.size = size
        inputField.rect_transform.position = position

    def addLine(self, line, color=(0, 0, 0)):
        """Add a preformatted line to the panel, below the previous one."""
        self.lineCount += 1

        linePos = self.lineCount*self.defaultTextSize
        linePosOffset = self.lineCount*self.defaultSpacing
        position = (0, self.firstLinePos - linePos - linePosOffset)
        self.addText(line, size=self.defaultTextSize, anchor="middle_left",
                     position=position)

    def remove(self):
        """Remove all the elements created in this class."""
        self.panel.remove()
        self.canvas.remove()
        for elem in self.elements:
            elem.remove()

    def __repr__(self):
        return ("<Panel : " + self.title + ">")
