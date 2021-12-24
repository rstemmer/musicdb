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
This module is the core of the music handling of MusicDB.
It is the interface between the music and its entries in the database (:mod:`musicdb.lib.db.musicdb`).
"""

import os
import stat
import signal
from pathlib import Path
from musicdb.lib.fileprocessing import Fileprocessing
from musicdb.lib.metatags       import MetaTags
from musicdb.lib.cfg.musicdb    import MusicDBConfig
from musicdb.lib.db.musicdb     import *
from musicdb.lib.db.trackerdb   import TrackerDatabase      # To update when a song gets removed
from musicdb.mdbapi.musicdirectory  import MusicDirectory


class MusicDBMusic(object):
    """
    This class provides tools to manage the music database and its files.
    The main purpose is to act as interface between the database and the files associated to the entries inside the database.

    In comparison to the :class:`~musicdb.mdbapi.musicdirectory.MusicDirectory` a link between a file and the database is assumed.

    This class supports the following features

        * File management
            * :meth:`~FindLostPaths`: Check if all paths in the *songs*, *albums* and *artists* table are valid.
            * :meth:`~FindNewPaths`: Check if there are new songs, albums or artists in the music collection that are not in the database.
            * :meth:`~FindNewSongs`:
        * Database management
            * :meth:`~AddArtist`, :meth:`~AddAlbum`, :meth:`~AddSong`, :meth:`~AddVideo`: Adds a new artist, album, song video to the database
            * :meth:`~UpdateArtist`, :meth:`~UpdateAlbum`, :meth:`~UpdateSong`: Updates a artist, album or song path in the database
            * :meth:`~RemoveArtist`, :meth:`~RemoveAlbum`, :meth:`~RemoveSong`: Removes a artist, album or song from the database
        * Add information into the database
            * :meth:`~AddLyricsFromFile`: Read lyrics from the meta data of a song file into the database
            * :meth:`~UpdateChecksum`: Calculates and adds the checksum of a song file into the database
        * Other

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
        self.fileprocessing = Fileprocessing(self.cfg.directories.music)
        self.musicdirectory = MusicDirectory(config)
        self.meta   = MetaTags(self.cfg.directories.music)

        # -rw-rw-r--
        self.filepermissions= stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH
        # drwxrwxr-x
        self.dirpermissions = stat.S_IRWXU | stat.S_IRWXG | stat.S_IROTH | stat.S_IXOTH                 

        # read lists with files and directories that shall be ignored by the scanner
        self.ignoreartists = self.cfg.music.ignoreartists
        self.ignorealbums  = self.cfg.music.ignorealbums
        self.ignoresongs   = self.cfg.music.ignoresongs

        self.artistpathscache = []
        self.albumpathscache  = []
        self.songpathscache   = []
        self.videopathscache  = []
        self._UpdatePathsCaches()



    def _UpdatePathsCaches(self):
        """
        """
        artists = self.db.GetAllArtists()
        albums  = self.db.GetAllAlbums()
        songs   = self.db.GetAllSongs()
        videos  = self.db.GetVideos()
        self.artistpathscache = [artist["path"] for artist in artists]
        self.albumpathscache  = [album["path"]  for album  in albums]
        self.songpathscache   = [song["path"]   for song   in songs]
        self.videopathscache  = [video["path"]  for video  in videos]
        return



    def FindLostPaths(self):
        """
        This method checks all artist, album song and video entries if the paths to their related directories and files are still valid.
        Entries with invalid paths gets returned in as a list inside a dictionary.

        Returns:
            A dictionary with 4 entries: ``"artists"``, ``"albums"``, ``"songs"`` and ``"videos"``.
        """
        lostartists = []
        lostalbums  = []
        lostsongs   = []
        lostvideos  = []

        # Check Artists
        artists = self.db.GetAllArtists()
        for artist in artists:
            if not self.musicdirectory.IsDirectory(artist["path"]):
                lostartists.append(artist)

        # Check Albums
        albums = self.db.GetAllAlbums()
        for album in albums:
            if not self.musicdirectory.IsDirectory(album["path"]):
                lostalbums.append(album)

        # Check Songs
        songs = self.db.GetAllSongs()
        for song in songs:
            if not self.musicdirectory.IsFile(song["path"]):
                lostsongs.append(song)

        # Check Videos
        videos = self.db.GetVideos()
        for video in videos:
            if not self.musicdirectory.IsFile(video["path"]):
                lostvideos.append(video)

        lostpaths = {}
        lostpaths["artists"] = lostartists
        lostpaths["albums"]  = lostalbums
        lostpaths["songs"]   = lostsongs
        lostpaths["videos"]  = lostvideos
        return lostpaths



    def FindNewPaths(self):
        """
        This method searches inside the music directory for valid artist, album song and video paths.
        If those paths are not in the database, they will be returned.
        So this method returns four lists: artist-, album-, song-, and video- paths.
        Each representing an artist, album, song or video that is not known by the database yet.
        Files and directories in the configured ignore-list will be ignored.

        If a new directory was found, the subdirectories will also be added!
        So for a new album, the new songs are explicit added as well.

        This method is very optimistic. It will also list empty directories.
        The user may want to check if the results of this method are valid for him.

        Furthermore this method is error tolerant. This means, if in the database has an invalid entry,
        it does not lead to errors. For example, if an album path gets renamed, this path will be returned.
        It does not lead to an error that the old path is still in the database.

        Returns:
            A dictionary with 4 entries: ``"artists"``, ``"albums"``, ``"songs"`` and ``"videos"``.
            Each a list of paths that are valid but unknown by the database. Empty lists if there is no valid entry.
        """
        newpaths = {}
        newpaths["artists"] = []
        newpaths["albums"]  = []
        newpaths["songs"]   = []
        newpaths["videos"]  = []

        self._UpdatePathsCaches()

        artistpaths = self.musicdirectory.GetSubdirectories(None, self.ignoreartists)
        artistpaths = self.musicdirectory.ToString(artistpaths)

        # Check Artists
        knownartistpaths = self.artistpathscache

        for path in artistpaths:
            if path not in knownartistpaths:
                newpaths["artists"].append(path)

        # Check Albums
        knownalbumpaths = self.albumpathscache
        albumpaths      = self.musicdirectory.GetSubdirectories(artistpaths, self.ignorealbums)
        albumpaths      = self.musicdirectory.ToString(albumpaths)
        
        for path in albumpaths:
            if path not in knownalbumpaths:
                newpaths["albums"].append(path)

        # Check Songs
        for albumpath in albumpaths:
            newsongpaths = self.FindNewSongs(albumpath)
            newpaths["songs"].extend(newsongpaths)

        # Check Videos
        knownvideopaths = self.videopathscache
        videopaths      = self.musicdirectory.GetFiles(artistpaths)
        videopaths      = self.musicdirectory.ToString(videopaths)

        for path in videopaths:

            # check if this is really an audio file
            extension = self.musicdirectory.GetFileExtension(path)
            if extension not in ["mp4", "m4v", "webm"]:
                continue

            if path not in knownvideopaths:
                newpaths["videos"].append(path)

        return newpaths



    def FindNewSongs(self, albumpath: str) -> list:
        """
        This method searches inside a given album path for new songs.
        The album part can address an album that is known by the MusicDB, but it can also be an unknown one.

        The songs are filtered by the configured ignore list (see :doc:`/basics/config`).

        Furthermore the songs are filtered by their extension.
        Only the following files are considered: .aac, .m4a, .mp3, .flac

        If the song path in already known (can be found in the database), then the song is ignored as well.

        Args:
            albumpath (str): path to an album that may have new/unknown songs. The path must be relative to the music directory.

        Returns:
            A list of new, unknown song paths. If no new songs have be found, an empty list gets returned.
        """
        newpaths        = []
        knownsongpaths  = self.songpathscache
        songpaths       = self.musicdirectory.GetFiles(albumpath, self.ignoresongs)
        songpaths       = self.musicdirectory.ToString(songpaths)

        for path in songpaths:

            # check if this is really an audio file
            extension = self.musicdirectory.GetFileExtension(path)
            if extension == None or extension == []:
                continue

            extension = extension.lower()
            if extension not in ["aac", "m4a", "mp3", "flac"]:
                continue

            if path not in knownsongpaths:
                newpaths.append(path)
        return newpaths



    def AddArtist(self, artistpath):
        """
        The *AddArtist* method adds a new artist to the database.
        This is done in the following steps:

            #. Check if the artist path is inside the music root directory
            #. Check if the artist is already in the database
            #. Extract the artist name from the path
            #. Set file attributes and ownership using :meth:`~musicdb.mdbapi.musicdirectory.MusicDirectory.FixAttributes`
            #. Add artist to database
            #. Call :meth:`~musicdb.mdbapi.music.MusicDBMusic.AddAlbum` for all subdirectories of the artistpath. (Except for the directory-names in the *ignorealbum* list)

        Args:
            artistpath (str): Absolute or relative (to the music directory) path to the artist that shall be added to the database.

        Returns:
            ``None``

        Raises:
            ValueError: If the path does not address a directory
            ValueError: If artist is already in the database
        """
        # remove the leading part to the music directory
        artistpath = self.musicdirectory.TryRemoveRoot(artistpath)
        artistpath = self.musicdirectory.ToString(artistpath)

        if not self.musicdirectory.IsDirectory(artistpath):
            raise ValueError("Artist path " + artistpath + " is not a directory!")

        # Check if the artist already exists in the database
        artist = self.db.GetArtistByPath(artistpath)
        if artist != None:
            raise ValueError("Artist \"" + artist["name"] + "\" does already exist in the database.")
        
        # The filesystem is always right - Survivor of the "tag over fs"-apocalypse - THE FS IS _ALWAYS_ RIGHT!
        artistname = os.path.basename(artistpath)

        # fix attributes to fit in mdb environment before adding it to the database
        try:
            self.musicdirectory.FixAttributes(videopath)
        except Exception as e:
            logging.warning("Fixing file attributes failed with error: %s \033[1;30m(leaving permissions as they are)",
                    str(e))

        # add artist to database
        self.db.AddArtist(artistname, artistpath)
        artist = self.db.GetArtistByPath(artistpath)

        # Add all albums to the artist
        albumpaths = self.musicdirectory.GetSubdirectories(artistpath, self.ignorealbums)
        for albumpath in albumpaths:
            self.AddAlbum(albumpath, artist["id"])

        return None



    def UpdateArtist(self, artistid, newpath):
        """
        This method updates an already existing artist entry in the database.

        Updates information are:

            * path
            * name

        All albums and songs of this artist will also be updated using
        :meth:`~UpdateAlbum` and :meth:`~UpdateSong`.

        Args:
            artistid (int): ID of the artist entry that shall be updated
            newpath (str): Relative path to the new artist

        Returns:
            ``None``
        """
        artistpath = self.musicdirectory.TryRemoveRoot(newpath)
        artistpath = self.musicdirectory.ToString(artistpath)

        artist     = self.db.GetArtistById(artistid)
        artist["path"] = artistpath
        artist["name"] = os.path.basename(artistpath)
        self.db.WriteArtist(artist)

        albums = self.db.GetAlbumsByArtistId(artistid)
        for album in albums:
            albumpath    = album["path"]
            albumpath    = albumpath.split(os.sep)
            albumpath[0] = artistpath
            albumpath    = os.sep.join(albumpath)
            if self.musicdirectory.IsDirectory(albumpath):
                self.UpdateAlbum(album["id"], albumpath)

        return None



    def AddAlbum(self, albumpath, artistid=None):
        """
        This method adds an album to the database in the following steps:

            #. Check if the album already exists in the database
            #. Get all songs of the album by getting all files inside the directory except those on the *ignoresongs*-list.
            #. Load the metadata from one of those songs using :meth:`musicdb.lib.metatags.MetaTags.GetAllMetadata`
            #. Analyze the path of one of the song using :meth:`~musicdb.mdbapi.musicdirectory.MusicDirectory.AnalysePath`
            #. If *artistid* is not given as parameter, it gets read from the database identifying the artist by its path.
            #. Get modification date using :meth:`~musicdb.lib.filesystem.FileSystem.GetModificationDate`
            #. Set file attributes and ownership using :meth:`~musicdb.mdbapi.musicdirectory.MusicDirectory.FixAttributes`
            #. Create new entry for the new album in the database and get the default values
            #. Add each song of the album to the database by calling :meth:`~musicdb.mdbapi.music.MusicDBMusic.AddSong`
            #. Write all collected information of the album into the database

        If adding the songs to the database raises an exception, that song gets skipped.
        The *numofsongs* value for the album is the number of actual existing songs for this album in the database.
        It is save to add the failed song later by using the :meth:`~musicdb.mdbapi.music.MusicDBMusic.AddSong` method.

        Args:
            albumpath (str): Absolute path, or path relative to the music root directory, to the album that shall be added to the database.
            artistid (int): Optional, default value is ``None``. The ID of the artist this album belongs to.

        Returns:
            ``None``

        Raises:
            ValueError: If the path does not address a directory
            ValueError: If album already exists in the database
            AssertionError: If there is no artist for this album in the database
            AssertionError: If loading metadata from one of the song files failed

        """
        # remove the leading part to the music directory (it may be already removed)
        albumpath = self.musicdirectory.TryRemoveRoot(albumpath)
        albumpath = self.musicdirectory.ToString(albumpath)

        if not self.musicdirectory.IsDirectory(albumpath):
            raise ValueError("Artist path " + artistpath + " is not a directory!")

        # Check if the album already exists in the database
        album = self.db.GetAlbumByPath(albumpath)
        if album != None:
            raise ValueError("Album \"" + album["name"] + "\" does already exist in the database.")

        # This album dictionary gets filled with all kind of information during this method.
        # At the end they are written into the database
        album = {}
        album["name"]       = None
        album["path"]       = albumpath

        # get all songs from the albums - this is important to collect all infos for the album entry
        paths = self.musicdirectory.GetFiles(albumpath, self.ignoresongs) # ignores also all directories

        # remove files that are not music
        songpaths = []
        for path in paths:
            if self.musicdirectory.GetFileExtension(path) in ["mp3", "m4a", "aac", "flac"]:
                songpaths.append(path)

        # analyse the first one for the album-entry
        self.meta.Load(songpaths[0])
        tagmeta = self.meta.GetAllMetadata()
        fsmeta  = self.musicdirectory.AnalysePath(songpaths[0])
        if fsmeta == None:
            raise AssertionError("Analysing path \"%s\" failed!", songpaths[0])
        moddate = self.musicdirectory.GetModificationDate(albumpath)

        # usually, the filesystem is always right, but in case of iTunes, the meta data are
        # FIX: NO! THEY ARE NOT! - THE FILESYSTEM IS _ALWAYS_ RIGHT!
        album["name"]    = fsmeta["album"]
        album["release"] = fsmeta["release"]
        album["origin"]  = tagmeta["origin"]
        album["added"]   = moddate
        album["hidden"]  = False
        
        if artistid == None:
            # the artistname IS the path, because thats how the fsmeta data came from
            artist = self.db.GetArtistByPath(fsmeta["artist"])
            if artist == None:
                raise AssertionError("Artist for the album \"" + album["name"] + "\" is not avaliable in the database.")
            artistid = artist["id"]

        # fix attributes to fit in mdb environment before adding it to the database
        try:
            self.musicdirectory.FixAttributes(videopath)
        except Exception as e:
            logging.warning("Fixing file attributes failed with error: %s \033[1;30m(leaving permissions as they are)",
                    str(e))

        # Add Album to database
        self.db.AddAlbum(artistid, album["name"], album["path"])

        # read the new database entry to get defaults - this is needed by the WriteAlbum-method
        entry = self.db.GetAlbumByPath(album["path"])
        album["id"]         = entry["id"]
        album["artworkpath"]= entry["artworkpath"]
        album["bgcolor"]    = entry["bgcolor"]
        album["fgcolor"]    = entry["fgcolor"]
        album["hlcolor"]    = entry["hlcolor"]

        # update the album entry
        album["artistid"]   = artistid

        # now add all the albums songs to the database
        for songpath in songpaths:
            try:
                self.AddSong(songpath, artistid, album["id"])
            except Exception as e:
                logging.exception("CRITICAL ERROR! Adding a song to the new added album \"%s\" failed with the exception \"%s\"! \033[1;30m(ignoring that song (%s) and continue with next)", str(album["name"]), str(e), str(songpath))

        # get some final information after adding the songs
        songs = self.db.GetSongsByAlbumId(album["id"])
        numofcds = 0
        for song in songs:
            if song["cd"] > numofcds:
                numofcds = song["cd"]

        album["numofsongs"] = len(songs)
        album["numofcds"]   = numofcds

        try:
            self.db.WriteAlbum(album)
        except Exception as e:
            logging.exception("CRITICAL ERROR! Updating album information failed with error \"%s\". Use the musicdb database command to remove this album and see the log file for further details.", str(e))
        return None



    def UpdateAlbum(self, albumid, newpath):
        """
        This method updates an already existing album entry in the database.
        So in case some information in the filesystem were changed (renaming, new files, …) the database gets updated.
        The following steps will be done to do this:

            #. Update the *path* entry of the album to the new path
            #. Reading a song file inside the directory to load meta data
            #. Analyse the path to collect further information from the filesystem
            #. Update database entry for the album with the new collected information

        Updates information are:

            * path
            * name
            * release date
            * origin

        All albums and songs of this artist will also be updated using
        :meth:`~UpdateSong`.

        Args:
            albumid (int): ID of the album entry that shall be updated
            newpath (str): Relative path to the new album

        Returns:
            ``None``

        Raises:
            AssertionError: When the new path is invalid
        """
        albumpath = self.musicdirectory.TryRemoveRoot(newpath)
        albumpath = self.musicdirectory.ToString(albumpath)

        album = self.db.GetAlbumById(albumid)

        album["path"] = albumpath

        # get all songs from the albums - this is important to collect all infos for the album entry
        songpaths = self.musicdirectory.GetFiles(albumpath, self.ignoresongs) # ignores also all directories

        # analyse the first one for the album-entry
        self.meta.Load(songpaths[0])
        tagmeta = self.meta.GetAllMetadata()
        fsmeta  = self.musicdirectory.AnalysePath(songpaths[0])
        if fsmeta == None:
            raise AssertionError("Analysing path \"%s\" failed!", songpaths[0])

        album["name"]    = fsmeta["album"]
        album["release"] = fsmeta["release"]
        album["origin"]  = tagmeta["origin"]
        self.db.WriteAlbum(album)

        songs = self.db.GetSongsByAlbumId(albumid)
        for song in songs:
            songpath    = song["path"]
            songpath    = songpath.split(os.sep)    # [artist, album, song]
            songpath.pop(0)                         # [album, song]         // remove old artist
            songpath[0] = albumpath                 # [artist/album, song]  // add new artist/album string
            songpath    = os.sep.join(songpath)

            # If it does not work, it does not matter.
            # This can be fixed by the user later.
            # It may fail because not only the album name changed,
            # but also the files inside
            if self.musicdirectory.IsFile(songpath):
                self.UpdateSong(song["id"], songpath)

        return None



    def AddSong(self, songpath, artistid=None, albumid=None):
        """
        This method adds a song to the MusicDB database.
        To do so, the following steps were done:

            #. Check if the song already exists in the database
            #. Load the metadata from the song using :meth:`musicdb.lib.metatags.MetaTags.GetAllMetadata`
            #. Analyze the path of one of the song using :meth:`~musicdb.mdbapi.musicdirectory.MusicDirectory.AnalysePath`
            #. If *artistid* is not given as parameter, it gets read from the database identifying the artist by its path.
            #. If *albumid* is not given as parameter, it gets read from the database identifying the album by its path.
            #. Set file attributes and ownership using :meth:`~musicdb.mdbapi.musicdirectory.MusicDirectory.FixAttributes`
            #. Add song to database
            #. If the parameter *albumid* was ``None`` the *numofsongs* entry of the determined album gets incremented
            #. If there are lyrics in the song file, they get also inserted into the database

        In case the album ID is set, this method assumes that its database entry gets managed by the :meth:`~musicdb.mdbapi.music.MusicDBMusic.AddAlbum` method.
        So, nothing will be changed regarding the album.
        If album ID was ``None``, this method also updates the album-entry, namely the *numofsongs* value gets incremented.

        Args:
            songpath (str): Absolute path, or path relative to the music root directory, to the song that shall be added to the database.
            artistid (int): Optional, default value is ``None``. The ID of the artist this song belongs to.
            albumid (int): Optional, default value is ``None``. The ID of the album this song belongs to.

        Returns:
            ``None``

        Raises:
            ValueError: If song already exists in the database
            AssertionError: If analyzing the path fails
            AssertionError: If there is no album for this song in the database
        """
        # do some checks
        # remove the root-path to the music directory
        songpath = self.musicdirectory.TryRemoveRoot(songpath)
        songpath = self.musicdirectory.ToString(songpath)

        # Check if the song already exists in the database
        song = self.db.GetSongByPath(songpath)
        if song != None:
            raise ValueError("Song \"" + song["name"] + "\" does already exist in the database.")

        # Get all information from the songpath and its meta data
        try:
            self.meta.Load(songpath)
        except Exception:
            logging.debug("Metadata of file %s cannot be load. Assuming this is not a song file!", str(songpath))
            # Ignore this file, it is not a valid song file
            return None

        tagmeta = self.meta.GetAllMetadata()
        fsmeta  = self.musicdirectory.AnalysePath(songpath)
        if fsmeta == None:
            raise AssertionError("Invalid path-format: " + songpath)

        # Collect all data needed for the song-entry (except the song ID)
        # Remember! The filesystem is always right
        song = {}
        song["artistid"]    = artistid # \_ In case they are None yet, they will be updated later in the code
        song["albumid"]     = albumid  # /
        song["path"]        = songpath
        song["number"]      = fsmeta["songnumber"]
        song["cd"]          = fsmeta["cdnumber"]
        song["disabled"]    = 0
        song["playtime"]    = tagmeta["playtime"]
        song["bitrate"]     = tagmeta["bitrate"]
        song["likes"]       = 0
        song["dislikes"]    = 0
        song["favorite"]    = 0
        song["lyricsstate"] = SONG_LYRICSSTATE_EMPTY
        song["checksum"]    = self.fileprocessing.Checksum(songpath)
        song["lastplayed"]  = 0
        song["liverecording"]=0
        song["badaudio"]    = 0

        # FIX: THE FILESYSTEM IS _ALWAYS_ RIGHT! - WHAT THE FUCK!
        song["name"] = fsmeta["song"] 

        # artistid may be not given by the arguments of this method.
        # In this case, it must be searched in the database
        if artistid == None:
            artist = self.db.GetArtistByPath(fsmeta["artist"])
            if artist == None:
                raise AssertionError("Artist for the song \"" + songpath + "\" is not avaliable in the database.")

            song["artistid"] = artist["id"]

        if albumid == None:
            # reconstruct the album path out of the songs meta-information from the filesystem
            # so it is easy to find the right album by just comparing the pathes
            albumpath = fsmeta["artist"] + "/" + str(fsmeta["release"]) + " - " + fsmeta["album"]

            # find the album from the given artist to that the song belongs
            albums = self.db.GetAlbumsByArtistId(song["artistid"])
            for album in albums:
                if album["path"] == albumpath:
                    song["albumid"] = album["id"]
                    break
            else:
                raise AssertionError("The album for the song \"" + songpath + "\" is not avaliable in the database.")
            # if the albumid was unknown, the numofsongs was not updated before.
            # So the next section is necessary to determin the new numofsongs
            # (Will not be written to DB yet, only if AddFullSong at the end succeeds)
            newalbumentry   = self.db.GetAlbumById(song["albumid"])
            songlist        = self.db.GetSongsByAlbumId(song["albumid"])
            newalbumentry["numofsongs"] = len(songlist) + 1
        else:
            newalbumentry   = None  # there is no update for the album-entry

        # fix attributes to fit in mdb environment before adding it to the database
        try:
            self.musicdirectory.FixAttributes(songpath)
        except Exception as e:
            logging.warning("Fixing file attributes failed with error: %s \033[1;30m(leaving permissions as they are)",
                    str(e))

        # add to database
        retval = self.db.AddFullSong(song)
        if retval == False:
            raise AssertionError("Adding song %s failed!", song["path"])

        if newalbumentry:
            self.db.WriteAlbum(newalbumentry)

        # Add lyrics for this song
        if tagmeta["lyrics"] != None:
            try:
                self.db.SetLyrics(song["id"], tagmeta["lyrics"], SONG_LYRICSSTATE_FROMFILE)
            except Exception as e:
                logging.warning("Adding lyrics for song %s failed with error \"%s\". \033[1;30m(Does not break anything)",
                        song["name"], str(e))

        return None



    def UpdateSong(self, songid, newpath):
        """
        This method updates a song entry and parts of the related album entry.
        The following steps will be done to do this:

            #. Update the *path* entry of the album to the new path
            #. Reading the song files meta data
            #. Analyse the path to collect further information from the filesystem
            #. Update database entry with the new collected information

        Updates information are:

            * path
            * name
            * song number
            * cd number
            * playtime
            * bitrate
            * checksum

        Further more the following album information get updted:

            * numofsongs
            * numofcds

        Args:
            songid (int): ID of the song entry that shall be updated
            newpath (str): Relative path to the new album

        Returns:
            ``None``

        Raises:
            AssertionError: When the new path is invalid
            Exception: When loading the meta data failes
        """
        songpath = self.musicdirectory.TryRemoveRoot(newpath)
        songpath = self.musicdirectory.ToString(songpath)
        song     = self.db.GetSongById(songid)

        # Get all information from the songpath and its meta data
        try:
            self.meta.Load(songpath)
        except Exception as e:
            logging.excpetion("Metadata of file %s cannot be load. Error: %s", str(songpath), str(e))
            raise e

        tagmeta = self.meta.GetAllMetadata()
        fsmeta  = self.musicdirectory.AnalysePath(songpath)
        if fsmeta == None:
            raise AssertionError("Invalid path-format: " + songpath)

        # Remember! The filesystem is always right
        song["path"]     = songpath
        song["name"]     = fsmeta["song"] 
        song["number"]   = fsmeta["songnumber"]
        song["cd"]       = fsmeta["cdnumber"]
        song["playtime"] = tagmeta["playtime"]
        song["bitrate"]  = tagmeta["bitrate"]
        song["checksum"] = self.fileprocessing.Checksum(songpath)

        self.db.WriteSong(song)

        # Fix album information
        album = self.db.GetAlbumById(song["albumid"])
        songs = self.db.GetSongsByAlbumId(album["id"])
        numofcds = 0
        for song in songs:
            if song["cd"] > numofcds:
                numofcds = song["cd"]

        album["numofsongs"] = len(songs)
        album["numofcds"]   = numofcds
        self.db.WriteAlbum(album)
        return None



    def AddVideo(self, videopath, artistid=None):
        """
        This method adds a video to the MusicDB database.
        To do so, the following steps were done:

            #. Check if the video already exists in the database
            #. Load the metadata from the video using :meth:`musicdb.lib.metatags.MetaTags.GetAllMetadata`
            #. Analyze the path of one of the video using :meth:`~musicdb.mdbapi.musicdirectory.MusicDirectory.AnalysePath`
            #. If *artistid* is not given as parameter, it gets read from the database identifying the artist by its path.
            #. Set file attributes and ownership using :meth:`~musicdb.mdbapi.musicdirectory.MusicDirectory.FixAttributes`
            #. Add video to database

        This method assumes that the artist the video belongs to exists in the database.
        If not, an ``AssertionError`` exception gets raised.

        Args:
            videopath (str): Absolute path, or path relative to the music root directory, to the video that shall be added to the database.
            artistid (int): Optional, default value is ``None``. The ID of the artist this video belongs to.

        Returns:
            ``True`` on success, otherwise ``False`` (or it raises an exception)

        Raises:
            ValueError: If video already exists in the database
            AssertionError: If analyzing the path fails
            AssertionError: If artist does not exists in the database
            AssertionError: If adding the video to the database fails
        """
        # do some checks
        # remove the root-path to the music directory
        videopath = self.musicdirectory.TryRemoveRoot(videopath)
        videopath = self.musicdirectory.ToString(videopath)

        # Check if the video already exists in the database
        video = self.db.GetVideoByPath(videopath)
        if video != None:
            raise ValueError("Video \"" + video["name"] + "\" does already exist in the database.")

        # Get all information from the video path and its meta data
        try:
            self.meta.Load(videopath)
        except Exception as e:
            logging.error("Meta data of file %s cannot be loaded (Error: %s). Assuming this is not a video file!", str(videopath), str(e))
            # Ignore this file, it is not a valid song file
            return False

        tagmeta = self.meta.GetAllMetadata()
        fsmeta  = self.musicdirectory.AnalysePath(videopath)
        if fsmeta == None:
            raise AssertionError("Invalid path-format: " + videopath)

        moddate = self.musicdirectory.GetModificationDate(videopath)

        # artistid may be not given by the arguments of this method.
        # In this case, it must be searched in the database
        if artistid == None:
            artist = self.db.GetArtistByPath(fsmeta["artist"])
            if artist == None:
                raise AssertionError("Artist for the video \"" + videopath + "\" is not available in the database.")
            artistid = artist["id"]

        # Collect all data needed for the song-entry (except the song ID)
        # Remember! The file system is always right!
        video = {}
        video["id"]          = None     # Not yet known. Will be inserted by AddFullVideo
        video["songid"]      = None
        video["albumid"]     = None
        video["artistid"]    = artistid
        video["name"]        = fsmeta["video"]
        video["path"]        = videopath
        video["disabled"]    = 0
        video["playtime"]    = tagmeta["playtime"]
        video["origin"]      = tagmeta["origin"]
        video["release"]     = fsmeta["release"]
        video["added"]       = moddate
        video["codec"]       = tagmeta["codec"]
        video["xresolution"] = tagmeta["xresolution"]
        video["yresolution"] = tagmeta["yresolution"]
        video["framesdirectory"] = ""
        video["thumbnailfile"]   = ""
        video["previewfile"] = ""
        video["likes"]       = 0
        video["dislikes"]    = 0
        video["favorite"]    = 0
        video["liverecording"]=0
        video["badaudio"]    = 0
        video["checksum"]    = self.fileprocessing.Checksum(videopath)
        video["lastplayed"]  = 0
        video["lyricsvideo"] = 0
        video["bgcolor"]     = "#101010"
        video["fgcolor"]     = "#F0F0F0"
        video["hlcolor"]     = "#909090"
        video["vbegin"]      = 0
        video["vend"]        = video["playtime"]

        # Fix attributes to fit in MusicDB environment before adding it to the database
        try:
            self.musicdirectory.FixAttributes(videopath)
        except Exception as e:
            logging.warning("Fixing file attributes failed with error: %s \033[1;30m(leaving permissions as they are)",
                    str(e))

        # add to database
        retval = self.db.AddFullVideo(video)
        if retval == False:
            raise AssertionError("Adding video %s failed!", video["path"])

        return True



    def UpdateVideo(self, videoid, newpath):
        """
        This method updates a video entry in the database.
        The following steps will be done to do this:

            #. Update the *path* entry of the video to the new path (in case the file name is different)
            #. Reading the video files meta data
            #. Analyse the path to collect further information from the file system
            #. Update database entry with the new collected information

        Updates information are:

            * path
            * name
            * playtime
            * origin
            * release
            * date the file was added
            * codec
            * x/y resolution
            * video begin/end
            * checksum

        Args:
            videoid (int): ID of the video entry that shall be updated
            newpath (str): Relative path to the new album

        Returns:
            ``None``

        Raises:
            AssertionError: When the new path is invalid
            Exception: When loading the meta data failes
        """
        videopath = self.musicdirectory.TryRemoveRoot(newpath)
        videopath = self.musicdirectory.ToString(videopath)
        video     = self.db.GetVideoById(videoid)

        # Get all information from the video path and its meta data
        try:
            self.meta.Load(videopath)
        except Exception as e:
            logging.excpetion("Meta data of file %s cannot be load. Error: %s", str(videopath), str(e))
            raise e

        tagmeta = self.meta.GetAllMetadata()
        moddate = self.musicdirectory.GetModificationDate(videopath)
        fsmeta  = self.musicdirectory.AnalysePath(videopath)
        if fsmeta == None:
            raise AssertionError("Invalid path-format: " + videopath)

        # Remember! The file system is always right
        video["name"]        = fsmeta["video"]
        video["path"]        = videopath
        video["playtime"]    = tagmeta["playtime"]
        video["origin"]      = tagmeta["origin"]
        video["release"]     = fsmeta["release"]
        video["added"]       = moddate
        video["codec"]       = tagmeta["codec"]
        video["xresolution"] = tagmeta["xresolution"]
        video["yresolution"] = tagmeta["yresolution"]
        video["checksum"]    = self.fileprocessing.Checksum(videopath)
        video["vbegin"]      = 0
        video["vend"]        = video["playtime"]

        self.db.WriteVideo(video)
        return None



    def RemoveSong(self, songid):
        """
        This method removed a song from the database.
        The file gets not touched, and so it does not matter if it even exists.
        All related information will also be removed.

        .. warning::

            This is not a *"set the deleted flag"* method.
            The data gets actually removed from the database.
            No recovery possible!

        Args:
            songid (int): ID of the song that shall be removed from database

        Return:
            ``None``
        """
        tracker = TrackerDatabase(self.cfg.files.trackerdatabase)

        # remove from music.db
        self.db.RemoveSong(songid)
        # remove from tracker.db
        tracker.RemoveSong(songid)

        return None


    def RemoveAlbum(self, albumid):
        """
        This method removes an album from the database.
        The files gets not touched, and so it does not matter if they even exists.
        All related information will also be removed.

        .. warning::

            For all songs in this album, the :meth:`~RemoveSong` method gets called!

        .. warning::

            This is not a *"set the deleted flag"* method.
            The data gets actually removed from the database.
            No recovery possible!

        Args:
            albumid (int): ID of the album that shall be removed from database

        Return:
            ``None``
        """
        songs = self.db.GetSongsByAlbumId(albumid)
        for song in songs:
            self.RemoveSong(song["id"])
        self.db.RemoveAlbum(albumid)
        return None


    def RemoveArtist(self, artistid):
        """
        This method removes an artist from the database.
        The files gets not touched, and so it does not matter if they even exists.
        All related information will also be removed.

        .. warning::

            For all artists albums, the :meth:`~RemoveAlbum` method gets called!

        .. warning::

            This is not a *"set the deleted flag"* method.
            The data gets actually removed from the database.
            No recovery possible!

        Args:
            artistid (int): ID of the artist that shall be removed from database

        Return:
            ``None``
        """
        albums = self.db.GetAlbumsByArtistId(artistid)
        for album in albums:
            self.RemoveAlbum(album["id"])
        self.db.RemoveArtist(artistid)
        return None



    def UpdateChecksum(self, songpath):
        """
        This method can be used to add or update the checksum of the file of a song into the database.
        The method does not care if there is already a checksum.
        
        .. note::

            :meth:`~AddSong` and :meth:`~UpdateSong` also update the checksum.
            So after calling that methods, calling this ``AddChecksum`` method is not necessary.

        Args:
            songpath (str): Absolute song path, or relative to the music root directory.

        Returns:
            ``True`` on success, otherwise ``False``
        """
        # remove the root-path to the music directory
        songpath = self.musicdirectory.TryRemoveRoot(songpath)
        songpath = self.musicdirectory.ToString(songpath)

        # Check if the song exists in the database
        song = self.db.GetSongByPath(songpath)
        if song == None:
            logging.warning("There is no song with file \"%s\" in the database! \033[1;30m(No checksum will be added)", songpath)
            return False

        # Add new checksum
        song["checksum"] = self.fileprocessing.Checksum(songpath)
        self.db.WriteSong(song)
        return True



    def AddLyricsFromFile(self, songpath):
        """
        This method can be used to add lyrics from the file of a song into the database.
        It tries to load the metadata from the song file.
        If that succeeds, the song entry gets loaded from the database and the lyrics state of that entry gets checked.
        The lyrics from the file gets stored in the song database in case the current lyrics state is *empty*.
        Otherwise the files lyrics get rejected.

        This method returns ``True`` when *new* lyrics were added. If there already exist lyrics ``False`` gets returned.

        Args:
            songpath (str): Absolute song path, or relative to the music root directory.

        Returns:
            ``True`` on success, otherwise ``False``
        """
        # remove the root-path to the music directory
        songpath = self.musicdirectory.TryRemoveRoot(songpath)
        songpath = self.musicdirectory.ToString(songpath)

        # Get all information from the song path and its meta data
        try:
            self.meta.Load(songpath)
        except Exception as e:
            logging.warning("Loading songs metadata failed with error: %s. \033[1;30m(No lyrics will be loaded)", str(e))
            return False

        # read all meta-tags
        tagmeta = self.meta.GetAllMetadata()

        if tagmeta["lyrics"] == None:
            # No lyrics - no warning because this is common
            return False

        # Check if the song exists in the database
        song = self.db.GetSongByPath(songpath)
        if song == None:
            logging.warning("There is no song with file \"%s\" in the database! \033[1;30m(No lyrics will be added)", songpath)
            return False

        # check if there are already lyrics, if yes, cancel
        if song["lyricsstate"] != SONG_LYRICSSTATE_EMPTY:
            logging.warning("Song \"%s\" has already lyrics. They will NOT be overwritten!", song["name"])
            return False
        
        # store lyrics and update lyricsstate
        self.db.SetLyrics(song["id"], tagmeta["lyrics"], SONG_LYRICSSTATE_FROMFILE)
        return True



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

