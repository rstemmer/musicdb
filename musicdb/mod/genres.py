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
Execute ``musicdb genres`` to execute this module.
This command runs a command line "GUI" to manage genre tags.
Every change gets write to the database immediately.
Press ``Ctrl-D`` to exit the tag manager.

Managing Genres
---------------

.. figure:: ../images/genres.png

After calling the *genres* module, the form shown on the screenshot above appears.
There you can add, edit or remove main and sub genres.
On the left side, a list of all available main genres gets shown.
You can move through the list using the arrow keys (← and →).
On the right side, you see a list of sub genres that are associated to the main genre selected in the left list.
You can switch between those lists using the tab key (↹).

Pressing the a-key opens a dialog where you can enter the name of the new genre.
Pressing e opens the same dialog for the selected genre where you can edit its name.
When removing a genre, all relations to songs and that genre gets removed as well.
Be careful removing genres.

Beside the name, you can enter a position as well.
For main genres, the position gets printed in gray color right to the name.

This position indicates where the genre shall appear in lists in the WebUI.
For main genres, it is the *Genre Select* box show in the screenshot below.
Those positions are not mandatory and will be ignored for sub genres anyway.

.. figure:: ../images/genres-box.png


Updating Caches
---------------

Even if with each change the database gets updated, the WebSocket server and client many have outdated caches.
To to propagate the changes on the genres to the server and clients, force an cache update writing ``"refresh"`` into MusicDBs fifo file.
This file can be found in MusicDB's data directory.
The following command line shows how to do this with a default installation setup.

    .. code-block:: bash

        echo "refresh" > /opt/musicdb/data/musicdb.fifo



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


class GenreView(ListView, MusicDBTags):
    def __init__(self, config, database, title, x, y, w, h):
        ListView.__init__(self, title, x, y, w, h)
        MusicDBTags.__init__(self, config, database)
        self.UpdateView()

        self.dialog     = Dialog("Edit Genre", self.x, self.y+1, self.w, self.h-1)
        self.dialogmode = False
        self.nameinput  = TextInput()
        self.posxinput  = TextInput()
        self.dialog.AddInput("Name:",     self.nameinput, "Visibly for user")
        self.dialog.AddInput("Position:", self.posxinput, "Position in WebUI list (positive integer)")


    def UpdateView(self):
        self.SetData(self.GetAllGenres())


    def Draw(self):
        # Only draw the list view when not in dialog mode
        if self.dialogmode == False:
            ListView.Draw(self)


    def onDrawElement(self, element, number, maxwidth):
        # Render Position
        posx = element["posx"]
        posy = element["posy"]
        if posx == None:
            posx = "--"
        else:
            posx = "%2d"%(posx)

        pos    = " (" + posx + ")"

        # Render Name
        width = maxwidth - len(pos)
        name  = element["name"]
        name  = name[:width]
        name  = name.ljust(width)
        return name + "\033[1;30m" + pos


    def onAction(self, element, key):
        if key == "e":      # Edit tag
            name = element["name"]
            posx = element["posx"]

            # Initialize dialog with element
            self.nameinput.SetData(name)
            self.posxinput.SetData(str(posx))

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
                posx = self.posxinput.GetData()
                oldname = self.dialog.oldname

                try:
                    posx = int(posx)
                    assert posx >= 0
                except:
                    posx = None # do not update an invalid position

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

                self.ModifyGenre(tagname, newname, newposx=posx)
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
                self.posxinput.SetData("")
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
        # Only show subgenres of the selected genre
        genre     = self.genreview.GetSelectedData()
        subgenres = self.GetAllSubgenres()
        elements  = [ subgenre for subgenre in subgenres if subgenre["parentid"] == genre["id"] ]

        self.SetData(elements)


    def Draw(self):
        # Only draw the list view when not in dialog mode
        if self.dialogmode == False:
            ListView.Draw(self)


    def onDrawElement(self, element, number, maxwidth):
        name  = element["name"]
        name  = name[:maxwidth]
        name  = name.ljust(maxwidth)
        return name


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



class genres(MDBModule):
    def __init__(self, config, database):
        MDBModule.__init__(self)

        self.db  = database
        self.cfg = config


    @staticmethod
    def MDBM_CreateArgumentParser(parserset, modulename):
        parser = parserset.add_parser(modulename, help="Manage genres using a CLI GUI")
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

        # The GUI must have two lists: main genre, sub genre
        # main and sub genre shall be encapsulated by a frame
        listwidth   = maxw // 2 - 1           # - 1 for some space around
        listystart  = 3
        listheight  = maxh - (listystart + 3)   # +3 for a ButtonView
        list1xstart = 1
        list2xstart = 2 + listwidth

        # List Views
        self.genreview    = GenreView   (self.cfg, self.db, 
                "Main Genre", list1xstart, listystart, listwidth, listheight)
        self.subgenreview = SubGenreView(self.cfg, self.db, self.genreview, 
                "Sub Genre",  list2xstart, listystart, listwidth, listheight)

        # Buttons
        self.buttons = ButtonView(align="middle")
        self.buttons.AddButton("a", "Add new tag")
        self.buttons.AddButton("e", "Edit tag")
        self.buttons.AddButton("r", "Remove tag")
        self.buttons.AddButton("↹", "Select list")

        # Composition
        tabgroup = TabGroup()
        tabgroup.AddPane(self.genreview)
        tabgroup.AddPane(self.subgenreview)

        # Draw once
        self.buttons.Draw(0, maxh-2, maxw)


        key = " "
        selectedmaingenre = 0   # trace selected main genre to update subgenre view
        while key != "Ctrl-D":
            # Show everything
            self.genreview.Draw()
            self.subgenreview.Draw()
            cli.FlushScreen()

            # Handle keys
            key = cli.GetKey()
            tabgroup.HandleKey(key)

            genre = self.genreview.GetSelectedData()
            if genre["id"] != selectedmaingenre:
                selectedmaingenre = genre["id"]
                self.subgenreview.UpdateView()


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

