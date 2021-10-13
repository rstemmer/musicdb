# MusicDB,  a music manager with web-bases UI that focus on music.
# Copyright (C) 2021  Ralf Stemmer <ralf.stemmer@gmx.net>
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
This class handles the upload of music files to external storages.
Before most of the methods can be used, the mountpoint of the external storage must be set using :meth:`~musicdb.mdbapi.extern.MusicDBExtern.SetMountpoint`.
The default mount poiunt is ``"/mnt"``.
There are three main tasks this class implements:

* `Initializing a Storage`_
* `Updating a Storage`_ 
* `Handling Toxic Environments`_


Initializing a Storage
----------------------

Each storage must have a directory configured in the main MusicDB-Configuration, that holds some states.
This directory can be created and initialized using the :meth:`~musicdb.mdbapi.extern.MusicDBExtern.InitializeStorage`.
It is possible to check if the storage was already initialized using the method :meth:`~musicdb.mdbapi.extern.MusicDBExtern.IsStorageInitialized`.

Example:

    .. code-block:: python

        database = MusicDatabase("./music.db")
        config   = MusicDBConfig("./musicdb.ini")
        extern   = MusicDBExtern(config, database)
        extern.SetMountpoint("/mnt")

        # Initialize mounted storage if not done yet
        if not extern.IsStorageInitialized():
            extern.InitializeStorage()

After initializing, a directory is created and a bare *config.ini* is copied from the *MusicDB share directory*.
The name of the directory, the config-source-file and the state-file-names can be configured in the MusicDB-Config file.
It is recommended to use a hidden directory for the states on the external storage.
MusicDB must have write access to the directory and its files.

Storage Configuration
^^^^^^^^^^^^^^^^^^^^^

The storage configuration can be used to adapt to the environment other software or devices require to use the music that will be stored on it.
More details about `Handling Toxic Environments`_ can be found in the related subsection.

Template for such a storage configuration:

    .. literalinclude:: ../../../share/extconfig.ini
        :language: ini

The State-File
^^^^^^^^^^^^^^

The state-file mostly called *songmap* is a Comma Separated Value (csv) file.
It contains a row for each song on the storage and is used to identify the song.
This is mandatory because the path on the external storage may differ from the paths of the music collection. 
This can happen for example by transcoding or renaming to a FAT compatible path.

Each row has the following columns:

    * Original file path (relative)
    * File path on the external storage (relative)

The csv file must have the following dialect:

    * delimiter:  ``,`` 
    * escapechar: ``\``
    * quotechar:  ``"``
    * quoting:    ``csv.QUOTE_NONNUMERIC``

Example:

    .. code-block:: python

       "Rammstein/2001 - Mutter/03 Sonne.m4a","Rammstein/2001 - Mutter/03 Sonne.mp3" 

This file gets generated by the method :meth:`~musicdb.mdbapi.extern.MusicDBExtern.WriteSongmap` 
and can be read by :meth:`~musicdb.mdbapi.extern.MusicDBExtern.ReadSongmap`.
Usually the user should never touch this file.


Updating a Storage
------------------

Updating an external storage device like a mp3-player or a SD-Card, the :meth:`~musicdb.mdbapi.extern.MusicDBExtern.UpdateStorage` method can be used.

Example:

    .. code-block:: python

        database = MusicDatabase("./music.db")
        config   = MusicDBConfig("./musicdb.ini")
        extern   = MusicDBExtern(config, database)
        extern.SetMountpoint("/mnt")

        # Update storage if it is valid
        if extern.IsStorageInitialized():
            extern.UpdateStorage()


Handling Toxic Environments
---------------------------

A *toxic environment* is a device that has some limitations and constraints the exported music has to fulfill.
For example, my car can only read mp3 files, has a path length limit of 256 characters and can only access a FAT filesystem.
My mp3-player does not have that many constraints, but slows down if the album covers are too large and have to be scaled down the mp3 players screen resolution.
Those limitations can be handled by MusicDBExtern.

There are several methods to handle toxic environments.
They can be activated in the config file that will be generated when the storage gets initialized.

