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
This command provides a workflow for importing a new album.
It adds its songs to MusicDB and allows renaming then to follow the MusicDB naming scheme.
When the artist of the new album does not exists, it gets also added to MusicDB.

It does the following steps:

    #. Find artists and albums that are not in the database
    #. Provide an UI to rename the files (with online validation)
    #. Import artist and album
    #. Import artwork (if there is one in the meta data)
    #. Import lyrics (if there are some in the files meta data)
    #. Run MusicAI to determine the music genres

Press ``Ctrl-D`` to exit the tool and reject non-saved changes.

Example:

    .. code-block:: bash

        musicdb add
"""

import argparse
import os
import re
from lib.modapi         import MDBModule
from lib.db.musicdb     import MusicDatabase, SONG_LYRICSSTATE_FROMFILE
from lib.filesystem     import Filesystem
from lib.metatags       import MetaTags
#from mdbapi.tags        import MusicDBTags
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

from mod.musicai        import musicai as musicai_module

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
        self.dialogmode = False


    def FindSongs(self):
        files = self.fs.GetFiles(self.albumpath, self.cfg.music.ignoresongs)
        songs = []
        # Only take audio files into account - ignore images and booklets
        for f in files:
            extension = self.fs.GetFileExtension(f)
            if extension in ["mp3","flac","m4a","aac"]:
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
            newfilename += filename[seg["name"]:]

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

        # Render validation
        if not analresult:
            validation = "\033[1;31m ✘ "
        else:
            validation = "\033[1;32m ✔ "
        width -= 3


        # Render file name
        renderedname  = ""
        width        -= len(filename)
        seg           = self.FileNameSegments(filename)
        renderedname += "\033[1;31m\033[4m" + filename[0:seg["number"]] + "\033[24m"
        renderedname += "\033[1;34m" + filename[seg["number"]:seg["gap"]]
        renderedname += "\033[1;31m\033[4m" + filename[seg["gap"]:seg["name"]] + "\033[24m"
        renderedname += "\033[1;34m" + filename[seg["name"]:]

        # Render file extension
        fileextension = "." + extension
        fileextension = fileextension[:width]
        fileextension = fileextension.ljust(width)
        return validation + "\033[1;34m" + renderedname + "\033[1;30m" + fileextension

    def Draw(self):
        if self.dialogmode == True:
            pass
        else:
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
        newartists ,  newalbums, _ = self.FindNewPaths()
        for newartist in newartists:
            albumpaths = self.fs.GetSubdirectories(newartist, self.cfg.music.ignorealbums)
            newalbums.extend(albumpaths)

        return newalbums


    def GetAlbumMetadata(self, albumpath):
        # get all songs from the albums
        songpaths = self.fs.GetFiles(albumpath, self.cfg.music.ignoresongs) # ignores also all directories
        metatags  = MetaTags(self.cfg.music.path)
        metatags.Load(songpaths[0])
        metadata  = metatags.GetAllMetadata()
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
        pathh   = 2
        dialogx = 1
        dialogy = 2 + headh
        dialogw = self.maxw-2
        dialogh = 9
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
        musicaiinput   = BoolInput()
        lyricsinput    = BoolInput()

        albumdialog.AddInput("Artist name:", artistinput, "Correct name of the album artist")
        albumdialog.AddInput("Album name:", nameinput, "Correct name of the album (no release year)")
        albumdialog.AddInput("Release date:", releaseinput, "Year with 4 digits like \"2017\"")
        albumdialog.AddInput("Origin:", origininput, "\"iTunes\", \"bandcamp\", \"CD\", \"internet\", \"music163\"")
        albumdialog.AddInput("Import artwork:", artworkinput, "Import the artwork to MusicDB")
        albumdialog.AddInput("Import lyrics:", lyricsinput, "Try to import lyrics from file")
        albumdialog.AddInput("Predict genre:", musicaiinput, "Runs MusicAI to predict the song genres")

        # Initialize dialog
        albumdirname = os.path.split(albumpath)[1]
        artistdirname= os.path.split(albumpath)[0]
        metadata     = self.GetAlbumMetadata(albumpath)
        origin       = str(metadata["origin"])
        analresult   = self.fs.AnalyseAlbumDirectoryName(albumdirname)
        if analresult:
            release   = str(analresult["release"])
            albumname = analresult["name"]
        else:
            # suggest the release date from meta data - the user can change when it's wrong
            release   = str(metadata["releaseyear"])
            albumname = albumdirname

        artistinput.SetData(artistdirname)
        nameinput.SetData(albumname)
        releaseinput.SetData(release)
        origininput.SetData(origin)
        artworkinput.SetData(True)
        musicaiinput.SetData(False)
        if metadata["lyrics"]:
            lyricsinput.SetData(True)
        else:
            lyricsinput.SetData(False)

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
            musicai     = musicaiinput.GetData()

            # Show everything
            songview.Draw()
            albumdialog.Draw()
            self.ShowArtistValidation(artistname, pathx, pathy, pathw)
            self.ShowAlbumValidation(artistname, albumname, releasedate, pathx, pathy+1, pathw)
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
                data["runmusicai"]  = musicai
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
            self.AddAlbum(newalbumpath, artist["id"])

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
            metadata = MetaTags()
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

        if data["runmusicai"]:
            self.cli.PrintText("\033[1;37mRun MusicAI\n")
            absalbumpath = self.fs.AbsolutePath(newalbumpath)
            musicai      = musicai_module(self.cfg, self.db)
            mdbsongs     = musicai.GetSongsFromPath(absalbumpath)
            if not mdbsongs:
                self.cli.PrintText("\033[1;31mNo songs to analyze found in %s! \033[1;30m\033[0m"%(absalbumpath))
                return
            
            musicai.GenerateFeatureset(mdbsongs)
            prediction = self.PerformPrediction(mdbsongs)
            self.StorePrediction(prediction)

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

