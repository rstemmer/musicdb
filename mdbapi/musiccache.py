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
This class manages the music cache.
This cache is used for the following features of MusicDB:

    #. **Streaming:** Instead of on-the-fly transcoding, MusicDB uses this cache.
    #. **Export:** This cache can be used as a clean base for exporting music to other devices. (The mobile app will use this cache as source)
    #. **HTML5-Source:** The WebUI can use this cache as clean source to access the music via HTML5-Audio-Tags.


Features and Constraints
------------------------

    * Audio files are 320kbps mp3 files
        * They have clean and valid Unicode ID3v2.3 tags
        * They have artworks with a resolution of 500x500 pixels
    * File names have the following scheme: ``ArtistID/AlbumID/SongID:Checksum.mp3``
    * All files in the cache are managed by MusicDB and should not be accessed by any user or other software


Configuration
-------------

Most features of the cache are strict and cannot be configured.
Only the place where the cached files will be stored can be defined in the *musicdb.ini* file:

    .. block-code:: ini
        
        ; Example of the mp3 cache configuration
        [music]
        cache=/opt/musicdb/data/mp3cache



Updating the Cache
------------------

For updating the cache, call the MusicDB Commandline Module :mod:`~mod.cache`.

    .. code-block:: bash

        musicdb cache update


Examples
--------

Add a song to the cache
^^^^^^^^^^^^^^^^^^^^^^^

This example adds a new song to the cache using the :meth:`MusicCache.Add` method.

    .. code-block:: python

        database = MusicDatabase("./music.db")
        config   = MusicDBConfig("./musicdb.ini")
        cache    = MusicCache(config, database)

        # Add song
        song   = database.GetSongById(1000)
        retval = cache.Add(song)
        if retval == False:
            print("Adding %s failed! - See log file for details."%(song["name"]))


Get a songs path inside the case
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This example gets the path to a cached song using the :meth:`MusicCache.GetSongPath` method.

    .. code-block:: python

        database = MusicDatabase("./music.db")
        config   = MusicDBConfig("./musicdb.ini")
        cache    = MusicCache(config, database)

        # Get song
        song = database.GetSongById(1000)
        path = cache.GetSongPath(song)
        if not path:
            print("Song %s not cached!"%(song["name"]))


