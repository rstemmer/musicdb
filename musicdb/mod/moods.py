# MusicDB,  a music manager with web-bases UI that focus on music.
# Copyright (C) 2017-2021  Ralf Stemmer <ralf.stemmer@gmx.net>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
The command ``musicdb moods`` runs a command line "GUI" to manage mood-tags.
Every change gets write to the database immediately.
Press ``Ctrl-D`` to exit the tag manager.

Moods are tags that are designed to annotate moods and feelings to songs.
The implementation is pretty general so that they can be used to annotate any kind of information to a song.
Only restriction is, that they can be represented with "one single" (after rendering) Unicode character.

After executing ``musicdb moods`` the UI shown on the following screenshot appears:

.. figure:: ../images/moods.png

In that form, Mood flags are represented as 
list (explained in the `Mood List`_ section) and as 
grid (explained in the `Mood Grid`_ section).
You can switch between those representations using the tab key (↹).


Mood List
---------

The Mood List show all moods in the database.
The first column is the icon and color assigned to the mood.
Next column is the name of that mood.
On the right side are the coordinates of the moods in the `Mood Grid`_ and the type of the icon.
Currently, only Unicode icons (txt) are implemented.

In the Mood List pane you can add, edit or remove mood tag.
When you add or edit a flag, the dialog shown on the next screenshot appears.

.. figure:: ../images/moods-edit.png

The input forms can be accessed using the arrow keys ↑ and ↓.
The inputs have the following meanings:

    Name:
        Name of the tag. This will be visible to the user via tool tips.
        This name should be short but meaningful.

    Icon:
        An Unicode icon.
        This can be any printable Unicode character.
        It can also be extended with combining characters.
        This value gets stored as string.
        As long as it will be rendered as a single character, everything is fine.

    U+FE0E:
        If this checkbox is set, the Unicode character *VARIATION SELECTOR-15* gets append to the icon.
        This forces the software that displays the icon (In this case the web browser or shell) to use the
        text representation of the Unicode character and not replace it with a "fancy" image.
        Set this flag in case a browser or shell you use does this.
        The problem with replacing the character by an Image is, that it destroys the color scheme of the Web UI.

    Color:
        Here you can specify a color to highlight an Icon.
        This should only be done in exceptional cases.
        To color must start with a hash (#) followed by a two hexadecimal number for the red value, then the green value, then blue.
        For example ("#0080FF") is 0% red, 50% green and 100% blue.
        Most color wheels have a HTML color representation.
        So for choosing a color you can use for example *GIMP*.
        Forcing an icon to not follow the color scheme of the Web UI can lead to ugly side effects.
        Just imagine you have a red heart icon on a red background.
        The excessive use of explicit colors in the example shown on the screenshot is how *not* to use this feature ;)
        
    X/Y:
        This is the position in the `Mood Grid`_. Details are explained below.
        When you add a new Icon, you must give it some initial values.
        They can be anywhere in the grid where no other icon is.
        You should not exceed 2 lines (so only ``y=0`` and ``y=1`` should be used).

Pressing enter (↵) writes the changes to the database.
Pressing escape twice rejects the changes.


Mood Grid
---------

The Mood Grid helps you to arrange the mood tags in a grid.
This is the same grid used in the WebUI to show the tags in the HUD as shown on the screenshot below, upper part.
Furthermore you can see, that in the WebUI, the color gets not used inside the mood grid in the HUD.
When a mood gets assigned to a song, than the icon is visible on the right part of the song entry in the Album View (bottom part of the screenshot).
There, the icons color will be used to highlight special flags.

.. figure:: ../images/moods-webui.png

You can use the arrow keys (↑↓←→) to move the rectangle around the icons in the Mood Gird.
When pressing space, the rectangle changes to arrows and + signs (See following screenshot) and you can mode the icon itself.

.. figure:: ../images/mood-grid.png

As you can see on the screenshot, you can exchange the positions of the sun with the heart by pressing ← or snow flake by pressing ↑.
When you press → a new column gets added to the grid.
The sun icon will then be placed in the next column.
When there are columns on the left or right that are not used, they get removed automatically.
Not each cell of the grid needs to have an icon.
Feel free to place the icons to intuitive places.


Style Guide
-----------

    * Only use colors in exceptional cases.
    * Give meaningful but short names.
    * Arrange icons to intuitive places.
    * Do not add too much mood tags. (It should not exceed 8 or 10 max)

