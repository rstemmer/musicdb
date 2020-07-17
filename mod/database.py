# MusicDB,  a music manager with web-bases UI that focus on music.
# Copyright (C) 2017-2020  Ralf Stemmer <ralf.stemmer@gmx.net>
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
A subcommand and a path to the target (artist, album, song): ``musicdb database $SUBCOMMAND $PATH``.
The target gets determined by its path.

The following subcommands are provided:

    ``add``: 
        Add new artist, album, song or video to the database.
        Direct interface to:

            * If the path addresses a song: :meth:`mdbapi.database.MusicDBDatabase.AddSong`
            * If the path addresses a album: :meth:`mdbapi.database.MusicDBDatabase.AddAlbum`
            * If the path addresses a artist: :meth:`mdbapi.database.MusicDBDatabase.AddArtist`
            * If the path addresses a video: :meth:`mdbapi.database.MusicDBDatabase.AddVideo`

    ``remove``:
        Removes an artist, album or song from the database.
        Only the database entries get removed.
        The files will not be touched.

    ``getlyrics``: 
        Search in song files for lyrics.
        This is done by calling for each song file :meth:`mdbapi.database.MusicDBDatabase.AddLyricsFromFile`
        
    ``check``: 
        Check the given path if it is a valid artist, album or song path.
        This is done by calling :meth:`mdbapi.database.MusicDBDatabase.TryAnalysePathFor`.

.. attention::

    While adding a new artist, album or song to the database, the file and directory attributes 
    and ownership gets changed to the configured one in the MusicDB Configuration.

    And after adding the new data, the command (``refresh``) gets written into the servers named pipe
    to update its cache.


Examples:

    .. code-block:: bash

        musicdb database add /data/music/Artist/2000\ -\ New\ Album

        musicdb database remove /data/music/Bad\ Artist

        musicdb database add /data/music/Artist/2000\ -\ Video.m4v


"""

import argparse
import os
from lib.modapi         import MDBModule
from mdbapi.database    import MusicDBDatabase
from tqdm               import tqdm
import traceback

class database(MDBModule, MusicDBDatabase):
    def __init__(self, config, database):
        MusicDBDatabase.__init__(self, config, database)


    def CMD_Add(self, target, path):
        print("\033[1;34mAdding following \033[1;36m" + target + "\033[1;34m to database:\033[0;36m %s \033[1;34m… "%(path), end="")
        if target == "artist":
            self.AddArtist(path)
        elif target == "album":
            self.AddAlbum(path)
        elif target == "song":
            self.AddSong(path)
        elif target == "video":
            self.AddVideo(path)
        else:
            raise ValueError("Invalid target! Target must be \"artist\", \"album\", \"song\" or \"video\".")
        print("\033[1;32mdone")

        # propagate changes
        print("\033[1;34mTrying to signal \033[1;36mMusicDB-Server\033[1;34m to update its cache … \033[1;31m", end="")
        self.UpdateServerCache()
        print("\033[1;32mdone")
        return None



    def CMD_Remove(self, target, abspath):

        try:
            path = self.fs.RemoveRoot(abspath)
        except ValueError:
            print("\033[1;31mERROR: Path %s is not part of the music collection!\033[0m"%(abspath))
            return None
        
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
        else:
            raise ValueError("Invalid target! Target must be \"artist\", \"album\" or \"song\".")
        print("\033[1;32mdone")

        # propagate changes
        print("\033[1;34mTrying to signal \033[1;36mMusicDB-Server\033[1;34m to update its cache … \033[1;31m", end="")
        self.UpdateServerCache()
        print("\033[1;32mdone")
        return None



    def CMD_GetLyrics(self, target, path):
        print("\033[1;34mAdding lyrics to following \033[1;36m" + target + "\033[1;34m:\033[0;36m %s \033[1;34m… "%(path), end="")
        if target == "song":
            self.AddLyricsFromFile(path)

        elif target == "album":
            path  = self.fs.RemoveRoot(path) # remove the path to the music directory
            album = self.db.GetAlbumByPath(path)
            songs = self.db.GetSongsByAlbumId(album["id"])
            
            for song in tqdm(songs, unit="songs"):
                self.AddLyricsFromFile(song["path"])

        elif target == "artist":
            path   = self.fs.RemoveRoot(path) # remove the path to the music directory
            artist = self.db.GetArtistByPath(path)
            songs  = self.db.GetSongsByArtistId(artist["id"])
            
            for song in tqdm(songs, unit="songs"):
                self.AddLyricsFromFile(song["path"])

        else:
            raise ValueError("Invalid target! Target must be \"artist\", \"album\" or \"song\".")

        print("\033[1;32mdone")
        return None



    def GetTargetByPath(self, abspath):
        # returns "album", "artist", "song", "video" or None if path is invalid

        try:
            path = self.fs.RemoveRoot(abspath)
        except ValueError:
            print("\033[1;31mERROR: Path %s is not part of the music collection!\033[0m"%(abspath))
            return None

        print("\033[1;34mDetermin target by path \"\033[0;36m%s\033[1;34m\" …"%(path))

        if self.fs.IsArtistPath(path, self.cfg.music.ignorealbums, self.cfg.music.ignoresongs):
            print("\033[1;34mWorking on Artist-path\033[0m")
            return "artist"

        elif self.fs.IsAlbumPath(path, self.cfg.music.ignoresongs):
            print("\033[1;34mWorking on Album-path")
            return "album"

        elif self.fs.IsSongPath(path):
            print("\033[1;34mWorking on Song-path")
            return "song"

        elif self.fs.IsVideoPath(path):
            print("\033[1;34mWorking on Video-path")
            return "video"

        else:
            print("\033[1;31mERROR: Path does not address a Song, Album or Artist\033[0m")
            return None



    @staticmethod
    def MDBM_CreateArgumentParser(parserset, modulename):
        parser = parserset.add_parser(modulename, help="do database management")
        parser.set_defaults(module=modulename)

        subp   = parser.add_subparsers(title="Commands", metavar="command", help="database commands")
        
        addparser = subp.add_parser("add", help="add target to database")
        addparser.add_argument("path", help="path to an artist, album, song or video")
        addparser.set_defaults(command="Add")

        addparser = subp.add_parser("remove", help="remove target from database")
        addparser.add_argument("path", help="path to an artist, album or song")
        addparser.set_defaults(command="Remove")

        getparser = subp.add_parser("getlyrics", help="read lyrics from file(s) and store them in the database")
        getparser.add_argument("path", help="path to an artist, album or song directory")
        getparser.set_defaults(command="GetLyrics")

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
        try:
            path = os.path.abspath(args.path)
        except Exception as e:
            print("\033[1;31mDetermine absolute path failed with exception \"%s\"!\033[0m"%(str(e)))
            return 1

        # Determine target by path
        try:
            target = self.GetTargetByPath(args.path)
        except Exception as e:
            print("\033[1;31mDetermine target by path failed with exception \"%s\"!\033[0m"%(str(e)))
            return 1

        if not target:
            return 1

        # Check if path is valid for target (GetTargetByPath is too error tolerant)
        if not self.TryAnalysePathFor(target, path):
            print("\033[1;31mInvalid path or target! Path \"%s\" does not match %s-naming scheme!\033[0m" % (path, target))
            return 1

        # Execute command
        try:
            if command == "Add":
                exitcode = self.CMD_Add(target, path)
            elif command == "Remove":
                exitcode = self.CMD_Remove(target, path)
            elif command == "GetLyrics":
                exitcode = self.CMD_GetLyrics(target, path)
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

