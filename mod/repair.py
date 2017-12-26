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
This command checks the database and finds inconsistent information.
The following things get checked:

    #. Do all artist, album and song files have an database entry
    #. Do all artist, album and song database entries have a file

The result gets presented in two lists.
The left list lists all files without a database entry, the right list all database entries without a file.
To switch between those lists use *tab* key.
The key commands listed above the lists work on the selected entries.
The key commands listed below are independent of the data.

The update command ``u`` will merge the file selected in the left list with the database entry selected in the right list

Press ``q`` key, or ``Ctrl-D`` to exit the tool.

.. warning::
    
    Currently, only songs can be removed.

Example:

    .. code-block:: bash

        musicdb -q repair
        # -q: do not show logs on stdout
"""

import argparse
from lib.modapi         import MDBModule
from lib.db.musicdb     import MusicDatabase
from lib.filesystem     import Filesystem
from mdbapi.database    import MusicDBDatabase
from lib.clui.listview  import ListView
from lib.clui.text      import Text
from lib.clui.buttonview import ButtonView
from lib.clui.tabgroup  import TabGroup


class OrphanPathView(ListView):
    def __init__(self, title, x=0, y=0, w=0, h=0):
        ListView.__init__(self, title, x, y, w, h)

    def SetData(self, artists, albums, songs):
        artistdata = [("artist", path) for path in artists]
        albumdata  = [("album",  path) for path in albums ]
        songdata   = [("song",   path) for path in songs  ]

        data = []
        data.extend(artistdata)
        data.extend(albumdata )
        data.extend(songdata  )
        ListView.SetData(self, data)

    def onDrawElement(self, element, number, maxwidth):
        tag  = element[0]
        path = element[1]
        maxpathlen = maxwidth - 6   # - "[xxx] "

        string = "\033[1;30m["
        if tag == "artist":
            string += "art"
        elif tag == "album":
            string += "alb"
        elif tag == "song":
            string += "sng"
        else:
            string += "INV"
        string += "] \033[1;34m"
        string += path[:(maxpathlen)].ljust(maxpathlen)
        return string


class OrphanEntryView(ListView):
    def __init__(self, title, x=0, y=0, w=0, h=0):
        ListView.__init__(self, title, x, y, w, h)

    def SetData(self, artists, albums, songs):
        artistdata = [("artist", entry) for entry in artists]
        albumdata  = [("album",  entry) for entry in albums ]
        songdata   = [("song",   entry) for entry in songs  ]

        data = []
        data.extend(artistdata)
        data.extend(albumdata )
        data.extend(songdata  )
        ListView.SetData(self, data)

    def onDrawElement(self, element, number, maxwidth):
        tag   = element[0]
        entry = element[1]
        if tag == "song":
            name = "%2d-%2d - %s"%(entry["cd"], entry["number"], entry["name"])
        elif tag == "album":
            name = "%4d - %s"%(entry["release"], entry["name"])
        elif tag == "artist":
            name = entry["name"]
        else:
            name = "INVALID"

        maxnamewidth = maxwidth - 6 # - "[xxx] "

        string = "\033[1;30m["
        if tag == "artist":
            string += "art"
        elif tag == "album":
            string += "alb"
        elif tag == "song":
            string += "sng"
        else:
            string += "INV"
        string += "] \033[1;34m"
        string += name[:(maxnamewidth)].ljust(maxnamewidth)
        return string


class repair(MDBModule, MusicDBDatabase):
    def __init__(self, config, database):
        MDBModule.__init__(self)
        MusicDBDatabase.__init__(self, config, database)

        # gets already set by MusicDBDatabase
        #self.db  = None
        #self.cfg = None
        #self.fs  = None

        self.lostartists = []
        self.lostalbums  = []
        self.lostsongs   = []
        self.newartists  = []
        self.newalbums   = []
        self.newsongs    = []


    @staticmethod
    def MDBM_CreateArgumentParser(parserset, modulename):
        parser = parserset.add_parser(modulename, help="find and repair inconsistent information")
        parser.set_defaults(module=modulename)
        return parser


    def RunCheck(self):
        """
        This method runs the following checks and updates the internal state of this class.

            * :meth:`mdbapi.database.MusicDBDatabase.FindLostPaths`
            * :meth:`mdbapi.database.MusicDBDatabase.FindNewPaths`

        Returns:
            *Nothing*
        """
        self.lostartists, self.lostalbums, self.lostsongs = self.FindLostPaths()
        self.newartists,  self.newalbums,  self.newsongs  = self.FindNewPaths()


    def UpdateDatabase(self, target, targetid, path):
        if target == "artist":
            self.UpdateArtist(targetid, path)
        elif target == "album":
            self.UpdateAlbum(targetid, path)
        elif target == "song":
            self.UpdateSong(targetid, path)

    def AddToDatabase(self, target, path):
        if target == "artist":
            self.AddArtist(path)
        elif target == "album":
            self.AddAlbum(path)
        elif target == "song":
            self.AddSong(path)

    def RemoveFromDatabase(self, target, targetid):
        if target == "song":
            self.RemoveSong(targetid)
        #if target == "artist":
        #    pass
        #elif target == "album":
        #    pass
        #elif target == "song":
        #    pass



    def UpdateUI(self):
        self.RunCheck()
        self.orphanpathview.SetData(self.newartists, self.newalbums, self.newsongs)
        self.orphanentryview.SetData(self.lostartists, self.lostalbums, self.lostsongs)
        self.orphanpathview.Draw()
        self.orphanentryview.Draw()


    def ShowUI(self):
        cli  = Text()
        cli.ShowCursor(False)
        cli.ClearScreen()
        maxw, maxh = cli.GetScreenSize()

        # List Views
        self.orphanpathview  = OrphanPathView("Orphan Paths", x=1, y=3, w=maxw//2-1, h=maxh-6)
        self.orphanpathview.SetData(self.newartists, self.newalbums, self.newsongs)

        self.orphanentryview = OrphanEntryView("Orphan DB Entries", x=maxw//2+1, y=3, w=maxw//2-1, h=maxh-6)
        self.orphanentryview.SetData(self.lostartists, self.lostalbums, self.lostsongs)

        # Buttons
        lbuttons = ButtonView(align="left")
        lbuttons.AddButton("a", "Add path to database")
        lbuttons.AddButton("↑", "Go up")
        lbuttons.AddButton("↓", "Go down")
        
        mbuttons = ButtonView(align="middle")
        mbuttons.AddButton("u", "Update database entry path")

        rbuttons = ButtonView(align="right")
        rbuttons.AddButton("↑", "Go up")
        rbuttons.AddButton("↓", "Go down")
        rbuttons.AddButton("r", "Remove song from database")
        
        bbuttons = ButtonView() # bottom-buttons
        bbuttons.AddButton("c", "Check again")
        bbuttons.AddButton("↹", "Select list")
        bbuttons.AddButton("q", "Quit")
        
        # Draw ButtonViews
        w = (maxw // 3) - 2
        lbuttons.Draw(2,         1,      w)
        mbuttons.Draw(maxw//3,   1,      w)
        rbuttons.Draw(2*maxw//3, 1,      w)
        bbuttons.Draw(2,         maxh-2, maxw)

        # Draw Lists
        self.orphanpathview.Draw()
        self.orphanentryview.Draw()

        # Create Tab group
        tabgroup = TabGroup()
        tabgroup.AddPane(self.orphanpathview)
        tabgroup.AddPane(self.orphanentryview)

        key = " "
        while key != "q" and key != "Ctrl-D":
            cli.FlushScreen()
            key = cli.GetKey()
            tabgroup.HandleKey(key)

            # Update Views
            if key == "c":
                self.UpdateUI()

            # Update Database
            if key == "u":
                newdata = self.orphanpathview.GetSelectedData()
                olddata = self.orphanentryview.GetSelectedData()

                # check if both are songs, albums or artists
                if newdata[0] != olddata[0]:
                    continue
                target  = newdata[0]
                newpath = newdata[1]
                entryid = olddata[1]["id"]
                self.UpdateDatabase(target, entryid, newpath)
                self.UpdateUI()

            # Add To Database
            if key == "a":
                newdata = self.orphanpathview.GetSelectedData()

                target  = newdata[0]
                newpath = newdata[1]
                self.AddToDatabase(target, newpath)

            # Remove From Database
            if key == "r":
                data = self.orphanentryview.GetSelectedData()

                target   = data[0]
                targetid = data[1]["id"]
                self.RemoveFromDatabase(target, targetid)
                self.UpdateUI()


        cli.ClearScreen()
        cli.SetCursor(0,0)
        cli.ShowCursor(True)
        return


    # return exit-code
    def MDBM_Main(self, args):
        albums       = self.db.GetAllAlbums()
        songs        = self.db.GetAllSongs()

        self.RunCheck()
        self.ShowUI()
        return 0

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

