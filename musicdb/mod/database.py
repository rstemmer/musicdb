# MusicDB,  a music manager with web-bases UI that focus on music.
# Copyright (C) 2017 - 2021  Ralf Stemmer <ralf.stemmer@gmx.net>
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
This module manages the music database.
Its main task is to add new albums, artists or music videos to the Music Database.
This module can also be seen as the low level interface compared to :doc:`/mod/add`.

.. attention::

    The addressed paths must follow the naming scheme.
    See :doc:`/usage/music` for details.

This command line interface expects two positional arguments. 
A subcommand and a path to the target (artist, album, song, video): ``musicdb database $SUBCOMMAND $PATH``.
The target gets determined by its path.

The following subcommands are provided:

    ``remove``:
        Removes an artist, album or song from the database.
        Only the database entries get removed.
        The files will not be touched.

    ``getlyrics``: 
        Search in song files for lyrics.
        This is done by calling for each song file :meth:`musicdb.mdbapi.music.MusicDBMusic.AddLyricsFromFile`
        
    ``check``: 
        Check the given path if it is a valid artist, album or song path.
        This is done by calling :meth:`musicdb.mdbapi.music.MusicDBMusic.AnalysePath`.

.. attention::

    TODO: DEPRECATED - This behavior changed in MusicDB 8.0.0

    While adding a new artist, album or song to the database, the file and directory attributes 
    and ownership gets changed to the configured one in the MusicDB Configuration.

    And after adding the new data, the command (``refresh``) gets written into the servers named pipe
    to update its cache.


Examples:

    .. code-block:: bash


        musicdb database remove /data/music/Bad\ Artist

"""

import argparse
import traceback
from musicdb.lib.modapi     import MDBModule
from musicdb.lib.filesystem import Filesystem
from musicdb.mdbapi.music   import MusicDBMusic

class database(MDBModule, MusicDBMusic):
    def __init__(self, config, database):
        MusicDBMusic.__init__(self, config, database)



    def CMD_Remove(self, target, abspath):

        try:
            path = self.musicdirectory.RemoveRoot(abspath)
        except ValueError:
            print("\033[1;31mERROR: Path %s is not part of the music collection!\033[0m"%(abspath))
            return None
        path = self.musicdirectory.ToString(path)
        
        print("\033[1;34mRemoving following \033[1;36m" + target + "\033[1;34m from database:\033[0;36m %s \033[1;34m… "%(path), end="")

        if target == "artist":
            artist = self.db.GetArtistByPath(path)
            self.RemoveArtist(artist["id"])

        elif target == "album":
            album = self.db.GetAlbumByPath(path)
            self.RemoveAlbum(album["id"])

        elif target == "song":
            song = self.db.GetSongByPath(path)
            self.RemoveSong(song["id"])

        elif target == "video":
            video = self.db.GetVideoByPath(path)
            self.RemoveVideo(video["id"])

        else:
            raise ValueError("Invalid target! Target must be \"artist\", \"album\", \"video\" or \"song\".")
        print("\033[1;32mdone")
        return None



    def GetTargetByPath(self, abspath):
        # returns "album", "artist", "song", "video" or None if path is invalid

        try:
            path = self.musicdirectory.RemoveRoot(abspath)
        except ValueError:
            print("\033[1;31mERROR: Path %s is not part of the music collection!\033[0m"%(abspath))
            return None

        print("\033[1;34mDetermin target by path \"\033[0;36m%s\033[1;34m\" …"%(path))
        infos = self.musicdirectory.AnalysePath(path)

        if infos == None:
            print("\033[1;31mERROR: The path \033[1;30m%s\033[1;31m does not address a Song, Album, Artist or Video\033[0m"%(path))
            return None

        if infos["video"] != None:
            print("\033[1;34mWorking on the \033[1;35mVideo\033[1;34m file path of \033[0;36m" + infos["video"])
            return "video"

        if infos["song"] != None:
            print("\033[1;34mWorking on the \033[1;35mSong\033[1;34m file path of \033[0;36m" + infos["song"])
            return "song"

        if infos["album"] != None:
            print("\033[1;34mWorking on the \033[1;35mAlbum\033[1;34m directory path of \033[0;36m" + infos["album"])
            return "album"

        if infos["artist"] != None:
            print("\033[1;34mWorking on the \033[1;35mArtist\033[1;34m directory path of \033[0;36m" + infos["artist"])
            return "artist"

        print("\033[1;31mERROR: The path \033[1;30m%s\033[1;31m does not address a Song, Album, Artist or Video\033[0m"%(path))
        return None


    @staticmethod
    def MDBM_CreateArgumentParser(parserset, modulename):
        parser = parserset.add_parser(modulename, help="do database management")
        parser.set_defaults(module=modulename)

        subp   = parser.add_subparsers(title="Commands", metavar="command", help="database commands")

        addparser = subp.add_parser("remove", help="remove target from database")
        addparser.add_argument("path", help="path to an artist, album or song")
        addparser.set_defaults(command="Remove")

        chkparser = subp.add_parser("check", help="check if the path is in a correct format")
        chkparser.add_argument("path", help="path to an artist, album, song or root music directory")
        chkparser.set_defaults(command="CheckPath")


    # return exit-code
    def MDBM_Main(self, args):

        # get & check command and its arguments
        if not args.command:
            print("\033[1;31mNo command given to module database!\033[0m")
            return 1

        command = args.command

        # Determine absolute path by relative path
        fs = Filesystem()
        try:
            path = fs.AbsolutePath(args.path)
        except Exception as e:
            print("\033[1;31mDetermine absolute path failed with exception \"%s\"!\033[0m"%(str(e)))
            return 1
        path = fs.ToString(path)

        # Determine target by path
        try:
            target = self.GetTargetByPath(path)
        except Exception as e:
            traceback.print_exc()
            print("\033[1;31mDetermine target by path failed with exception \"%s\"!\033[0m"%(str(e)))
            return 1

        if not target:
            return 1

        # Check if path is valid for target (GetTargetByPath is too error tolerant for songs and albums)
        if target in ["song", "album"]:
            if not self.musicdirectory.TryAnalysePathFor(target, path):
                print("\033[1;31mInvalid path or target! Path \"%s\" does not match %s-naming scheme!\033[0m" % (path, target))
                return 1


        # Execute command
        try:
            if command == "Remove":
                exitcode = self.CMD_Remove(target, path)
            elif command == "CheckPath":
                # Nothing to do.
                # When it comes to execute a command, the path got already checked.
                print("\033[1;34mPath \033[0;36m%s\033[1;34m is a \033[1;32mvalid %s \033[1;34mpath.\033[0m"%(path,target))
                exitcode = 0
            return exitcode
        except Exception as e:
            print("\033[1;31mFATAL ERROR:");
            print(e)
            traceback.print_exc()
            return 1

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