The following methods will be applied if activated in the config:

    * :meth:`~musicdb.mdbapi.extern.MusicDBExtern.ReducePathLength` if the pathlength is limited
    * :meth:`musicdb.lib.fileprocessing.Fileprocessing.ConvertToMP3` if only mp3-files are allowed
    * :meth:`musicdb.lib.fileprocessing.Fileprocessing.OptimizeMP3Tags` to scale artwork and make proper ID3 tags
    * :meth:`musicdb.lib.fileprocessing.Fileprocessing.OptimizeM4ATags` make proper meta tags for m4a files
    * :meth:`~musicdb.mdbapi.extern.MusicDBExtern.FixPath` to handle unicode in paths

    .. warning::

        When optimizing M4A-Tags, the album artwork gets lost.
        This is a `bug <https://trac.ffmpeg.org/ticket/2798>`_ in ``ffmpeg``. I did not find any good workarounds yet.

"""

import os
import re
import shutil
import sys
import csv
from musicdb.lib.cfg.extern     import ExternConfig
from musicdb.lib.cfg.musicdb    import MusicDBConfig
from musicdb.lib.db.musicdb     import MusicDatabase
from musicdb.lib.filesystem     import Filesystem
from musicdb.lib.fileprocessing import Fileprocessing
from musicdb.lib.cache          import ArtworkCache
from tqdm               import tqdm
import logging

class MusicDBExtern(object):
    """
    Args:
        config: MusicDB configuration object
        database: MusicDB database

    Raises:
        TypeError: when *config* or *database* not of type :class:`~musicdb.lib.cfg.musicdb.MusicDBConfig` or :class:`~musicdb.lib.db.musicdb.MusicDatabase`
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
        self.mp     = None
        self.fs     = Filesystem("/")
        self.fileprocessor = Fileprocessing("/")
        self.artworkcache  = ArtworkCache(self.cfg.directories.artwork)
        self.SetMountpoint("/mnt")    # initialize self.mp with the default mount point /mnt



    def CheckForDependencies(self) -> bool:
        """
        Checks for dependencies required by this module.
        Those dependencies are ``ffmpeg`` and `id3edit <https://github.com/rstemmer/id3edit>_`.

        If a module is missing, the error message will be printed into the log file
        and also onto the screen (stderr)

        Returns:
            ``True`` if all dependencies exist, otherwise ``False``.
        """
        nonemissing = True # no dependency is missing, as long as no check returns false

        if not self.fileprocessor.ExistsProgram("ffmpeg"):
            logging.error("Required dependency \"ffmpeg\" missing!")
            print("\033[1;31mRequired dependency \"ffmpeg\" missing!", file=sys.stderr)
            nonemissing = False

        if not self.fileprocessor.ExistsProgram("id3edit"):
            logging.error("Required dependency \"id3edit\" missing!")
            print("\033[1;31mRequired dependency \"id3edit\" missing!", file=sys.stderr)
            nonemissing = False

        return nonemissing



    # INITIALIZATION METHODS
    ########################


    def SetMountpoint(self, mountpoint="/mnt"):
        """
        Sets the mountpoint MusicDBExtern shall work on.
        If the mountpoint does not exists, ``False`` gets returned.
        The existence of a mountpoint does not guarantee that the device is mounted.
        Furthermore the method does not check if the mounted device is initialized - this can be done by calling :meth:`~musicdb.mdbapi.extern.MusicDBExtern.IsStorageInitialized`.

        Args:
            mountpoint (str): Path where the storage that shall be worked on is mounted

        Returns:
            ``True`` if *mountpoint* exists, ``False`` otherwise.
        """
        if not os.path.exists(mountpoint):
            logging.error("\033[1;31mERROR: "+mountpoint+" is not a valid mountpoint/directory!\033[0m")
            return False
        self.mp = mountpoint
        logging.debug("set mountpoint to %s", self.mp)
        return True


    def IsStorageInitialized(self):
        """
        This method checks for the state-directory and the storage configuration file inside the state directory.
        If both exists, the storage is considered as initialized and ``True`` gets returned.

        Returns:
            ``True`` if storage is initialized, otherwise ``False``
        """
        if not self.mp:
            logging.error("mountpoint-variable not set. Missing SetMountpoint call!")
            return False

        extstatedir = os.path.join(self.mp,     self.cfg.extern.statedir)    # directory for the state config files
        extcfgfile  = os.path.join(extstatedir, self.cfg.extern.configfile)  # config file for the external storage

        if not os.path.exists(extstatedir):
            logging.debug("State directory missing!")
            return False
        if not os.path.exists(extcfgfile):
            logging.debug("Config file missing!")
            return False

        return True


    def InitializeStorage(self):
        """
        This method creates the state-directory inside the mountpoint.
        Then a template of the storage configuration gets copied inside the new creates state-directory

        Returns:
            ``True`` on success, else ``False``
        """
        if not self.mp:
            logging.error("mountpoint-variable not set. Missing SetMountpoint!")
            return False

        extstatedir = os.path.join(self.mp,     self.cfg.extern.statedir)    # directory for the state config files
        extcfgfile  = os.path.join(extstatedir, self.cfg.extern.configfile)  # config file for the external storage

        try:
            logging.info("Creating %s" % extstatedir)
            os.makedirs(extstatedir)

            logging.info("Creating %s" % extcfgfile)
            shutil.copy(self.cfg.extern.configtemplate, extcfgfile)

        except Exception as e:
            logging.error("Initializing external storage failed!")
            logging.error(e)
            return False

        logging.info("\033[1;32mCreated new MDB-state at \033[0;36m %s" % extstatedir)
        return True



    # OPTIMIZATION METHODS
    ######################


    def ReducePathLength(self, path):
        """
        This method reduces a path length to hopefully fit into a path-length-limit.
        The reduction is done by removing the song name from the path.
        Everything left is the directory the song is stored in, the song number and the file extension.

        Example:

            .. code-block:: python

                self.ReducePathLength("artist/album/01 very long name.mp3")
                # returns "artist/album/01.mp3"
                self.ReducePathLength("artist/album/1-01 very long name.mp3")
                # returns "artist/album/1-01.mp3"

        Args:
            path (str): path of the song

        Returns:
            shortend path as string if successfull, ``None`` otherwise
        """
        # "directory/num name.ext" -> "directory", "num name.ext"
        directory, songfile = os.path.split(path)
        # "num name.ext" -> "num name", "ext"
        name, extension = os.path.splitext(songfile)
        # "num name" -> "num"
        number = name.split(" ")[0]

        newpath  = os.path.join(directory, number)
        newpath += extension;

        return newpath


    def FixPath(self, string, charset):
        """
        This method places characters that are invalid for *charset* by a valid one.

            #. Replaces ``?<>\:*|"`` by ``_``
            #. Replaces ``äöüÄÖÜß`` by ``aouAOUB``

        .. warning::

            Obviously, this method is incomplete and full of shit. It must and will be replaced in future.

        Example:

            .. code-block:: python

                self.FixPath("FAT/is f*cking/scheiße.mp3")
                # returns "FAT/is f_cking/scheiBe.mp3"
        
        Args:
            string (str): string that shall be fixed
            charset (str): until now, only ``"FAT"`` is considered. Other sets will be ignored

        Returns:
            A string that is valid for *charset*
        """
        # 1. replace all bullshit-chars
        good = "_"

        if charset == "FAT":
            bad = "?<>\\:*|\""
        else:
            return string

        fixed = re.sub("["+bad+"]", good, string)

        # 2. fix unicode problems
        # TODO: Rebuild this method. Consider the whole unicode space!
        if charset in ["FAT","ASCII"]:
            fixed = fixed.replace("ä", "a")
            fixed = fixed.replace("ö", "o")
            fixed = fixed.replace("ü", "u")
            fixed = fixed.replace("Ä", "A")
            fixed = fixed.replace("Ö", "O")
            fixed = fixed.replace("Ü", "U")
            fixed = fixed.replace("ß", "B") # This is ScheiBe

        return fixed



    # UPDATE METHODS
    ################

    def ReadSongmap(self, mappath):
        """
        This method reads the song map that maps relative song paths from the collection to relative paths on the external storage.

        Args:
            mappath (str): absolute path to the songmap

        Returns:
            ``None`` if there is no songmap yet. Otherwise a list of tuples (srcpath, dstpath) is returned.
        """

        # if there is no song-list, assume we are in a new environment
        if not os.path.exists(mappath):
            logging.warning("No songlist found under %s. \033[0;33m(assuming this is the first run and there are no songs yet)", mappath)
            return None

        with open(mappath) as csvfile:
            rows = csv.reader(csvfile, 
                    delimiter  =",", 
                    escapechar ="\\", 
                    quotechar  ="\"", 
                    quoting    =csv.QUOTE_NONNUMERIC)

            # Format of the lines: rel. source-path, rel. destination-path
            rows    = list(rows) # Transform csv-readers internal iteratable object to a python list.
            songmap = []         # for a list of tuple (src, dst)
            for row in tqdm(rows):
                songmap.append((row[0], row[1]))

        return songmap


    def UpdateSongmap(self, songmap, mdbpathlist):
        """
        This method updates the songmap read with :meth:`~musicdb.mdbapi.extern.MusicDBExtern.ReadSongmap`.
        Therefore, new source-paths will be added, and old one will be removed.
        The new ones will be tuple of ``(srcpath, None)`` added to the list.
        Removing songs will be done by replacing the sourcepath with ``None``.
        This leads to a list of tuple, with each tuple representing one of the following states:

            #. ``(srcp, dstp)`` Nothing to do: Source and Destination files exists
            #. ``(srcp, None)`` New file in the collection that must be copied to the external storage
            #. ``(None, dstp)`` Old file on the storage that must be removed

        Args:
            songmap: A list of tuples representing the external storage state. If ``None``, an empty map will be created.
            mdbpathlist: list of relative paths representing the music colletion.

        Returns:
            The updated songmap gets returned
        """
        # if there is no songmap, create one
        if not songmap:
            songmap = []

        songupdatemap = []

        # Check for outdated entries in the songmap
        for entry in songmap:
            # if srcpath still in collection, otherwise remove ist
            if entry[0] in mdbpathlist:
                mdbpathlist.remove(entry[0])    # no need to check this entry again
                songupdatemap.append(entry)
            else:
                songupdatemap.append((None, entry[1]))

        # add the rest of the pathlist to the map
        for path in mdbpathlist:
            songupdatemap.append((path, None))

        return songupdatemap


    def RemoveOldSongs(self, songmap, extconfig):
        """
        Remove all songs that have a destination-entry but no source-entry in the songmap.
        This constellation means that there is a file on the storage that does not exist in the music collection.

        Args:
            songmap: A list of tuple representing the external storage state.
            extconfig: Instance of the external storage configuration.

        Returns:
            The updated songmap without the entries of the files that were removed in this method
        """
        # read config
        musicdir = extconfig.paths.musicdir

        # remove all old files
        for entry in tqdm(songmap):
            # skip if the destination path has a related source path
            if entry[0] != None:
                continue

            # Generate all absolute paths that will be considered to remove
            abspath = os.path.join(self.mp, musicdir)
            abspath = os.path.join(abspath, entry[1])
            # Separate between song, album and artist
            songpath   = abspath
            albumpath  = os.path.split(songpath)[0]
            artistpath = os.path.split(albumpath)[0]
        
            # remove abandond destination file
            logging.debug("Trying to remove %s", songpath)
            try:
                os.remove(songpath)  # delete file
                os.rmdir(albumpath)  # remove album if there are no more songs
                os.rmdir(artistpath) # remove artist if there are no more albums
            except:
                pass

        # remove all entries from the songmap that hold outdated/abandoned files
        songmap = [ entry for entry in songmap if entry[0] != None ]

        return songmap


    def CopyNewSongs(self, songmap, extconfig):
        """
        This method handles the songs that are new to the collection and not yet copied to the external storage.
        The process is split into two tasks: 

            #. Generate path names for the new files on the external storage
            #. Copy the songs to the external storage

        The copy-process itself is done in another method :meth:`~musicdb.mdbapi.extern.MusicDBExtern.CopySong`.
        In future, the ``CopySong`` method shall be called simultaneously for multiple songs.

        Args:
            songmap: A list of tuples representing the external storage state.

        Returns:
            *songmap* with the new state of the storage. The dstpath-column is set for the copied songs.
        """
        # read configuration
        musicdir  = extconfig.paths.musicdir
        charset   = extconfig.constraints.charset
        pathlimit = extconfig.constraints.pathlen

        # split songmap into "already existing" and "new songs"
        oldsongs = [ entry for entry in songmap if entry[1] != None ]
        newsongs = [ entry for entry in songmap if entry[1] == None ]

        # 1.: generate destination paths for the new songs
        # all pathes are relative!
        for index, entry in enumerate(newsongs):
            srcpath = entry[0]

            # make constraint-compatible destination path
            dstpath = self.FixPath(srcpath, charset)

            # check for length-limit (the +1 is a "/")
            if pathlimit > 0 and len(musicdir) + 1 + len(dstpath) > pathlimit:
                dstpath = self.ReducePathLength(dstpath)

                # check result
                if len(musicdir) + 1 + len(dstpath) > pathlimit:
                    logging.warning(
                            "Path \"%s\" is too long and cannot be shorted to %d characters!"
                            " \033[1;30m(processing song anyway)", 
                            str(dstpath), pathlimit)

            # Add new potential dstpath to the entry 
            # (the extension may change later due to transcoding)
            newsongs[index] = (entry[0], dstpath)

        # 2.: Start the copy-process TODO: Make it in parallel
        with tqdm(total=len(newsongs)) as progressbar:
            for index, element in enumerate(newsongs):
                srcpath, dstpath = element
                dstpath = self.CopySong(srcpath, dstpath, extconfig)
                # same or corrected path, None on error.
                newsongs[index] = (srcpath, dstpath)
                progressbar.update()

        # merge entrie again and return a complete list of the current state of the storage
        songmap = []
        songmap.extend(oldsongs)
        songmap.extend(newsongs)
        return songmap


    def CopySong(self, relsrcpath, reldstpath, extconfig):
        """
        In this method, the copy process is done. This method is the core of this class.
        The copy process is done in several steps:

            #. Preparation of all paths and configurations
            #. Create missing directories
            #. Transcode, optimize, copy file

        It also creates the Artist and Album directory if they do not exist.
        If a song file already exists, the copy-process gets skipped.

        Arguments:
            relsrcpath (str): relative source path to the song that shall be copied
            reldstpath (str): relative destination path. Its extension may be changed due to transcoding.
            extconfig: Instance of the external storage configuration

        Returns:
            On success the updated ``reldstpath`` is returned. It may differ from the parameter due to transcoding the file. Otherwise ``None`` is returned.
        """
        # read config
        musicdir    = extconfig.paths.musicdir
        forcemp3    = extconfig.constraints.forcemp3
        optimizemp3 = extconfig.mp3tags.optimize
        noartwork   = extconfig.mp3tags.noartwork
        prescale    = extconfig.mp3tags.prescale
        forceid3v230= extconfig.mp3tags.forceid3v230
        optimizem4a = extconfig.m4atags.optimize

        # handle paths
        srcextension = os.path.splitext(relsrcpath)[1]
        if forcemp3 and srcextension != ".mp3":
            reldstpath = os.path.splitext(reldstpath)[0] + ".mp3"

        abssrcpath      = os.path.join(self.cfg.directories.music, relsrcpath)

        absdstpath      = os.path.join(self.mp,             musicdir)
        absdstpath      = os.path.join(absdstpath,          reldstpath)
        absdstdirectory = os.path.split(absdstpath)[0]
        
        logging.debug("copying song from %s to %s", abssrcpath, absdstpath)

        # TODO: Add option to force overwriting
        if os.path.exists(absdstpath):
            logging.debug("%s skipped - does already exist", absdstpath)
            return reldstpath
        
        # Create directories if not exits
        if not os.path.exists(absdstdirectory):
            try:
                os.makedirs(absdstdirectory)
            except Exception as e:
                logging.error("Creating directory \"" + absdstdirectory + "\" failed with error %s!"
                        "\033[1;30m (skipping song)",
                        str(e))
                return None

        # Open Music Database
        musicdb = self.db
        # FIXME: Invalid in multithreading env
        # Sadly the Optimization methods for the tags also access self.db.
        # No chance for multithreading in near future

        mdbsong   = musicdb.GetSongByPath(relsrcpath)
        mdbalbum  = musicdb.GetAlbumById(mdbsong["albumid"])
        mdbartist = musicdb.GetArtistById(mdbsong["artistid"])

        # handle artwork if wanted
        if noartwork:
            absartworkpath = None
        else:
            # Remember: paths of artworks are handled relative to the artwork cache
            if prescale:
                try:
                    relartworkpath = self.artworkcache.GetArtwork(mdbalbum["artworkpath"], prescale)
                except Exception as e:
                    logging.error("Getting artwork from cache failed with exception: %s!", str(e))
                    logging.error("   Artwork: %s", mdbalbum["artworkpath"])
                    return False

                absartworkpath = os.path.join(self.cfg.directories.artwork, relartworkpath)

            else:
                absartworkpath = os.path.join(self.cfg.directories.artwork, mdbalbum["artworkpath"])

        # copy the file
        if forcemp3 and srcextension != ".mp3":
            retval = self.fileprocessor.ConvertToMP3(abssrcpath, absdstpath)
            if retval == False:
                logging.error("\033[1;30m(skipping song due to previous error)")
                return None

            os.sync()   # This may help to avoid corrupt files. Conversion and optimization look right

            retval = self.fileprocessor.OptimizeMP3Tags(
                    mdbsong, mdbalbum, mdbartist,
                    absdstpath, absdstpath, 
                    absartworkpath, 
                    forceid3v230)
            if retval == False:
                logging.error("\033[1;30m(skipping song due to previous error)")
                return None

        elif optimizemp3 and srcextension == ".mp3":
            retval = self.fileprocessor.OptimizeMP3Tags(
                    mdbsong, mdbalbum, mdbartist,
                    abssrcpath, absdstpath,
                    absartworkpath, 
                    forceid3v230)
            if retval == False:
                logging.error("\033[1;30m(skipping song due to previous error)")
                return None

        elif optimizem4a and srcextension == ".m4a":
            retval = self.fileprocessor.OptimizeM4ATags(mdbsong, mdbalbum, mdbartist, abssrcpath, absdstpath)
            if retval == False:
                logging.error("\033[1;30m(skipping song due to previous error)")
                return None

        else:
            self.fileprocessor.CopyFile(abssrcpath, absdstpath)

        # return updated relative destination path for the songmap
        return reldstpath



    def WriteSongmap(self, songmap, mappath):
        """
        Writes all valid entries of *songmap* into the state-file.
        This method generates the new state of the external storage.

        A valid entry has a source and a destination path.

        Arguments:
            songmap: A list of tuples representing the external storage state.
            mappath (str): Path to the state-file

        Returns:
            ``None``
        """
        # open songlist (recreate the whole file)
        with open(mappath, "w") as csvfile:
            csvwriter = csv.writer(csvfile, 
                    delimiter  = ",", 
                    escapechar = "\\", 
                    quotechar  = "\"", 
                    quoting    = csv.QUOTE_NONNUMERIC)

            for entry in songmap:
                if entry[0] != None and entry[1] != None:
                    csvwriter.writerow(list(entry))

        return None


    def UpdateStorage(self):
        """
        This method does the whole update process. It consists of the following steps:

        #. Prepare envrionment like determin configfiles and opening them.
        #. Get all song paths from the Music Database
        #. :meth:`~musicdb.mdbapi.extern.MusicDBExtern.ReadSongmap` - Read the current state of the external storage
        #. :meth:`~musicdb.mdbapi.extern.MusicDBExtern.UpdateSongmap` - Update the list with the current state of the music collection
        #. :meth:`~musicdb.mdbapi.extern.MusicDBExtern.RemoveOldSongs` - Remove old songs from the external storage that are no longer in the collection
        #. :meth:`~musicdb.mdbapi.extern.MusicDBExtern.CopyNewSongs` - Copy new songs from the collection to the storage. Here, transcoding will be applied if configured. See `Handling Toxic Environments`_
        #. :meth:`~musicdb.mdbapi.extern.MusicDBExtern.WriteSongmap` - Writes the new state of the external storage device

        Returns:
            ``None``
        """
        if not self.mp:
            logging.error("Mountpoint is not initialized!")
            return None

        extstatedir = os.path.join(self.mp,     self.cfg.extern.statedir)

        # Get songmap-file
        mapfile     = os.path.join(extstatedir, self.cfg.extern.songmap)
        
        # Open external storage configuration
        extcfgfile  = os.path.join(extstatedir, self.cfg.extern.configfile)
        extconfig   = ExternConfig(extcfgfile)
        if extconfig.meta.version != 3:
            logging.warning("Unexpected config-version of external storage configuration: %d != 3."
                    "\033[0;33mDoing nothing to prevent Damage!", extconfig.meta.version)
            return None

        # Get all song Paths
        print(" \033[1;35m * \033[1;34mReading database …\033[0;36m")
        songs       = self.db.GetAllSongs()
        mdbpathlist = [ song["path"] for song in songs ]

        # Start update
        print(" \033[1;35m * \033[1;34mReading songmap …\033[0;36m")
        songmap = self.ReadSongmap   (mapfile)
        print(" \033[1;35m * \033[1;34mUpdating songmap …\033[0;36m")
        songmap = self.UpdateSongmap (songmap, mdbpathlist)
        print(" \033[1;35m * \033[1;34mRemoving outdated files …\033[0;36m")
        songmap = self.RemoveOldSongs(songmap, extconfig)
        print(" \033[1;35m * \033[1;34mCopying new files …\033[0;36m")
        songmap = self.CopyNewSongs  (songmap, extconfig)
        print(" \033[1;35m * \033[1;34mWriting songmap …\033[0;36m")
        self.WriteSongmap(songmap, mapfile)

        return None



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

