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
This module manages the music database.
Its main task is to add new albums or artist to the Music Database.

This command line interface expects three positional parameters. A subcommand, a target, and a path to the target: ``musicdb database $SUBCOMMAND $TARGET $PATH``

The following subcommands are provided:

    ``add``: 
        Add new artist, album or song to the database.
        Direct interface to:

            * if target is ``song``: :meth:`mdbapi.database.MusicDBDatabase.AddSong`
            * if target is ``album``: :meth:`mdbapi.database.MusicDBDatabase.AddAlbum`
            * if target is ``artist``: :meth:`mdbapi.database.MusicDBDatabase.AddArtist`

    ``update``:
        Update a song file via ::meth:`mdbapi.database.MusicDBDatabase.UpdateSong`

    ``getlyrics``: 
        Search in song files for lyrics.
        This is done by calling for each song file :meth:`mdbapi.database.MusicDBDatabase.AddLyricsFromFile`
        
    ``check``: 
        Check the given path if it is a valid artist, album or song path.
        This is done by calling :meth:`mdbapi.database.MusicDBDatabase.TryAnalysePathFor`.

.. attention::

    While adding a new artist, album or song to the database, the file and directory attributes and ownerrship gets changed to the configured one in the MusicDB Configuration.
    And after adding the new data, a signal (USR1) gets send to the server to update its cache.
    Therefore, root permissions are necessary.


Examples:

    .. code-block:: bash

        musicdb database add album /data/music/Artist/2000\ -\ New\ Album

    Update an existing song

    .. code-block:: bash

        musicdb database update song /tmp/01\ newsong.flac /data/music/Artist/2000\ -\ Album/01\ oldsong.mp3
        # only the song number must be identical!

"""

import argparse
import os
from lib.modapi         import MDBModule
from mdbapi.database    import MusicDBDatabase
import traceback

class database(MDBModule, MusicDBDatabase):
    def __init__(self, config, database):
        MusicDBDatabase.__init__(self, config, database)


    def CMD_Add(self, target, path):
        print("\033[1;34m - Adding following \033[1;36m" + target + "\033[1;34m to database:\033[0;36m " + path)
        try:
            if target == "artist":
                self.AddArtist(path)
            elif target == "album":
                self.AddAlbum(path)
            elif target == "song":
                self.AddSong(path)
            else:
                print("\033[1;31mInvalid target!")
                return None
            print("\033[1;32mdone")
        except Exception as e:
            print("\033[1;31mFAILED with error: %s"%(str(e)))


        # propergate changes
        print("\033[1;34m - Trying to signal \033[1;36mMusicDB-Server\033[1;34m to update his cache…\033[1;31m")
        self.UpdateServerCache()
        print("\033[1;32mdone")
        return None



    def CMD_Update(self, target, srcpath, dstpath):
        print("\033[1;34m - Updating \033[1;36m" + target + "\033[1;34m:\033[0;36m " + dstpath)
        if target == "song":
            if not self.UpdateSongPath(srcpath, dstpath):
                print("\033[1;31mUpdate failed! - See log file and check " + dstpath)
            else:
                print("\033[1;32mdone")

        else:
            print("\033[1;31mInvalid target!")
            return None

        # propergate changes
        print("\033[1;34m - Trying to signal \033[1;36mMusicDB-Server\033[1;34m to update his cache…\033[1;31m")
        self.UpdateServerCache()
        print("\033[1;32mdone")
        return None



    def CMD_GetLyrics(self, target, path):
        print("\033[1;34mAdding lyrics to following \033[1;36m" + target + "\033[1;34m:\033[0;36m" + path)
        if target == "song":
            self.AddLyricsFromFile(path)

        elif target == "album":
            path  = self.fs.RemoveRoot(path) # remove the path to the musicdirectory
            album = self.db.GetAlbumByPath(path)
            songs = self.db.GetSongsByAlbumId(album["id"])
            
            for song in tqdm(songs, unit="songs"):
                self.AddLyricsFromFile(song["path"])

        elif target == "artist":
            path   = self.fs.RemoveRoot(path) # remove the path to the musicdirectory
            artist = self.db.GetArtistByPath(path)
            songs  = self.db.GetSongsByArtistId(artist["id"])
            
            for song in tqdm(songs, unit="songs"):
                self.AddLyricsFromFile(song["path"])

        print("\033[1;32mdone")
        return None




    def CMD_CheckPath(self, target, path):
        print("\033[1;34mChecking following \033[1;36m" + target + "\033[1;34m path:\033[0;36m" + path)
        if self.TryAnalysePathFor(target, path):
            print("\033[1;34m Path is \033[1;32mOK\033[0m")
        else:
            print("\033[1;34m Path is \033[1;31minvalid\033[0m")
        return None



    @staticmethod
    def MDBM_CreateArgumentParser(parserset, modulename):
        parser = parserset.add_parser(modulename, help="do database management")
        parser.set_defaults(module=modulename)

        subp   = parser.add_subparsers(title="Commands", metavar="command", help="database commands")
        
        addparser = subp.add_parser("add", help="add target to database")
        addparser.add_argument("target", action="store", choices=["artist","album","song"], help="target table")
        addparser.add_argument("path", help="path to an artist, album or song")
        addparser.set_defaults(command="Add")

        addparser = subp.add_parser("update", help="update targets file and database entry")
        addparser.add_argument("target", action="store", choices=["song"], help="target table")
        addparser.add_argument("source", help="path to the new song file")
        addparser.add_argument("path", help="path to the song that shall be updated")
        addparser.set_defaults(command="Update")

        getparser = subp.add_parser("getlyrics", help="read lyrics from file(s) and store them in the database")
        getparser.add_argument("target", action="store", choices=["artist","album","song"], help="target table")
        getparser.add_argument("path", help="path to an artist, album or song directory")
        getparser.set_defaults(command="GetLyrics")

        chkparser = subp.add_parser("check", help="check if the path is in a correct format")
        chkparser.add_argument("target", action="store", choices=["artist","album","song","all"], help="target table")
        chkparser.add_argument("path", help="path to an artist, album, song or root music directory")
        chkparser.set_defaults(command="CheckPath")


    # return exit-code
    def MDBM_Main(self, args):

        # get & check command and its arguments
        if not args.command:
            print("\033[1;31mNo command given to module database!\033[0m")
            return 1

        command = args.command

        try:
            target = args.target
            path   = os.path.abspath(args.path)
        except Exception as e:
            print("\033[1;31mInvalid command line parameter!\033[0m")
            print(e)
            return 1

        if not self.TryAnalysePathFor(target, path):
            print("\033[1;31mERROR:\033[0m Invalid path or target")
            print("\t%s does not exist or does not fit to target %s" % (path, target))
            return 1

        # execte command
        try:
            if command == "Add":
                exitcode = self.CMD_Add(target, path)
            elif command == "Update":
                source = os.path.abspath(args.source)
                exitcode = self.CMD_Update(target, source, path)
            elif command == "GetLyrics":
                exitcode = self.CMD_GetLyrics(target, path)
            elif command == "CheckPath":
                exitcode = self.CMD_CheckPath(target, path)
            return exitcode
        except Exception as e:
            print("\033[1;31mFATAL ERROR:");
            print(e)
            traceback.print_exc()
            return 1

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

