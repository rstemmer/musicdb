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

    ``add``: 
        Add new artist, album, song or video to the database.
        Direct interface to:

            * If the path addresses a song: :meth:`musicdb.mdbapi.music.MusicDBMusic.AddSong`
            * If the path addresses a album: :meth:`musicdb.mdbapi.music.MusicDBMusic.AddAlbum`
            * If the path addresses a artist: :meth:`musicdb.mdbapi.music.MusicDBMusic.AddArtist`
            * If the path addresses a video: :meth:`musicdb.mdbapi.music.MusicDBMusic.AddVideo`

    ``update``:
        Allows updating the database when a song or video file got changed or exchanged.
        This sub command is partially redundant to the :doc:`/mod/repair` module.
        Compared to the repair module this method is more precise and can handle more uncommon situations.

        It is assumed that the path of the file did not changed.
        In case it is different to the path stored in the database you need to provide the old path via the optional parameter ``--oldpath`` 
        and use the new path as positional ``path`` parameter. (See Example at the end of this section)
        The *old path* is used to find the database entry.

        It interfaces the following methods:

            * For songs: :meth:`musicdb.mdbapi.music.MusicDBMusic.UpdateSong`
            * For videos: :meth:`musicdb.mdbapi.music.MusicDBMusic.UpdateVideo`

        After the update you may want to update the video artworks via :doc:`/mod/videoframes`.

    ``remove``:
        Removes an artist, album or song from the database.
        Only the database entries get removed.
        The files will not be touched.

    ``getlyrics``: 
        Search in song files for lyrics.
        This is done by calling for each song file :meth:`musicdb.mdbapi.music.MusicDBMusic.AddLyricsFromFile`
        
    ``check``: 
        Check the given path if it is a valid artist, album or song path.
        This is done by calling :meth:`musicdb.mdbapi.music.MusicDBMusic.TryAnalysePathFor`.

.. attention::

    TODO: DEPRECATED - This behavior changed in MusicDB 8.0.0

    While adding a new artist, album or song to the database, the file and directory attributes 
    and ownership gets changed to the configured one in the MusicDB Configuration.

    And after adding the new data, the command (``refresh``) gets written into the servers named pipe
    to update its cache.


Examples:

    .. code-block:: bash

        musicdb database add /data/music/Artist/2000\ -\ New\ Album

        musicdb database remove /data/music/Bad\ Artist

        musicdb database add /data/music/Artist/2000\ -\ Video.m4v

        # musicdb database update [-h] [--oldpath OLDPATH] path
        musicdb database update /data/music/Artist/2000\ -\ Video.m4v
        musicdb database update --newpath /data/music/Artist/2000\ -\ Video.m4v /data/music/Artist/2000\ -\ Video.webm


"""

import argparse
import os
from musicdb.lib.modapi         import MDBModule
from musicdb.mdbapi.music       import MusicDBMusic
from tqdm               import tqdm
import traceback

class database(MDBModule, MusicDBMusic):
    def __init__(self, config, database):
        MusicDBMusic.__init__(self, config, database)


    def CMD_Add(self, target, path):
        print("\033[1;34mAdding following \033[1;36m" + target + "\033[1;34m to database:\033[0;36m %s \033[1;34m… "%(path), end="")
        if target == "artist":
            self.AddArtist(path)
        elif target == "album":
            self.AddAlbum(path)
        elif target == "song":
            self.AddSong(path)
        elif target == "video":
            if not self.AddVideo(path):
                print("\033[1;31mfailed")
                return None
        else:
            raise ValueError("Invalid target! Target must be \"artist\", \"album\", \"song\" or \"video\".")
        print("\033[1;32mdone")
        return None



    def CMD_Update(self, target, path, oldpath):

        if oldpath == None:
            oldpath = path

        # 1. Get target ID
        if target == "song":
            song = self.db.GetSongByPath(oldpath)
            if song == None:
                raise ValueError("Song "+oldpath+" not found in database.")
            targetid = song["id"]

        elif target == "video":
            video = self.db.GetVideoByPath(oldpath)
            if video == None:
                raise ValueError("Video "+oldpath+" not found in database.")
            targetid = video["id"]

        else:
            raise ValueError("Invalid target! Target must be \"song\" or \"video\".")

        print("\033[1;34mUpdating following \033[1;36m" + target + "\033[1;34m:\033[0;36m %s \033[1;34m… "%(path), end="")
        if target == "song":
            self.UpdateSong(targetid, path)
        elif target == "video":
            self.UpdateVideo(targetid, path)
        print("\033[1;32mdone")
        return None



    def CMD_Remove(self, target, abspath):

        try:
            path = self.musicdirectory.RemoveRoot(abspath)
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
        return None



    def CMD_GetLyrics(self, target, path):
        print("\033[1;34mAdding lyrics to following \033[1;36m" + target + "\033[1;34m:\033[0;36m %s \033[1;34m… "%(path), end="")
        if target == "song":
            self.AddLyricsFromFile(path)

        elif target == "album":
            path  = self.musicdirectory.RemoveRoot(path) # remove the path to the music directory
            album = self.db.GetAlbumByPath(path)
            songs = self.db.GetSongsByAlbumId(album["id"])
            
            for song in tqdm(songs, unit="songs"):
                self.AddLyricsFromFile(song["path"])

        elif target == "artist":
            path   = self.musicdirectory.RemoveRoot(path) # remove the path to the music directory
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

        addparser = subp.add_parser("add", help="add target to database")
        addparser.add_argument("path", help="path to an artist, album, song or video")
        addparser.set_defaults(command="Add")

        updateparser = subp.add_parser("update", help="update target in database")
        updateparser.add_argument("path", help="path to a song or video")
        updateparser.set_defaults(command="Update")

        updateparser.add_argument("--oldpath",   action="store", type=str, default=None,
                help="The path of the old file in the database")

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

        # Handle optional oldpath argument
        #if args.oldpath:
        #    oldpath = os.path.abspath(args.oldpath)
        #    oldpath = self.musicdirectory.RemoveRoot(oldpath) # remove the path to the music directory
        #else:
        oldpath = None

        # Execute command
        try:
            if command == "Add":
                exitcode = self.CMD_Add(target, path)
            elif command == "Update":
                exitcode = self.CMD_Update(target, path, oldpath)
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

