# MusicDB,  a music manager with web-bases UI that focus on music.
# Copyright (C) 2020  Ralf Stemmer <ralf.stemmer@gmx.net>
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
This command provides a workflow for importing a new album.
It adds its songs to MusicDB and allows renaming then to follow the MusicDB naming scheme.
When the artist of the new album does not exists, it gets also added to MusicDB.

It does the following steps:

    #. Find artists and albums that are not in the database
    #. Provide an UI to rename the files (with online validation)
    #. Normalizes the Unicode of the file names to NFC (Canonical Composition) when applying ``[c] Clean name`` command.
    #. Import artist and album
    #. Import artwork (if there is one in the meta data)
    #. Import lyrics (if there are some in the files meta data)

Press ``Ctrl-D`` to exit the tool and reject changes.

The following sections describe how to use the Unicode based UI to import new albums to MusicDB.

Select Album
------------

.. figure:: ../images/add-select.png

After calling ``musicdb add`` a list of all albums in the music collection will be shown (see screenshot above).
These albums are not registered in the database yet.
In case the list is empty, no new albums got found.
In this example, a new album of the band *Megaherz* shall be added to the database.
The albums song files are stored at ``/data/music/Megaherz/Zombieland/.mp3``.
The music root directory (the path of the music collection) is ``/data/music``.

You can only import one album at a time.
If the artist on an album does not exist yet, it will be created with importing its first album.
Select the album you want to add to the database using the arrow keys (↓ and ↑) and press enter (↵).


Repair File Names
-----------------

.. figure:: ../images/add-dirty.png

After selecting an album, the form shown on the screenshot above will be shown.
There you can change the file names of the artist and album directory as well as the name of the song files.
The name of all directories and files must match the naming scheme of MusicDB.
The scheme is shown in the comment section on top of the form.

Below the comment section, there are two sub forms *Album Import* and *New Songs*.
You can switch between those forms using the tab key (↹).


Album Import Form
^^^^^^^^^^^^^^^^^

The artist and album directory names gets generated out of the artist name, album name and release year.
Those names and values can be changed in the *Album Import* form list.
Furthermore it the can be selected if the artwork shall be imported as well, the lyrics if available.
If there is an artwork file embedded in the song files, the import artwork checkbox gets set automatically.
In case there are lyrics in the file, the checkbox gets set as well.

You can select the row of that form using the arrow keys ↓ and ↑.
To toggle the checkboxes, use the space key.
For entering text in the text areas, select the row and just type.
You can move the cursor using ← and →.


New Songs Form
^^^^^^^^^^^^^^

Below the form for the directory names, a form for the song file exists.
Each file name gets analyzed by the *add*-module and checked if the name matches the naming scheme.
Parts of the name that does not fit gets printed in red.
Pressing the c-key removes all red printed parts from the file names.

.. figure:: ../images/add-clean.png

Pressing the e-key on a selected song entry, a dialog appears (see screenshot above) that allows you to fine tune the file name.
There you can set the song name and the song number.
Pressing enter (↵) confirms the changes and the *add*-module generates the new file name regarding the changes.
If there are no multiple CDs for an album, do not type anything into the *CD number* input box.
To reject the changes of that song, press escape (␛) twice.


Online Check
^^^^^^^^^^^^

While changing names and values, they get checked immediately.
If the entered values are correct gets displayed by a green ✔ marker.
If there are any values wrong, they get marked with a red ✘.

Those markers are in front of each song file entry, showing for each file name if it matches the naming scheme.
Furthermore there are two lines at the bottom of the import form showing the artist and album names.
There you can see if the entered values in the *Album Import* text areas are valid.
It gets also checked if the artist already exists in the database or if it does not yet.
A none existing artist may indicate a typo in the artists name, so the comment after the artist name gets printed in yellow.
If this is the first album of an artist you import, it is correct that the artist is not yet available in the database.


Import Process
--------------

If all changes are done and all values are correct, press capital W to rename the files and directories,
and import the album to the database.
If you press Ctrl-d instead, the import process gets canceled and nothing will be changed.

Depending on the checkboxes you set in the *Album Import* form, the following things will now happen:

    #. Renaming the files and directory.
    #. Importing the album artwork.
    #. Importing the lyrics from each file into the database