"""

import os
from lib.cfg.musicdb    import MusicDBConfig
from lib.db.musicdb     import MusicDatabase
from lib.filesystem     import Filesystem
from lib.fileprocessing import Fileprocessing
from lib.cache          import ArtworkCache
from tqdm               import tqdm
import logging

class MusicCache(object):
    """
    Args:
        config: MusicDB configuration object
        database: MusicDB database

    Raises:
        TypeError: when *config* or *database* not of type :class:`~lib.cfg.musicdb.MusicDBConfig` or :class:`~lib.db.musicdb.MusicDatabase`
    """
    def __init__(self, config, database):
        if type(config) != MusicDBConfig:
            print("\033[1;31mFATAL ERROR: Config-class of unknown type!\033[0m")
            raise TypeError("config argument not of type MusicDBConfig")
        if type(database) != MusicDatabase:
            print("\033[1;31mFATAL ERROR: Database-class of unknown type!\033[0m")
            raise TypeError("database argument not of type MusicDatabase")

        self.db     = database
        self.cfg    = config
        self.fs     = Filesystem(self.cfg.music.cache)
        self.fileprocessor = Fileprocessing(self.cfg.music.cache)
        self.artworkcache  = ArtworkCache(self.cfg.artwork.path)



    def GetAllCachedFiles(self):
        """
        This method returns three lists of paths of all files inside the cache.
        The tree lists are the following:

            #. All artist directories
            #. All album paths
            #. All song paths

        Returns:
            A tuple of three lists: (Artist-Paths, Album-Paths, Song-Paths)

        Example:

            .. code-block:: python

                (artists, albums, songs) = cache.GetAllCachedFiles()

                print("Albums in cache:")
                for path in albums:
                    name = musicdb.GetAlbumByPath(path)["name"]
                    print(" * " + name)

                print("Files in cache:")
                for path in songs:
                    print(" * " + path)
        """
        # Get all files from the cache
        artistpaths = self.fs.ListDirectory()
        albumpaths  = self.fs.GetSubdirectories(artistpaths)
        songpaths   = self.fs.GetFiles(albumpaths)

        return artistpaths, albumpaths, songpaths



    def RemoveOldArtists(self, cartistpaths, mdbartists):
        """
        This method removes all cached artists when they are not included in the artist list from the database.

        ``cartistpaths`` must be a list of artist directories with the artist ID as directory name.
        From these paths, a list of available artist ids is made and compared to the artist ids from the list of artists returned by the database (stored in ``mdbartists``)

        Is there a path/ID in ``cartistpaths`` that is not in the ``mdbartists`` list, the directory gets removed.
        The pseudo code can look like this:

            .. code-block:: python

                for path in cartistpaths:
                    if int(path) not in [mdbartists["id"]]:
                        self.fs.RemoveDirectory(path)

        Args:
            cartistpaths (list): a list of artist directories in the cache
            mdbartists (list): A list of artist rows from the Music Database

        Returns:
            *Nothing*
        """
        artistids = [artist["id"] for artist in mdbartists]
        cachedids = [int(path)    for path   in cartistpaths]

        for cachedid in cachedids:
            if cachedid not in artistids:
                self.fs.RemoveDirectory(str(cachedid))



    def RemoveOldAlbums(self, calbumpaths, mdbalbums):
        """
        This method compares the available album paths from the cache with the entries from the Music Database.
        If there are albums that do not match the database entries, then the cached album will be removed.

        Args:
            calbumpaths (list): a list of album directories in the cache (scheme: "ArtistID/AlbumID")
            mdbalbums (list): A list of album rows from the Music Database

        Returns:
            *Nothing*
        """
        # create "artistid/albumid" paths
        validpaths = [os.path.join(str(album["artistid"]), str(album["id"])) for album in mdbalbums]

        for cachedpath in calbumpaths:
            if cachedpath not in validpaths:
                self.fs.RemoveDirectory(cachedpath)



    def RemoveOldSongs(self, csongpaths, mdbsongs):
        """
        This method compares the available song paths from the cache with the entries from the Music Database.
        If there are songs that do not match the database entries, then the cached song will be removed.

        Args:
            csongpaths (list): a list of song files in the cache (scheme: "ArtistID/AlbumID/SongID:Checksum.mp3")
            mdbsongs (list): A list of song rows from the Music Database

        Returns:
            *Nothing*
        """
        # create song paths
        validpaths = []
        for song in mdbsongs:
            path = self.GetSongPath(song)
            if path:
                validpaths.append(path)

        for cachedpath in csongpaths:
            if cachedpath not in validpaths:
                self.fs.RemoveFile(cachedpath)



    def GetSongPath(self, mdbsong, absolute=False):
        """
        This method returns a path following the naming scheme for cached songs (``ArtistID/AlbumID/SongID:Checksum.mp3``).
        It is not guaranteed that the file actually exists.

        Args:
            mdbsong: Dictionary representing a song entry form the Music Database
            absolute: Optional argument that can be set to ``True`` to get an absolute path, not relative to the cache directory.

        Returns:
            A (possible) path to the cached song (relative to the cache directory, ``absolute`` got not set to ``True``).
            ``None`` when there is no checksum available. The checksum is part of the file name.
        """
        # It can happen, that there is no checksum for a song.
        # For example when an old installation of MusicDB got not updated properly.
        # Better check if the checksum is valid to avoid any further problems.
        if len(mdbsong["checksum"]) != 64:
            logging.error("Invalid checksum of song \"%s\": %s \033[1;30m(64 hexadecimal digit SHA265 checksum expected. Try \033[1;34mmusicdb repair --checksums \033[1;30mto fix the problem.)",
                    mdbsong["path"], mdbsong["checksum"])
            return None

        path  = os.path.join(str(mdbsong["artistid"]), str(mdbsong["albumid"])) # ArtistID/AlbumID
        path  = os.path.join(path, str(mdbsong["id"]))                          # ArtistID/AlbumID/SongID
        path += ":" + mdbsong["checksum"] + ".mp3"                              # ArtistID/AlbumID/SongID:Checksum.mp3

        if absolute:
            path = self.fs.AbsolutePath(path)

        return path



    def Add(self, mdbsong):
        """
        This method checks if the song exists in the cache.
        When it doesn't, the file will be created (this may take some time!!).

        This process is done in the following steps:

            #. Check if song already cached. If it does, the method returns with ``True``
            #. Create directory tree if it does not exist. (``ArtistID/AlbumID/``)
            #. Convert song to mp3 (320kbp/s) and write it into the cache.
            #. Update ID3 tags. (ID3v2.3.0, 500x500 pixel artworks)

        Args:
            mdbsong: Dictionary representing a song entry form the Music Database

        Returns:
            ``True`` on success, otherwise ``False``
        """
        path = self.GetSongPath(mdbsong)
        if not path:
            return False

        # check if file exists, and create it when not.
        if self.fs.IsFile(path):
            return True

        # Create directory if not exists
        directory = os.path.join(str(mdbsong["artistid"]), str(mdbsong["albumid"])) # ArtistID/AlbumID
        if not self.fs.IsDirectory(directory):
            self.fs.CreateSubdirectory(directory)

        # Create new mp3
        srcpath = os.path.join(self.cfg.music.path, mdbsong["path"])
        dstpath = self.fs.AbsolutePath(path)
        retval = self.fileprocessor.ConvertToMP3(srcpath, dstpath)
        if retval == False:
            logging.error("Converting %s to %s failed!", srcpath, dstpath)
            return False
        os.sync()

        # Optimize new mp3
        mdbalbum  = self.db.GetAlbumById(mdbsong["albumid"])
        mdbartist = self.db.GetArtistById(mdbsong["artistid"])

        try:
            relartworkpath = self.artworkcache.GetArtwork(mdbalbum["artworkpath"], "500x500")
        except Exception as e:
            logging.error("Getting artwork from cache failed with exception: %s!", str(e))
            logging.error("   Artwork: %s, Scale: %s", mdbalbum["artworkpath"], "500x500")
            return False

        absartworkpath = os.path.join(self.cfg.artwork.path, relartworkpath)
        
        retval = self.fileprocessor.OptimizeMP3Tags(mdbsong, mdbalbum, mdbartist, 
                srcpath        = path, 
                dstpath        = path,
                absartworkpath = absartworkpath,
                forceID3v230   = True)
        if retval == False:
            logging.error("Optimizing %s failed!", path)
            return False

        return True







# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

