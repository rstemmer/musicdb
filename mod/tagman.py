# MusicDB,  a music manager with web-bases UI that focus on music.
# Copyright (C) 2017  Ralf Stemmer <ralf.stemmer@gmx.net>
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
This command runs a command line "GUI" to manage tags.
Press ``Ctrl-D`` to exit the tag manager.

Example:

    .. code-block:: bash

        musicdb -q tagman 
        # -q: do not show logs on stdout
"""

import argparse
from lib.modapi         import MDBModule
from lib.db.musicdb     import MusicDatabase
from lib.filesystem     import Filesystem
from mdbapi.tags        import MusicDBTags
from lib.clui.listview  import ListView
from lib.clui.text      import Text
from lib.clui.pane      import Pane
from lib.clui.dialog    import Dialog
from lib.clui.textinput import TextInput
from lib.clui.boolinput import BoolInput
from lib.clui.buttonview import ButtonView
from lib.clui.tabgroup  import TabGroup

class GenreView(ListView, MusicDBTags):
    def __init__(self, config, database, title, x, y, w, h):
        ListView.__init__(self, title, x, y, w, h)
        MusicDBTags.__init__(self, config, database)
        self.UpdateView()

        self.dialog     = Dialog("Edit Genre", self.x, self.y+1, self.w, self.h-1)
        self.dialogmode = False
        self.nameinput  = TextInput()
        self.dialog.AddInput("Name:",  self.nameinput, "Visibly for user")


    def UpdateView(self):
        self.SetData(self.GetAllGenres())


    def Draw(self):
        # Only draw the list view when not in dialog mode
        if self.dialogmode == False:
            ListView.Draw(self)


    def onDrawElement(self, element, number, maxwidth):
        string = element["name"]
        string = string[:maxwidth]
        string = string.ljust(maxwidth)
        return string


    def onAction(self, element, key):
        if key == "e":      # Edit tag
            name = element["name"]

            # Initialize dialog with element
            self.nameinput.SetData(name)

            # show dialog
            self.dialog.oldname = name # trace Tag so that changes can be associated to a specific tag
            self.dialog.Draw()
            self.dialogmode = True

        elif key == "r":    # Remove Tag
            self.DeleteGenre(element["name"])
            self.elements.remove(element)
            self.UpdateView()
            self.Draw()
            return None

        return element


    def HandleKey(self, key):
        if self.dialogmode == True:
            if key == "enter":  # Commit dialog inputs
                self.dialogmode = False
                self.Draw() # show list view instead of dialog

                # Get data from dialog
                name = self.nameinput.GetData()
                oldname = self.dialog.oldname

                # Update database with new data
                if oldname == None:
                    self.CreateGenre(name)
                    tagname = name
                    newname = None
                else:
                    tagname = oldname
                    # Was the tag renamed?
                    if oldname != name:
                        newname = name
                    else:
                        newname = None

                self.ModifyGenre(tagname, newname)
                self.UpdateView()
                self.Draw()


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
                self.dialog.oldname = None    # new tag has no old name
                self.dialog.Draw()
                self.dialogmode = True
            else:
                ListView.HandleKey(self, key)



class SubGenreView(ListView, MusicDBTags):
    def __init__(self, config, database, genreview, title, x, y, w, h):
        ListView.__init__(self, title, x, y, w, h)
        MusicDBTags.__init__(self, config, database)

        if type(genreview) != GenreView:
            raise TypeError("genreview must be of type GenreView!")
        self.genreview = genreview
        self.UpdateView()

        self.dialog     = Dialog("Edit Subgenre", self.x, self.y+1, self.w, self.h-1)
        self.dialogmode = False
        self.nameinput  = TextInput()
        self.dialog.AddInput("Name:",  self.nameinput, "Visibly for user")


    def UpdateView(self):
        self.SetData(self.GetAllSubgenres())


    def Draw(self):
        # Only draw the list view when not in dialog mode
        if self.dialogmode == False:
            ListView.Draw(self)


    def onDrawElement(self, element, number, maxwidth):
        genre  = self.genreview.GetSelectedData()
        if element["parentid"] == genre["id"]:
            color = "\033[1;34m"
        else:
            color = "\033[1;30m"
        string = element["name"]
        string = string[:maxwidth]
        string = string.ljust(maxwidth)
        return color + string


    def onAction(self, element, key):
        if key == "e":      # Edit tag
            name = element["name"]

            # Initialize dialog with element
            self.nameinput.SetData(name)

            # show dialog
            parent     = self.genreview.GetSelectedData()
            parentname = parent["name"]

            self.dialog.oldname    = name # trace Tag so that changes can be associated to a specific tag
            self.dialog.parentname = parentname
            self.dialog.Draw()
            self.dialogmode = True

        elif key == "r":    # Remove Tag
            self.DeleteSubgenre(element["name"])
            self.elements.remove(element)
            self.UpdateView()
            self.Draw()
            return None

        return element


    def HandleKey(self, key):
        if self.dialogmode == True:
            if key == "enter":  # Commit dialog inputs
                self.dialogmode = False
                self.Draw() # show list view instead of dialog

                # Get data from dialog
                name       = self.nameinput.GetData()
                oldname    = self.dialog.oldname
                parentname = self.dialog.parentname

                # Update database with new data
                if oldname == None:
                    self.CreateSubgenre(name, parentname)
                    tagname = name
                    newname = None
                else:
                    tagname = oldname
                    # Was the tag renamed?
                    if oldname != name:
                        newname = name
                    else:
                        newname = None

                self.ModifySubgenre(tagname, newname)
                self.UpdateView()
                self.Draw()


            elif key == "escape":
                self.dialogmode        = False
                self.dialog.oldname    = None  # prevent errors by leaving a clean state
                self.dialog.parentname = None
                self.Draw() # show list view instead of dialog
                # reject changes

            else:
                self.dialog.HandleKey(key)
        else:
            if key == "a":
                # Add new tag
                self.nameinput.SetData("")

                parent     = self.genreview.GetSelectedData()
                parentname = parent["name"]

                self.dialog.oldname    = None    # new tag has no old name
                self.dialog.parentname = parentname
                self.dialog.Draw()
                self.dialogmode = True
            else:
                ListView.HandleKey(self, key)



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
        self.varselector= BoolInput()
        self.dialog.AddInput("Name:",  self.nameinput,   "Visibly for user")
        self.dialog.AddInput("Icon:",  self.iconinput,   "Unicode char")
        self.dialog.AddInput("U+FE0E:",self.varselector, "Do not replace with emoji")
        self.dialog.AddInput("Color:", self.colorinput,  "In HTML notation (#RRGGBB)")


    def UpdateView(self):
        self.SetData(self.GetAllMoods())


    def onDrawElement(self, element, number, maxwidth):
        if element["icontype"] == 1:    # unicode icon
            icon = element["icon"]
        else:
            icon = "?"

        if element["color"]:
            r = int(element["color"][1:3], 16)
            g = int(element["color"][3:5], 16)
            b = int(element["color"][5:7], 16)
        else:
            r = int("CC", 16)
            g = int("CC", 16)
            b = int("CC", 16)

        color = "\033[38;2;%d;%d;%dm"%(r,g,b)

        debug = " " + str(len(icon)) + " " + str(icon.encode())

        # there may be a modifier "\xef\xb8\x8e" at the end to prevent some silly browser
        #  to replace the Unicode characters with ugly emoji images that totally fuck up the design
        if len(icon) > 1:
            icon = icon[0]

        #string = "[" + icon + "] " + element["name"]
        name = element["name"]
        name = name[:maxwidth-2]
        name = name.ljust(maxwidth-2)
        return color + icon + " \033[1;34m" + name


    def Draw(self):
        # Only draw the list view when not in dialog mode
        if self.dialogmode == False:
            ListView.Draw(self)


    def onAction(self, element, key):
        if key == "e":      # Edit tag
            name = element["name"]

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

            # show dialog
            self.dialog.oldname = element["name"] # trace Tag so that changes can be associated to a specific tag
            self.dialog.Draw()
            self.dialogmode = True

        elif key == "r":    # Remove Tag
            self.DeleteMood(element["name"])
            self.elements.remove(element)
            self.UpdateView()
            self.Draw()
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

                self.ModifyMood(tagname, newname, icon, color)
                self.UpdateView()
                self.Draw()


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




class tagman(MDBModule):
    def __init__(self, config, database):
        MDBModule.__init__(self)

        self.db  = database
        self.cfg = config


    @staticmethod
    def MDBM_CreateArgumentParser(parserset, modulename):
        parser = parserset.add_parser(modulename, help="Manage tags using a CLI GUI")
        parser.set_defaults(module=modulename)
        return parser


    def ShowUI(self):
        cli  = Text()
        cli.ShowCursor(False)
        cli.ClearScreen()
        cli.SetCursor(1, 1)
        cli.SetColor("1;30", "40")
        cli.PrintText("New sub genre belong to selected main genre.  Ctrl-D to exit.")

        maxw, maxh = cli.GetScreenSize()

        # The GUI must have three lists: main genre, sub genre, mood
        # main and sub genre shall be encapsulated by a frame
        listwidth   = (maxw - 2) // 3           # -2 for the extra frame, /3 for three lists
        framewidth  = listwidth * 2 + 2
        listystart  = 3
        listheight  = maxh - (listystart + 3)   # +3 for a ButtonView
        list1xstart = 1
        list2xstart = 1 + listwidth
        list3xstart = 2 + 2*listwidth
        framexstart = list1xstart - 1

        # Add spaces between the frames
        spacewidth   = 1
        framexstart += spacewidth       # space before
        framewidth  -= spacewidth * 2   # space around
        list1xstart += spacewidth * 2   # screen<->frame + frame<->list1
        list2xstart += spacewidth * 1   # list1<->list2
        list3xstart += spacewidth * 1   # 
        listwidth   -= spacewidth * 3

        # List Views
        self.genreview    = GenreView   (self.cfg, self.db, 
                "Main Genre", list1xstart, listystart, listwidth, listheight)
        self.subgenreview = SubGenreView(self.cfg, self.db, self.genreview, 
                "Sub Genre",  list2xstart, listystart, listwidth, listheight)
        self.moodview     = MoodView    (self.cfg, self.db, 
                "Moods",      list3xstart, listystart, listwidth, listheight)

        # Frame
        self.genreframe = Pane("Genre", framexstart, listystart-1, framewidth, listheight+2)
        self.genreframe.SetFGColor("0;31")

        # Buttons
        self.buttons = ButtonView(align="middle")
        self.buttons.AddButton("a", "Add new tag")
        self.buttons.AddButton("e", "Edit tag")
        self.buttons.AddButton("m", "Arrange tags")
        self.buttons.AddButton("r", "Remove tag")
        self.buttons.AddButton("↹", "Select next tag list")

        # Composition
        tabgroup = TabGroup()
        tabgroup.AddPane(self.genreview)
        tabgroup.AddPane(self.subgenreview)
        tabgroup.AddPane(self.moodview)

        # Draw once
        self.genreframe.Draw()
        self.buttons.Draw(0, maxh-2, maxw)

        key = " "
        while key != "Ctrl-D":
            # Show everything
            self.genreview.Draw()
            self.subgenreview.Draw()
            self.moodview.Draw()
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
        return 0

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