It may happen that there is no artwork inside the song files.
In that case, you have to import an artwork manually using the :doc:`/mod/artwork` module.

"""

import argparse
import os
import re
import unicodedata
from lib.modapi         import MDBModule
from lib.db.musicdb     import MusicDatabase, SONG_LYRICSSTATE_FROMFILE
from lib.filesystem     import Filesystem
from lib.metatags       import MetaTags
from mdbapi.database    import MusicDBDatabase
from mdbapi.artwork     import MusicDBArtwork
from lib.clui.listview  import ListView
from lib.clui.text      import Text
from lib.clui.pane      import Pane
from lib.clui.dialog    import Dialog
from lib.clui.textinput import TextInput, NoTextInput
from lib.clui.boolinput import BoolInput
from lib.clui.buttonview import ButtonView
from lib.clui.tabgroup  import TabGroup


class FileNameInput(TextInput):
    def __init__(self, x=0, y=0, w=0):
        TextInput.__init__(self, x, y, w)

    def HandleKey(self, key):
        # Replace slash with DIVISION SLASH
        if key == "/":
            key = "∕"
        TextInput.HandleKey(self, key)
    

class AlbumView(ListView):
    def __init__(self, title, x=0, y=0, w=0, h=0):
        ListView.__init__(self, title, x, y, w, h)


class SongView(ListView, ButtonView):
    def __init__(self, config, albumpath, title, x, y, w, h):
        ListView.__init__(self, title, x, y, w, h)
        ButtonView.__init__(self, align="center")
        self.AddButton("↑", "Go up")
        self.AddButton("↓", "Go down")
        self.AddButton("c", "Clean name")
        self.AddButton("e", "Edit name")
        #self.AddButton("␣", "Toggle")
        #self.AddButton("↵", "Commit")
        #self.AddButton("␛", "Cancel")

        # elements are a tuple (original path, new path)

        self.cfg       = config
        self.fs        = Filesystem(self.cfg.music.path)
        self.albumpath = albumpath

        self.nameinput   = FileNameInput()
        self.numberinput = TextInput()
        self.cdnuminput  = TextInput()
        dialogh = 2+3
        self.dialog = Dialog("Rename Song", self.x, self.y+1, self.w, dialogh)
        self.dialog.AddInput("Song name:",   self.nameinput,   "Correct name only")
        self.dialog.AddInput("Song number:", self.numberinput, "Song number only")
        self.dialog.AddInput("CD number:",   self.cdnuminput,  "CD number or nothing")

        # Internal states
        self.dialogmode        = False
        self.allsongnamesvalid = False


    def FindSongs(self):
        files = self.fs.GetFiles(self.albumpath, self.cfg.music.ignoresongs)
        songs = []
        # Only take audio files into account - ignore images and booklets
        for f in files:
            extension = self.fs.GetFileExtension(f)
            if extension in ["mp3","flac","m4a","aac"]:
                # Check if the name has valid Unicode.
                # Some strange music stores have strange Unicode issues
                try:
                    f.encode("utf-8")
                except UnicodeEncodeError as e:
                    print("\n\033[1;31mThere is a file with a name that contains invalid utf-8 code.")
                    print("Please navigate to the album %s and rename strange looking files.\033[0m"%(self.albumpath))
                    print("\033[1;30mIf there is no cursor visible, execute \033[0;36mreset\033[0m")
                    exit(1)

                songs.append((f,f))
        return songs


    def CleanFileNames(self):
        for index, element in enumerate(self.elements):
            origpath   = element[0]
            path       = element[1]
            directory  = self.fs.GetDirectory(path)
            filename   = self.fs.GetFileName(path)
            extension  = self.fs.GetFileExtension(path)
            seg        = self.FileNameSegments(filename)

            newfilename  = filename[seg["number"]:seg["gap"]]
            newfilename += filename[seg["name"]:seg["end"]]
            newfilename  = unicodedata.normalize("NFC", newfilename)

            newpath = os.path.join(directory, newfilename + "." + extension)
            self.elements[index] = (origpath, newpath)


    # no path, no file extension!
    # returns indices of name segments
    def FileNameSegments(self, filename):
        seg = {}
        
        # Start of song number
        m = re.search("\d", filename)
        if m:
            seg["number"] = m.start()
        else:
            seg["number"] = 0

        # End of song number (1 space is necessary)
        m = re.search("\s", filename[seg["number"]:])
        if m:
            seg["gap"] = seg["number"] + 1 + m.start()
        else:                             
            seg["gap"] = seg["number"] + 1

        # Find start of song name
        m = re.search("\w", filename[seg["gap"]:])
        if m:
            seg["name"] = seg["gap"] + m.start()
        else:
            seg["name"] = seg["gap"]

        # Find end of song name (before " [Explicit]")
        i = filename.rfind(" [Explicit]")
        if i > 0:
            seg["end"] = i
        else:
            seg["end"] = len(filename)

        return seg 


    def UpdateUI(self):
        newsongs = self.FindSongs()
        self.SetData(newsongs)


    def onDrawElement(self, element, number, maxwidth):
        oldpath    = element[0]
        path       = element[1]
        width      = maxwidth
        filename   = self.fs.GetFileName(path)
        extension  = self.fs.GetFileExtension(path)
        analresult = self.fs.AnalyseSongFileName(filename + "." + extension)
        seg        = self.FileNameSegments(filename)

        # Render validation
        if not analresult:
            validation = "\033[1;31m ✘ "
            self.allsongnamesvalid = False
        elif seg["number"] != 0 or seg["gap"] != seg["name"] or seg["end"] != len(filename):
            validation = "\033[1;31m ✘ "
            self.allsongnamesvalid = False
        else:
            validation = "\033[1;32m ✔ "
        width -= 3


        # Render file name
        renderedname  = ""
        width        -= len(filename)
        renderedname += "\033[1;31m\033[4m" + filename[0:seg["number"]] + "\033[24m"
        renderedname += "\033[1;34m" + filename[seg["number"]:seg["gap"]]
        renderedname += "\033[1;31m\033[4m" + filename[seg["gap"]:seg["name"]] + "\033[24m"
        renderedname += "\033[1;34m" + filename[seg["name"]:seg["end"]]
        renderedname += "\033[1;31m\033[4m" + filename[seg["end"]:] + "\033[24m"

        # Render file extension
        fileextension = "." + extension
        fileextension = fileextension[:width]
        fileextension = fileextension.ljust(width)
        return validation + "\033[1;34m" + renderedname + "\033[1;30m" + fileextension

    def Draw(self):
        if self.dialogmode == True:
            pass
        else:
            self.allsongnamesvalid = True  # Will be updated by ListView.Draw() call
            ListView.Draw(self)
            x = self.x + 1
            y = self.y + self.h - 1
            w = self.w - 2
            ButtonView.Draw(self, x, y, w)


    def HandleKey(self, key):
        if self.dialogmode == True:
            if key == "enter":  # Commit dialog inputs
                songname   = self.nameinput.GetData()
                songnumber = self.numberinput.GetData()
                cdnumber   = self.cdnuminput.GetData()

                element    = self.dialog.oldelement
                path       = element[1] # the editable path is 1, 0 is the original path
                directory  = self.fs.GetDirectory(path)
                extension  = self.fs.GetFileExtension(path)

                if len(songnumber) == 1:
                    songnumber = "0"+songnumber
                if cdnumber:
                    songnumber = cdnumber + "-" + songnumber

                newpath    = os.path.join(directory, songnumber + " " + songname + "." + extension)
                self.SetSelectedData((element[0], newpath))

                self.dialogmode = False
                self.Draw() # show list view instead of dialog

            elif key == "escape":
                self.dialogmode     = False
                self.dialog.oldname = None  # prevent errors by leaving a clean state
                self.Draw() # show list view instead of dialog
                # reject changes

            else:
                self.dialog.HandleKey(key)

        else:
            if key == "up" or key == "down":
                ListView.HandleKey(self, key)

            elif key == "c":
                self.CleanFileNames()

            elif key == "e":  # edit name
                element    = self.GetSelectedData()
                editpath   = element[1]
                filename   = self.fs.GetFileName(editpath)
                seg        = self.FileNameSegments(filename)
                songnumber = filename[seg["number"]:seg["gap"]].strip()
                songname   = filename[seg["name"]:].strip()

                if "-" in songnumber:
                    cdnumber   = songnumber.split("-")[0].strip()
                    songnumber = songnumber.split("-")[1].strip()
                else:
                    cdnumber = ""

                self.nameinput.SetData(songname)
                self.numberinput.SetData(songnumber)
                self.cdnuminput.SetData(cdnumber)

                self.dialog.oldelement = element
                self.dialog.Draw()
                self.dialogmode = True



class add(MDBModule, MusicDBDatabase):
    def __init__(self, config, database):
        MDBModule.__init__(self)
        MusicDBDatabase.__init__(self, config, database)

        # gets already set by MusicDBDatabase
        #self.db  = None
        #self.cfg = None
        #self.fs  = None
        self.cli = None # \.
        self.maxh= 0    #  > gets initialized in the main method
        self.maxw= 0    # /


    @staticmethod
    def MDBM_CreateArgumentParser(parserset, modulename):
        parser = parserset.add_parser(modulename, help="Easy import of a new Album")
        parser.set_defaults(module=modulename)
        return parser


    def FindNewAlbums(self):
        # Also find new artists and list their albums.
        newpaths   = self.FindNewPaths()
        newartists = newpaths["artists"]
        newalbums  = newpaths["albums"]

        # With MusicDB 7.0.0 all new albums are listed in new album paths, not only of known artists
        #for newartist in newartists:
        #    albumpaths = self.fs.GetSubdirectories(newartist, self.cfg.music.ignorealbums)
        #    newalbums.extend(albumpaths)

        return newalbums


    def GetAlbumMetadata(self, albumpath):
        # get all songs from the albums
        songpaths = self.fs.GetFiles(albumpath, self.cfg.music.ignoresongs) # ignores also all directories
        metatags  = MetaTags(self.cfg.music.path)

        # Try to load a file
        for songpath in songpaths:
            try:
                metatags.Load(songpath)
            except ValueError:
                continue
            break
        else:
            return None

        metadata = metatags.GetAllMetadata()
        return metadata



    def ShowAlbumView(self, newalbums):
        self.cli.ShowCursor(False)
        self.cli.ClearScreen()
        self.cli.SetCursor(1, 1)
        self.cli.SetColor("1;30", "40")
        self.cli.PrintText("Press Ctrl-D to exit without any changes.")

        # Calculate the positions of the UI element
        listx = 1
        listy = 3
        listw = self.maxw - 2  # -2 for some space around
        listh = self.maxh - 6  # -6 for info on top and the button bar below

        # List Views
        albumview = AlbumView("New Albums", listx, listy, listw, listh)
        albumview.SetData(newalbums)

        # Buttons
        buttons = ButtonView(align="middle")
        buttons.AddButton("↑", "Go up")
        buttons.AddButton("↓", "Go down")
        buttons.AddButton("↵", "Select for Import")

        # Draw once
        buttons.Draw(0, self.maxh-2, self.maxw)

        while True:
            # Show everything
            albumview.Draw()
            self.cli.FlushScreen()

            # Handle keys
            key = self.cli.GetKey()
            if key == "Ctrl-D":
                return None

            elif key == "enter":
                return albumview.GetSelectedData()

            else:
                albumview.HandleKey(key)


    def ShowArtistValidation(self, artistname, x, y, w):
        width = w
        label = "Artist entry: "
        self.cli.SetCursor(x, y)

        # Print Validation Marker
        if "/" in artistname:
            validation = "\033[1;31m✘ "
            validname  = False
        else:
            validation = "\033[1;32m✔ "
            validname  = True
        self.cli.PrintText(validation)
        width -= 2

        # Print Label
        self.cli.SetFGColor("34")
        self.cli.PrintText(label)
        width -= len(label)

        # Print Path
        if validname:
            self.cli.SetFGColor("36")
        else:
            self.cli.SetFGColor("31")
        self.cli.PrintText(artistname)
        width -= len(artistname)

        # Print Note
        artist = self.db.GetArtistByPath(artistname)
        if artist:
            self.cli.SetFGColor("0;32")
            note = " (Exists in database)"
        elif validname:
            self.cli.SetFGColor("0;33")
            note = " (Will be created)"
        else:
            self.cli.SetFGColor("0;31")
            note = " (Invalid name)"
        note = note[:width]
        note = note.ljust(width)
        self.cli.PrintText(note)


    def ShowAlbumValidation(self, artistname, albumname, releasedate, x, y, w):
        width = w
        label = "Album directory: "
        self.cli.SetCursor(x, y)

        # Check if everything is valid
        note = ""
        if len(releasedate) != 4 or releasedate.isnumeric() == False:
            validrelease = False
            note = " (Release date is not a 4 digit year!)"
        else:
            validrelease = True

        if "/" in albumname:
            validname = False
            note = " (/ in album name forbidden!)"
        elif len(albumname) == 0:
            validname = False
            note = " (No name entered!)"
        else:
            validname = True

        if self.db.GetAlbumByPath(artistname + "/" + releasedate + " - " + albumname):
            note = " (Already exists in database!)"
            validentry = False
        else:
            validentry = True

        # Print Validation Marker
        if validrelease and validname and validentry:
            validation = "\033[1;32m✔ "
        else:
            validation = "\033[1;31m✘ "

        self.cli.PrintText(validation)
        width -= 2

        # Print Label
        self.cli.SetFGColor("1;34")
        self.cli.PrintText(label)
        width -= len(label)

        # Print directory name
        #albumpath = releasedate + " - " + albumname
        width -= len(releasedate)
        width -= len(" - ")
        width -= len(albumname)
        if validrelease and validentry:
            self.cli.SetFGColor("1;36")
        else:
            self.cli.SetFGColor("1;31")
        self.cli.PrintText(releasedate)
        if not validentry:
            self.cli.SetFGColor("1;31")
        else:
            self.cli.SetFGColor("1;36")
        self.cli.PrintText(" - ")
        if validname and validentry:
            self.cli.SetFGColor("1;36")
        else:
            self.cli.SetFGColor("1;31")
        self.cli.PrintText(albumname)

        # Print Note
        note = note[:width]
        note = note.ljust(width)
        self.cli.SetFGColor("0;31")
        self.cli.PrintText(note)


    def ShowSongValidation(self, valid, x, y, w):
        width = w
        self.cli.SetCursor(x, y)

        if valid:
            label = "\033[1;32m✔ "
            note  = "\033[0;32m(Valid)                                 " # FIXME: This is a hack to overwrite the "invalid" note
        else:
            label = "\033[1;31m✘ "
            note  = "\033[0;31m(Invalid names - please edit song names)"
        label += "\033[1;34mSong file names: " + note

        #label = label[:width]
        #label = label.ljust(width)
        self.cli.PrintText(label)


    def ShowImportDialog(self, albumpath):
        self.cli.ShowCursor(False)
        self.cli.ClearScreen()
        self.cli.SetColor("1;30", "40")
        self.cli.SetCursor(1, 1)
        self.cli.PrintText("Press Ctrl-D to exit without any changes.")
        self.cli.SetCursor(1, 2)
        self.cli.PrintText("\033[1;31m✘\033[1;30m marks invalid data, \033[1;32m✔\033[1;30m marks valid data.")
        self.cli.SetCursor(1, 3)
        self.cli.PrintText("MusicDB file naming scheme:")
        self.cli.SetCursor(3, 4)
        self.cli.PrintText("{artistname}/{albumrelease} - {albumname}/{songnumber} {songname}.{extension}")
        self.cli.SetCursor(3, 5)
        self.cli.PrintText("{artistname}/{albumrelease} - {albumname}/{cdnumber}-{songnumber} {songname}.{extension}")

        # Calculate the positions of the UI element
        headh   = 5 # n lines high headline
        pathh   = 3
        dialogx = 1
        dialogy = 2 + headh
        dialogw = self.maxw-2
        dialogh = 8
        listx   = 1
        listy   = dialogy + dialogh + 1
        listw   = self.maxw-2
        listh   = self.maxh - (headh + dialogh + pathh + 3*2)
        pathx   = dialogx + 1
        pathw   = dialogw - 2
        pathy   = listy + listh + 1

        # List Views
        songview    = SongView(self.cfg, albumpath, "New Songs", listx, listy, listw, listh)
        albumdialog = Dialog("Album Import", dialogx, dialogy, dialogw, dialogh)
        albumdialog.RemoveButton("Cancel")
        albumdialog.RemoveButton("Commit")

        artistinput    = FileNameInput()
        nameinput      = FileNameInput()
        releaseinput   = TextInput()
        origininput    = TextInput()
        artworkinput   = BoolInput()
        lyricsinput    = BoolInput()

        albumdialog.AddInput("Artist name:", artistinput, "Correct name of the album artist")
        albumdialog.AddInput("Album name:", nameinput, "Correct name of the album (no release year)")
        albumdialog.AddInput("Release date:", releaseinput, "Year with 4 digits like \"2017\"")
        albumdialog.AddInput("Origin:", origininput, "\"iTunes\", \"bandcamp\", \"Amazon\", \"CD\", \"internet\"")
        albumdialog.AddInput("Import artwork:", artworkinput, "Import the artwork to MusicDB")
        albumdialog.AddInput("Import lyrics:", lyricsinput, "Try to import lyrics from file")

        # Initialize dialog
        albumdirname = os.path.split(albumpath)[1]
        artistdirname= os.path.split(albumpath)[0]
        metadata     = self.GetAlbumMetadata(albumpath)
        if metadata:
            origin   = str(metadata["origin"])

            if metadata["lyrics"]:
                lyricsinput.SetData(True)
            else:
                lyricsinput.SetData(False)
        else: # No meta data available
            origin   = "Internet"

        analresult   = self.fs.AnalyseAlbumDirectoryName(albumdirname)
        if analresult:
            release   = str(analresult["release"])
            albumname = analresult["name"]
        else:
            # suggest the release date from meta data - the user can change when it's wrong
            if metadata:
                release = str(metadata["releaseyear"])
            else:
                release = "20??"
            albumname = albumdirname

        artistinput.SetData(artistdirname)
        nameinput.SetData(albumname)
        releaseinput.SetData(release)
        origininput.SetData(origin)
        artworkinput.SetData(True)

        # Initialize list
        songview.UpdateUI()

        # Buttons
        buttons = ButtonView(align="middle")
        buttons.AddButton("↹", "Select list")
        buttons.AddButton("W", "Rename files Write to database")

        # Composition
        tabgroup = TabGroup()
        tabgroup.AddPane(albumdialog)
        tabgroup.AddPane(songview)

        # Draw once
        buttons.Draw(0, self.maxh-2, self.maxw)

        while True:
            artistname  = artistinput.GetData()
            albumname   = nameinput.GetData()
            releasedate = releaseinput.GetData()
            origin      = origininput.GetData()
            artwork     = artworkinput.GetData()
            lyrics      = lyricsinput.GetData()

            # Show everything
            songview.Draw()
            albumdialog.Draw()
            self.ShowArtistValidation(artistname, pathx, pathy, pathw)
            self.ShowAlbumValidation(artistname, albumname, releasedate, pathx, pathy+1, pathw)
            self.ShowSongValidation(songview.allsongnamesvalid, pathx, pathy+2, pathw)
            #if songview.allsongnamesvalid:
            #    validation = "\033[1;32m✔ "
            #else:
            #    validation = "\033[1;31m✘ "
            #self.cli.PrintText(validation)

            self.cli.FlushScreen()

            # Handle keys
            key = self.cli.GetKey()
            if key == "Ctrl-D":
                return None

            elif key == "W":
                # Returns a dicrionary
                data = {}
                data["oldalbumpath"]= albumpath
                data["artistname"]  = artistname
                data["albumname"]   = albumname
                data["releasedate"] = releasedate
                data["origin"]      = origin
                data["runartwork"]  = artwork
                data["runlyrics"]   = lyrics
                data["songs"]       = songview.GetData()
                return data

            else:
                tabgroup.HandleKey(key)


    def RunImportProcess(self, data):
        # show tasks
        self.cli.ClearScreen()
        self.cli.SetCursor(0,0)

        # rename songs
        for song in data["songs"]:
            oldpath = song[0]
            newpath = song[1]
            if oldpath == newpath:
                continue

            self.cli.PrintText("\033[1;34mRename Song: \033[0;31m%s\033[1;34m -> \033[0;32m%s\n"%(song[0], song[1]))
            self.fs.MoveFile(oldpath, newpath)

        # rename album
        oldalbumpath = data["oldalbumpath"]
        newalbumpath = os.path.join(data["artistname"], data["releasedate"] + " - " + data["albumname"])
        if oldalbumpath != newalbumpath:
            self.cli.PrintText("\033[1;34mRename Album:  \033[0;31m%s\033[1;34m -> \033[0;32m%s\n"%(oldalbumpath, newalbumpath))
            self.fs.MoveDirectory(oldalbumpath, newalbumpath)

        # rename artist
        oldartistpath = self.fs.GetDirectory(oldalbumpath)
        newartistpath = data["artistname"]
        if oldartistpath != newartistpath:
            self.cli.PrintText("\033[1;34mRename Artist: \033[0;31m%s\033[1;34m -> \033[0;32m%s\n"%(oldartistpath, newartistpath))
            self.fs.MoveDirectory(oldartistpath, newartistpath)

        # import
        artist = self.db.GetArtistByPath(newartistpath)
        if not artist:
            self.cli.PrintText("\033[1;34mAdd new artist \033[0;36m%s\n"%(newartistpath))
            self.db.AddArtist(newartistpath, newartistpath)
            artist = self.db.GetArtistByPath(newartistpath)

        if not artist:
            self.cli.PrintText("\033[1;31mAdding artist failed! \033[1;30m(Retry the import workflow and check the names of the files in the file system)\033[0m")
            return
        else:
            self.cli.PrintText("\033[1;34mImport album \033[0;36m%s\n"%(newalbumpath))
            try:
                self.AddAlbum(newalbumpath, artist["id"])
            except Exception as e:
                self.cli.PrintText("\033[1;31mImporting album failed with exception %s!\033[1;30m (Nothing bad happened, just try to solve the issue and repeat. Were all Paths and file names valid?)\n"%(str(e)))

        # set origin
        album = self.db.GetAlbumByPath(newalbumpath)
        if not album:
            self.cli.PrintText("\033[1;31mImporting album failed! \033[1;30m(Retry the import workflow and check the names of the files in the file system)\033[0m")
            return
        elif album["origin"] != data["origin"]:
            self.cli.PrintText("\033[1;34mSet Origin \033[0;36m%s\n"%(data["origin"]))
            album["origin"] = data["origin"]
            self.db.WriteAlbum(album)
        self.cli.PrintText("\033[1;32mImporting album succeeded!\n")

        # process
        if data["runartwork"]:
            self.cli.PrintText("\033[1;37mRun Artwork Import\n")
            artwork = MusicDBArtwork(self.cfg, self.db)
            artwork.UpdateAlbumArtwork(album)

        if data["runlyrics"]:
            self.cli.PrintText("\033[1;37mRun Lyrics Import\n")
            metadata = MetaTags(self.cfg.music.path)

            for songtuple in data["songs"]:
                songpath = songtuple[1]
                song     = self.db.GetSongByPath(songpath)
                if not song:
                    continue
                songid   = song["id"]

                metadata.Load(songpath)
                lyrics   = metadata.GetLyrics()
                if lyrics:
                    self.db.SetLyrics(songid, lyrics, SONG_LYRICSSTATE_FROMFILE)


    # return exit-code
    def MDBM_Main(self, args):

        self.cli = Text()
        self.maxw, self.maxh = self.cli.GetScreenSize()

        newalbums = self.FindNewAlbums()
        if newalbums:
            albumpath = self.ShowAlbumView(newalbums)
        else:
            print("\033[1;33mNo new albums found")
            return 0

        if albumpath:
            data = self.ShowImportDialog(albumpath)
        else:
            data = None
            print("\033[1;33mImport process canceled by user")
            
        if data:
            self.RunImportProcess(data)
            self.UpdateServerCache()
        else:
            self.cli.ClearScreen()
            self.cli.SetCursor(0,0)


        self.cli.SetColor("0","40")
        self.cli.ShowCursor(True)
        return 0

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

