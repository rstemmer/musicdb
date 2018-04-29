# MusicDB,  a music manager with web-bases UI that focus on music.
# Copyright (C) 2018  Ralf Stemmer <ralf.stemmer@gmx.net>
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
This module manages the mp3 cache used by MusicDB.
It does the following things:

    * Remove old files from the cache
    * Cache new files

Caching new files means, that they will be transcoded into the mp3 file format.
Furthermore the ID3 tags will be updated with clean information.

Examples:

    Updating the cache:

    .. code-block:: bash

        musicdb cache update
        
"""

import argparse
from lib.modapi         import MDBModule
from mdbapi.musiccache  import MusicCache
from tqdm               import tqdm


class cache(MDBModule, MusicCache):
    def __init__(self, config, database):
        MusicCache.__init__(self, config, database)


    def UpdateCache(self):
        """
        This method checks for all songs in the database, if they are cached.
        If not, they will be.

        Files inside the cache that are not needed anymore will be removed.

        The process is done in the following steps:

            #. Find all files inside the cache using :meth:`mdbapi.musiccache.MusicCache.GetAllCachedFiles`
            #. Getting all artists, albums and songs from the Music Database
            #. Removing old artists, albums and songs from the cache using :meth:`mdbapi.musiccache.MusicCache.RemoveOldArtists`. :meth:`mdbapi.musiccache.MusicCache.RemoveOldAlbums` and :meth:`mdbapi.musiccache.MusicCache.RemoveOldSongs`
            #. Calling for each song in the database :meth:`mdbapi.musiccache.MusicCache.Add` which adds none existing songs into the cache.

        Returns:
            *Nothing*
        """
        # Get all cached files
        print("\033[1;35m [1/4] \033[1;34mSeaching all files inside the cache …\033[0m")
        cartistpaths, calbumpaths, csongpaths = self.GetAllCachedFiles()

        # Get all entries from the database
        print("\033[1;35m [2/4] \033[1;34mGetting all artists, albums and songs from the database …\033[0m")
        mdbartists = self.db.GetAllArtists()
        mdbalbums  = self.db.GetAllAlbums()
        mdbsongs   = self.db.GetAllSongs()

        # Remove old data from the cache
        print("\033[1;35m [3/4] \033[1;34mRemoving outdated files from the cache …\033[0m")
        self.RemoveOldArtists(cartistpaths, mdbartists)
        self.RemoveOldAlbums( calbumpaths,  mdbalbums )
        self.RemoveOldSongs(  csongpaths,   mdbsongs  )

        # Refresh cache
        print("\033[1;35m [4/4] \033[1;34mChecking for new files in the cache and adding them …\033[0;36m")
        for song in tqdm(mdbsongs):
            self.Add(song)



    @staticmethod
    def MDBM_CreateArgumentParser(parserset, modulename):
        #parser = parserset.add_parser(modulename, help="Manage the mp3 cache")
        parser = parserset.add_parser(modulename, help="WILL NOT BE USED IN MUSICDB")
        parser.set_defaults(module=modulename)

        subp   = parser.add_subparsers(title="Commands", metavar="command", help="cache commands")
        
        updateparser = subp.add_parser("update", help="updates the mp3 cache")
        updateparser .set_defaults(command="update")



    # return exit-code
    def MDBM_Main(self, args):
        print("\033[1;33mThe mp3 cache will not be used in MusicDB!\033[1;30m\nThis command does nothing!\033[0m")
        return 0

        # get & check command and its arguments
        try:
            command = args.command
        except:
            print("\033[1;31mNo command given to module cache!\033[0m")
            return 1


        if command == "update":
            self.UpdateCache()

        return 0


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