"""

import argparse
from musicdb.lib.modapi         import MDBModule
from musicdb.lib.db.musicdb     import MusicDatabase
from musicdb.lib.filesystem     import Filesystem
from musicdb.lib.namedpipe      import NamedPipe
from musicdb.mdbapi.tags        import MusicDBTags
from musicdb.lib.clui.listview  import ListView
from musicdb.lib.clui.text      import Text
from musicdb.lib.clui.pane      import Pane
from musicdb.lib.clui.dialog    import Dialog
from musicdb.lib.clui.textinput import TextInput
from musicdb.lib.clui.boolinput import BoolInput
from musicdb.lib.clui.buttonview import ButtonView
from musicdb.lib.clui.tabgroup  import TabGroup


def HTMLColorToANSI(htmlcolor):
    r = int(htmlcolor[1:3], 16)
    g = int(htmlcolor[3:5], 16)
    b = int(htmlcolor[5:7], 16)
    return "\033[38;2;%d;%d;%dm"%(r,g,b)



class MoodView(ListView, MusicDBTags):
    def __init__(self, config, database, title, x, y, w, h):
        ListView.__init__(self, title, x, y, w, h)
        MusicDBTags.__init__(self, config, database)

        self.UpdateView()

        self.dialog     = Dialog("Edit Mood", self.x, self.y+1, self.w, self.h-1)
        self.dialogmode = False

        self.nameinput  = TextInput()
        self.iconinput  = TextInput()
        self.colorinput = TextInput()
        self.posxinput  = TextInput()
        self.posyinput  = TextInput()
        self.varselector= BoolInput()
        self.dialog.AddInput("Name:",  self.nameinput,   "Visibly for user")
        self.dialog.AddInput("Icon:",  self.iconinput,   "Unicode char")
        self.dialog.AddInput("U+FE0E:",self.varselector, "Do not replace with emoji")
        self.dialog.AddInput("Color:", self.colorinput,  "In HTML notation (#RRGGBB)")
        self.dialog.AddInput("X:",     self.posxinput,   "X coordinate on grid (positive integer)")
        self.dialog.AddInput("Y:",     self.posyinput,   "X coordinate on grid (positive integer)")

        self.moodgridcrossref=None


    def UpdateView(self):
        self.SetData(self.GetAllMoods())


    def onDrawElement(self, element, number, maxwidth):
        # prints the following information
        # Icon Name Position Type

        width = maxwidth    # trace left width during rendering. Start with maximum

        # Render Icon
        if element["icontype"] == 1:    # unicode icon
            icon = element["icon"]
        else:
            icon = "?"

        # there may be a modifier "\xef\xb8\x8e" at the end to prevent some silly browser
        #  to replace the Unicode characters with ugly emoji images that totally fuck up the design
        if len(icon) > 1:
            icon = icon[0]

        icon  += " "
        width -= 2

        # Render icon type (currently, only type 1 is supported by MusicDB)
        if element["icontype"] == 1:    # Unicode
            icontype = " type:txt"
        elif element["icontype"] == 2:  # HTML tag
            icontype = " type:htm"
        elif element["icontype"] == 3:  # png image
            icontype = " type:png"
        elif element["icontype"] == 4:  # svg graphic
            icontype = " type:svg"

        width -= len(icontype)      

        # Render Icon Color
        if element["color"]:
            color = HTMLColorToANSI(element["color"])
        else:
            color = HTMLColorToANSI("#CCCCCC")

        # Render Position
        posx = element["posx"]
        posy = element["posy"]
        if posx == None:
            posx = "--"
        else:
            posx = "%2d"%(posx)
        if posy == None:
            posy = "--"
        else:
            posy = "%2d"%(posy)

        pos = " (" + posx + ";" + posy + ")"
        width -= len(pos)

        # Render Name
        name = element["name"]
        name = name[:width]
        name = name.ljust(width)
        return color + icon + "\033[1;34m" + name + "\033[1;30m" + pos + icontype


    def Draw(self):
        # Only draw the list view when not in dialog mode
        if self.dialogmode == False:
            ListView.Draw(self)


    def onAction(self, element, key):
        if key == "e":      # Edit tag
            name = element["name"]
            posx = element["posx"]
            posy = element["posy"]

            if element["icon"] == None:
                icon = ""
            else:
                icon = element["icon"][0]

            # Check if variant selector 15 is append to the Unicode character
            if len(element["icon"]) > 1:
                varsec15 = True
            else:
                varsec15 = False

            # Check if there is a color defined
            if element["color"]:
                color = element["color"]
            else:
                color = ""

            # Initialize dialog with element
            self.nameinput.SetData(name)
            self.iconinput.SetData(icon)
            self.varselector.SetData(varsec15)
            self.colorinput.SetData(color)
            self.posxinput.SetData(str(posx))
            self.posyinput.SetData(str(posy))

            # show dialog
            self.dialog.oldname = element["name"] # trace Tag so that changes can be associated to a specific tag
            self.dialog.Draw()
            self.dialogmode = True

        elif key == "r":    # Remove Tag
            self.DeleteMood(element["name"])
            self.elements.remove(element)
            self.UpdateView()
            self.Draw()
            # Synchronize new state with mood grid
            self.moodgridcrossref.UpdateView()
            self.moodgridcrossref.Draw()
            return None

        return element


    def HandleKey(self, key):
        if self.dialogmode == True:
            if key == "enter":  # Commit dialog inputs
                self.dialogmode = False
                self.Draw() # show list view instead of dialog

                # Get data from dialog
                name = self.nameinput.GetData()
                icon = self.iconinput.GetData()
                posx = self.posxinput.GetData()
                posy = self.posyinput.GetData()

                try:
                    posx = int(posx)
                    assert posx >= 0
                except:
                    posx = None # do not update an invalid position
                try:
                    posy = int(posy)
                    assert posy >= 0
                except:
                    posy = None # do not update an invalid position

                if self.varselector.GetData() == True:
                    icon += b"\xef\xb8\x8e".decode()
                color = self.colorinput.GetData()

                if len(color) != 7 or color[0] != "#":
                    color = None
                oldname = self.dialog.oldname

                # Update database with new data
                if oldname == None:
                    self.CreateMood(name)
                    tagname = name
                    newname = None
                else:
                    tagname = oldname
                    # Was the tag renamed?
                    if oldname != name:
                        newname = name
                    else:
                        newname = None

                self.ModifyMood(tagname, newname, icon, color, posx, posy)
                self.UpdateView()
                self.Draw()
                # Synchronize new state with mood grid
                self.moodgridcrossref.UpdateView()
                self.moodgridcrossref.Draw()

            elif key == "escape":
                self.dialogmode     = False
                self.dialog.oldname = None  # prevent errors by leaving a clean state
                self.Draw() # show list view instead of dialog
                # reject changes

            else:
                self.dialog.HandleKey(key)
        else:
            if key == "a":
                # Add new tag
                self.nameinput.SetData("")
                self.iconinput.SetData("")
                self.varselector.SetData(False)
                self.colorinput.SetData("")
                self.dialog.oldname = None    # new tag has no old name
                self.dialog.Draw()
                self.dialogmode = True
            else:
                ListView.HandleKey(self, key)


class MoodGrid(Pane, MusicDBTags, ButtonView):
    def __init__(self, config, database, title, x, y, w, h):
        Pane.__init__(self, title, x, y, w, h)
        MusicDBTags.__init__(self, config, database)
        ButtonView.__init__(self, align="center")

        self.AddButton("⁘", "Navigate")
        self.AddButton("↵", "Commit")
        self.AddButton("␣", "Drag Icon")
        self.AddButton("␛", "Cancel")

        self.grid  = {}
        self.gridw = 0
        self.gridh = 0

        self.cursorx = 0
        self.cursory = 0

        self.mode = "select" # select: select an icon; move: move an icon

        self.UpdateView()

        self.moodlistcrossref=None


    def PositionToKey(self, x, y):
        if type(x) != int or type(y) != int:
            return None
        return "%d;%d"%(x,y)

    def SwichtGridElement(self, myx, myy, thatx, thaty):
        mykey   = self.PositionToKey(myx, myy)
        thatkey = self.PositionToKey(thatx, thaty)

        # Create empty entry if the new position has no mood tag assigned
        if not thatkey in self.grid:
            self.grid[thatkey] = {}
        if not mykey in self.grid:
            self.grid[mykey] = {}

        self.grid[mykey], self.grid[thatkey] = self.grid[thatkey], self.grid[mykey]

        # Update positions
        self.grid[thatkey]["posx"] = thatx
        self.grid[thatkey]["posy"] = thaty
        self.grid[mykey]["posx"] = myx
        self.grid[mykey]["posy"] = myy


    def RealignGrid(self):
        # find highest and lowest x position
        offset = 1000
        for key in self.grid:
            cell = self.grid[key]
            
            if not "name" in cell:
                continue    # dead cell

            offset = min(offset, cell["posx"])

        # Remove dead cells and offset
        newgrid  = {}
        newgridw = 0
        for key in self.grid:
            oldcell = self.grid[key]
            if not "name" in oldcell:
                continue

            newcell = dict(oldcell)
            newcell["posx"] -= offset

            newkey = self.PositionToKey(newcell["posx"], newcell["posy"])
            newgridw = max(newgridw, newcell["posx"]+1)
            newgrid[newkey] = newcell

        # Update state
        self.cursorx -= offset   # realign cursor
        self.grid     = newgrid
        self.gridw    = newgridw


    def ExtendGridToRight(self):
        newkey = self.PositionToKey(self.cursorx+1, self.cursory)
        self.grid[newkey] = {}
        self.grid[newkey]["posx"] = self.cursorx+1
        self.grid[newkey]["posy"] = self.cursory+1
        self.gridw += 1

    def ExtendGridToLeft(self):
        newgrid = {}
        for key in self.grid:
            cell    = self.grid[key]

            cell["posx"] += 1   # move cell to right

            newkey = self.PositionToKey(cell["posx"], cell["posy"])
            newgrid[newkey] = cell

        self.grid   = newgrid
        self.gridw += 1


    def UpdateView(self):
        moods = self.GetAllMoods()
        self.grid  = {}
        self.gridw = 0
        self.gridh = 0

        self.cursorx = 0
        self.cursory = 0

        for mood in moods:
            x = mood["posx"]
            y = mood["posy"]
            key = self.PositionToKey(x, y)

            # do not handle moods that don't have a coordinate on the grid
            if key == None:
                continue
            self.grid[key] = mood
            self.gridw     = max(self.gridw, x+1)
            self.gridh     = max(self.gridh, y)
        

    def CommitChanges(self):
        for key in self.grid:
            cell = self.grid[key]
            if not "name" in cell:
                continue

            self.ModifyMood(cell["name"], newposx=cell["posx"], newposy=cell["posy"])


    def Draw(self):
        cellwidth   = 5
        cellheight  = 3
        celloffsetx = cellwidth  // 2 + 1
        celloffsety = cellheight // 2 + 1

        # Clear cells and draw Frame
        self.SetFGColor("1;31")
        Pane.Draw(self)

        for key in self.grid:
            cell = self.grid[key]
            if not "name" in cell:  # this cell is empty - a dummy cell
                continue

            # Collect information
            posx = cell["posx"]
            posy = cell["posy"]

            name = cell["name"]

            if cell["icontype"] == 1:    # unicode icon
                icon = cell["icon"][0]
            else:
                icon = "?"

            if cell["color"]:
                color = HTMLColorToANSI(cell["color"])
            else:
                color = HTMLColorToANSI("#CCCCCC")

            # Calculate position real x;y from posx;posy
            x = self.x + celloffsetx + posx * cellwidth
            y = self.y + celloffsety + posy * cellheight

            # Print
            self.SetCursor(x, y)
            self.PrintText(color+icon)

            # This code segment prevents a heisenbug in Konsole.
            # Without this code, some Unicode characters were not printed at the correct position
            self.SetCursor(x-2, y-1)
            self.PrintText(" ")
            self.SetCursor(x+2, y-1)
            self.PrintText(" ")
            self.SetCursor(x-2, y+1)
            self.PrintText(" ")
            self.SetCursor(x+2, y+1)
            self.PrintText(" ")

        # Print cursor
        x = self.x + celloffsetx + self.cursorx * cellwidth
        y = self.y + celloffsety + self.cursory * cellheight
        distx = celloffsetx - 1
        disty = celloffsety - 1
        self.SetFGColor("1;36")

        if self.mode == "select":
            self.SetCursor(x - distx, y - disty)
            self.PrintText("┌╴")
            self.SetCursor(x + distx-1, y - disty)
            self.PrintText("╶┐")
            self.SetCursor(x - distx, y + disty)
            self.PrintText("└╴")
            self.SetCursor(x + distx-1, y + disty)
            self.PrintText("╶┘")

        elif self.mode == "move":
            if self.cursory > 0:
                self.SetCursor(x, y - disty)
                self.PrintText("↑")
            if self.cursory < self.gridh:
                self.SetCursor(x, y + disty)
                self.PrintText("↓")
            if self.cursorx > 0:
                self.SetCursor(x - distx, y)
                self.PrintText("←")
            else:
                self.SetCursor(x - distx, y)
                self.PrintText("+")
            if self.cursorx < self.gridw-1:
                self.SetCursor(x + distx, y)
                self.PrintText("→")
            else:
                self.SetCursor(x + distx, y)
                self.PrintText("+")

        # Print Buttons
        x = self.x + 1
        y = self.y + self.h - 1
        w = self.w - 2
        ButtonView.Draw(self, x, y, w)



    def HandleKey(self, key):
        if self.mode == "select":
            if key == "up" and self.cursory > 0:
                self.cursory -= 1
            elif key == "down" and self.cursory < self.gridh:
                self.cursory += 1
            elif key == "left" and self.cursorx > 0:
                self.cursorx -= 1
            elif key == "right" and self.cursorx < self.gridw-1:
                self.cursorx += 1
            elif key == " ":
                self.mode = "move"

        elif self.mode == "move":
            if key == "up" and self.cursory > 0:
                self.SwichtGridElement(self.cursorx, self.cursory, self.cursorx, self.cursory-1)
                self.cursory -= 1
                
            elif key == "down" and self.cursory < self.gridh:
                self.SwichtGridElement(self.cursorx, self.cursory, self.cursorx, self.cursory+1)
                self.cursory += 1

            elif key == "left":
                if self.cursorx == 0:
                    self.ExtendGridToLeft()
                    self.SwichtGridElement(self.cursorx+1, self.cursory, self.cursorx, self.cursory)
                else:
                    self.SwichtGridElement(self.cursorx, self.cursory, self.cursorx-1, self.cursory)
                    self.cursorx -= 1

            elif key == "right":
                if self.cursorx == self.gridw-1:
                    self.ExtendGridToRight()
                self.SwichtGridElement(self.cursorx, self.cursory, self.cursorx+1, self.cursory)
                self.cursorx += 1

            elif key == "enter":
                self.mode = "select"
                self.CommitChanges()
                # Synchronize new state with mood list
                self.moodlistcrossref.UpdateView()
                self.moodlistcrossref.Draw()

            elif key == "escape":
                self.mode = "select"
                # reload state from database
                self.UpdateView()

            self.RealignGrid()
            self.Draw()



class moods(MDBModule):
    def __init__(self, config, database):
        MDBModule.__init__(self)

        self.db  = database
        self.cfg = config


    @staticmethod
    def MDBM_CreateArgumentParser(parserset, modulename):
        parser = parserset.add_parser(modulename, help="Manage mood-tags using a CLI GUI")
        parser.set_defaults(module=modulename)
        return parser


    def ShowUI(self):
        cli  = Text()
        cli.ShowCursor(False)
        cli.ClearScreen()
        cli.SetCursor(1, 1)
        cli.SetColor("1;30", "40")
        cli.PrintText("Ctrl-D to exit.")

        maxw, maxh = cli.GetScreenSize()

        # Calculate the positions of the UI elements
        gridx = 1
        gridy = 3
        gridw = maxw - 2            # -2 for some space around
        gridh = 2 + 2*3             # 2 for the frame + 2 rows with height 3
        listx = 1
        listy = gridy + gridh + 1   # start where the grind ends + 1 space
        listw = maxw - 2            # -2 for some space around
        listh = maxh - (listy + 3)  # +3 for the button bar below


        # List Views
        self.moodlist = MoodView(self.cfg, self.db, "Mood list", listx, listy, listw, listh)
        self.moodgrid = MoodGrid(self.cfg, self.db, "Mood grid", gridx, gridy, gridw, gridh)

        self.moodgrid.moodlistcrossref = self.moodlist
        self.moodlist.moodgridcrossref = self.moodgrid

        # Buttons
        self.buttons = ButtonView(align="middle")
        self.buttons.AddButton("a", "Add new tag")
        self.buttons.AddButton("e", "Edit tag")
        self.buttons.AddButton("r", "Remove tag")
        self.buttons.AddButton("↹", "Select view")

        # Composition
        tabgroup = TabGroup()
        tabgroup.AddPane(self.moodlist)
        tabgroup.AddPane(self.moodgrid)

        # Draw once
        self.buttons.Draw(0, maxh-2, maxw)

        key = " "
        while key != "Ctrl-D":
            # Show everything
            self.moodlist.Draw()
            self.moodgrid.Draw()
            cli.FlushScreen()

            # Handle keys
            key = cli.GetKey()
            tabgroup.HandleKey(key)



        cli.ClearScreen()
        cli.SetCursor(0,0)
        cli.ShowCursor(True)
        return


    # return exit-code
    def MDBM_Main(self, args):

        self.ShowUI()

        # Update caches with the new tags
        pipe = NamedPipe(self.cfg.server.fifofile)
        pipe.WriteLine("refresh")

        return 0

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

