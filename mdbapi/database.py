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
This module is the core of the music handling of MusicDB.
It is the interface between the music and its entries in the database (:mod:`lib.db.musicdb`).
"""

import os
import stat
import signal
from lib.filesystem     import Filesystem
from lib.metatags       import MetaTags
from lib.pidfile        import *                    # Check PID File…
from lib.cfg.musicdb    import MusicDBConfig
from lib.db.musicdb     import *
from lib.db.trackerdb   import TrackerDatabase      # To update when a song gets removed


class MusicDBDatabase(object):
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
        self.fs     = Filesystem(self.cfg.music.path)
        self.meta   = MetaTags(self.cfg.music.path)

        # -rw-rw-r--
        self.filepermissions= stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH
        # drwxrwxr-x
        self.dirpermissions = stat.S_IRWXU | stat.S_IRWXG | stat.S_IROTH | stat.S_IXOTH                 

        # read lists with files and directories that shall be ignored by the scanner
        self.ignoreartists = self.cfg.music.ignoreartists
        self.ignorealbums  = self.cfg.music.ignorealbums
        self.ignoresongs   = self.cfg.music.ignoresongs



    def FindLostPaths(self):
        """
        This method checks all artist, album and song entries if the pathes to their related directories and files are still valid.
        Entries with invalid paths gets returned in three lists: ``artists, albums, songs``

        Returns:
            A three lists of database entries with invalid paths. Empty lists if there is no invalid entrie.
        """
        lostartists = []
        lostalbums  = []
        lostsongs   = []

        # Check Artists
        artists = self.db.GetAllArtists()
        for artist in artists:
            if not self.fs.IsDirectory(artist["path"]):
                lostartists.append(artist)

        # Check Albums
        albums = self.db.GetAllAlbums()
        for album in albums:
            if not self.fs.IsDirectory(album["path"]):
                lostalbums.append(album)

        # Check Songs
        songs = self.db.GetAllSongs()
        for song in songs:
            if not self.fs.IsFile(song["path"]):
                lostsongs.append(song)

        return lostartists, lostalbums, lostsongs



    def FindNewPaths(self):
        """
        This method searches inside the music directory for valid artist, album and song paths.
        If those paths are not in the database, they will be returned.
        So this method returns three lists: ``artistpaths, albumpaths, songpaths``.
        Each representing an artist, album or song that is not known by the database yet.
        Files and directories in the configured ignore-list will be ignored.

        If a new directory was found, the subdirectories will not be added!
        So for a new album, the new songs are implicite and not listed in the new-songs-list.

        This method is very optimistic. It will also list empty directories.
        The user may want to check if the results of this method are valid for him.

        Further more this method is error tolerant. This means, if in the database is an invalid entry,
        this does not lead to errors. For example, if an album path gets renamed, this path will be returned.
        It does not lead to an error that the old path is still in the database.

        Returns:
            A three lists of paths that are valid but unknown by the database. Empty lists if there is no invalid entrie.
        """
        newartists = []
        newalbums  = []
        newsongs   = []

        # Check Artists
        artists          = self.db.GetAllArtists()
        knownartistpaths = [artist["path"] for artist in artists if self.fs.IsDirectory(artist["path"])]
        artistpaths      = self.fs.GetSubdirectories(None, self.ignoreartists)

        for path in artistpaths:
            path = self.fs.RemoveRoot(path)
            if path not in knownartistpaths:
                newartists.append(path)

        # Check Albums
        albums          = self.db.GetAllAlbums()
        knownalbumpaths = [album["path"] for album in albums if self.fs.IsDirectory(album["path"])]
        albumpaths      = self.fs.GetSubdirectories(knownartistpaths, self.ignorealbums)
        
        for path in albumpaths:
            if path not in knownalbumpaths:
                newalbums.append(path)

        # Check Songs
        songs           = self.db.GetAllSongs()
        knownsongpaths  = [song["path"] for song in songs if self.fs.IsFile(song["path"])]
        songpaths       = self.fs.GetFiles(knownalbumpaths, self.ignoresongs)

        for path in songpaths:

            # check if this is really an audio file
            extension = self.fs.GetFileExtension(path)
            if extension not in ["mp4", "aac", "m4a", "mp3", "flac", "MP3"]:
                continue

            if path not in knownsongpaths:
                newsongs.append(path)

        return newartists, newalbums, newsongs




    def FixAttributes(self, path):
        """
        This method changes the access permissions and ownership of a file or directory.
        Only the addressed files or directory's permissions gets changed, not their parents.

            * File permissions: ``rw-rw-r--``
            * Directory permissions: ``rwxrwxr-x``
            * Ownership as configured in the settings: ``[music]->owner``:``[music]->group``

        Args:
            path (str): Path to an artist, album or song, relative to the music directory

        Returns:
            *Nothing*

        Raises:
            ValueError if path is neither a file nor a directory.
        """
        # check if file or dir permissions must be used
        if self.fs.IsDirectory(path):
            permissions = self.dirpermissions
        elif self.fs.IsFile(path):
            permissions = self.filepermissions
        else:
            raise ValueError("Path \""+str(path)+"\" is not a directory or file")

        # change attributes and ownership
        self.fs.SetAttributes(path, self.cfg.music.owner, self.cfg.music.group, permissions)
        


    def AnalysePath(self, path):
        """
        This method analyses a path to a song and extracts all the information encoded in the path.
        The path must consist of three parts: The artist directory, the album directory and the song file.

        A valid path has one the following structures: 
        
            * ``{artistname}/{albumrelease} - {albumname}/{songnumber} {songname}.{extension}``
            * ``{artistname}/{albumrelease} - {albumname}/{cdnumber}-{songnumber} {songname}.{extension}``

        The returned dictionary holds all the extracted information.
        In case there is no *cdnumber*, this entry is ``1``.
        The names can have all printable Unicode characters and of cause spaces.

        If an error occurs because the path does not follow the scheme, ``None`` gets returned.
        This method does not check if the path exists!

        Args:
            path (str): A path of a song including artist and album directory.

        Returns:
            On success, a dictionary with information about the artist, album and song.
            Otherwise ``None`` gets returned.
        """
        result = {}

        # separate the artist album and song name stored in the filesystem
        try:
            [artist, album, song] = path.split("/")[-3:]
        except:
            logging.warning("Analysing \"%s\" failed!", path)
            logging.warning("path cannot be split into three parts: {artist}/{album}/{song}")
            return None

        # analyse the artist-infos
        result["artist"] = artist

        # analyse the album-infos
        albuminfos = self.fs.AnalyseAlbumDirectoryName(album)
        if albuminfos == None:
            logging.warning("Analysing \"%s\" failed!", path)
            logging.warning("Unexpected album directory name. Expecting \"{year} - {name}\"")
            return None

        result["release"] = albuminfos["release"]
        result["album"]   = albuminfos["name"]

        # analyse the song-infos
        try:
            songname   = song.split(" ")[1:]
            songnumber = song.split(" ")[0]

            try:
                [cdnumber, songnumber] = songnumber.split("-")
            except:
                cdnumber = 1

            songnumber = int(songnumber)
            cdnumber   = int(cdnumber)
            songname   = " ".join(songname)
            extension  = os.path.splitext(songname)[1][1:]  # get extension without leading "."
            songname   = os.path.splitext(songname)[0]      # remove extension
        except:
            logging.warning("Analysing \"%s\" failed!", path)
            logging.warning("Unexpected song file name. Expected \"[{cdnumber}-]{songnumber} {songname}.{ending}\".")
            return None

        result["song"]       = songname
        result["songnumber"] = songnumber
        result["cdnumber"]   = cdnumber
        result["extension"]  = extension

        return result



    def TryAnalysePathFor(self, target="all", path=None):
        """
        This method checks if a path is valid for a specific target.

        The check is done in the following steps:

            #. Get all song paths
            #. Apply an information extraction on all found song paths using :meth:`~mdbapi.database.MusicDBDatabase.AnalysePath`

        This guarantees, that all files are valid to process with MusicDB.

        Args:
            target (str): Optional, default value is ``"all"``. One of the following targets: ``"all"``, ``"artist"``, ``"album"`` or ``"song"``
            path (str): Optional, default value is ``None``. Path to an artist, album or song. If target is ``"all"``, path can be ``None``.

        Returns:
            ``True`` If the path is valid for the given target. Otherwise ``False`` gets returned.

        Raises:
            ValueError: when *target* is not ``"all"``, ``"artist"``, ``"album"`` or ``"song"``
        """
        if path == None and target != "all":
            logging.error("Path to check if it is a valid for %s may not be None!", target)
            return False

        # Get all song paths
        try:
            if target == "all":
                artistpaths = self.fs.GetSubdirectories(path,        self.ignoreartists)
                albumpaths  = self.fs.GetSubdirectories(artistpaths, self.ignorealbums)
                songpaths   = self.fs.GetFiles(albumpaths, self.ignoresongs)

            elif target == "artist":
                albumpaths  = self.fs.GetSubdirectories(path, self.ignorealbums)
                songpaths   = self.fs.GetFiles(albumpaths, self.ignoresongs)

            elif target == "album":
                songpaths   = self.fs.GetFiles(path, self.ignoresongs)

            elif target == "song":
                songpaths   = [path]

            else:
                raise ValueError("target not in {all, artist, album, song}")

        except Exception as e:
            logging.error("FATAL ERROR: The given path (\"%s\") was not a valid %s-path!\033[1;30m (%s)", path, target, str(e))
            return False

        n = len(songpaths)
        if n < 1:
            logging.error("No songs in %s-path (%s)", target, path)
            return False

        for songpath in songpaths:
            if not os.path.exists(songpath):
                logging.error("The song path %s does not exist.", songpath)
                return False

        # Scan all songpathes - if they are not analysable, give an error
        for songpath in songpaths:
            result = self.AnalysePath(songpath)
            if result == False:
                logging.error("Invalid path: " + songpath)
                return False

        return True



    def AddArtist(self, artistpath):
        """
        The *AddArtist* method adds a new artist to the database.
        This is done in the following steps:

            #. Check if the artist path is inside the music root directory
            #. Check if the artist is already in the database
            #. Extract the artist name from the path
            #. Set directory attributes and ownership using :meth:`~mdbapi.database.MusicDBDatabase.FixAttributes`
            #. Add artist to database
            #. Call :meth:`~mdbapi.database.MusicDBDatabase.AddAlbum` for all subdirectories of the artistpath. (Except for the directory-names in the *ignorealbum* list)

        Args:
            artistpath (str): Absolute or relative (to the music directory) path to the artist that shall be added to the database.

        Returns:
            ``None``

        Raises:
            ValueError: If the path does not address a directory
            ValueError: If artist is already in the database
        """
        # remove the leading part to the music directory
        try:
            artistpath = self.fs.RemoveRoot(artistpath) # remove the path to the musicdirectory
        except ValueError:
            pass

        if not self.fs.IsDirectory(artistpath):
            raise ValueError("Artist path " + artistpath + " is not a directory!")

        # Check if the artist already exists in the database
        artist = self.db.GetArtistByPath(artistpath)
        if artist != None:
            raise ValueError("Artist \"" + artist["name"] + "\" does already exist in the database.")
        
        # The filesystem is always right - Survivor of the "tag over fs"-apocalypse - THE FS IS _ALWAYS_ RIGHT!
        artistname = os.path.basename(artistpath)

        # fix attributes to fit in mdb environment before adding it to the database
        try:
            self.FixAttributes(artistpath)
        except Exception as e:
            logging.warning("Fixing file attributes failed with error: %s \033[1;30m(leaving permissions as they are)",
                    str(e))

        # add artist to database
        self.db.AddArtist(artistname, artistpath)
        artist = self.db.GetArtistByPath(artistpath)

        # Add all albums to the artist
        albumpaths = self.fs.GetSubdirectories(artistpath, self.ignorealbums)
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
        try:
            newpath = self.fs.RemoveRoot(newpath) # remove the path to the musicdirectory
        except:
            pass

        artist     = self.db.GetArtistById(artistid)
        artist["path"] = newpath
        artist["name"] = os.path.basename(newpath)
        self.db.WriteArtist(artist)

        albums = self.db.GetAlbumsByArtistId(artistid)
        for album in albums:
            albumpath    = album["path"]
            albumpath    = albumpath.split(os.sep)
            albumpath[0] = newpath
            albumpath    = os.sep.join(albumpath)
            if self.fs.IsDirectory(albumpath):
                self.UpdateAlbum(album["id"], albumpath)

        return None



    def AddAlbum(self, albumpath, artistid=None):
        """
        This method adds an album to the database in the following steps:

            #. Check if the album already exists in the database
            #. Get all songs of the album by getting all files inside the directory except those on the *ignoresongs*-list.
            #. Load the metadata from one of those songs using :meth:`lib.metatags.MetaTags.GetAllMetadata`
            #. Analyze the path of one of those songs using :meth:`~mdbapi.database.MusicDBDatabase.AnalysePath`
            #. If *artistid* is not given as parameter, it gets read from the database identifying the artist by its path.
            #. Set directory attributes and ownership using :meth:`~mdbapi.database.MusicDBDatabase.FixAttributes`
            #. Create new entry for the new album in the database and get the default values
            #. Add each song of the album to the database by calling :meth:`~mdbapi.database.MusicDBDatabase.AddSong`
            #. Write all collected information of the album into the database

        If adding the songs to the database raises an exception, that song gets skipped.
        The *numofsongs* value for the album is the number of actual existing songs for this album in the database.
        It is save to add the failed song later by using the :meth:`~mdbapi.database.MusicDBDatabase.AddSong` method.

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
        try:
            albumpath = self.fs.RemoveRoot(albumpath) # remove the path to the musicdirectory
        except ValueError:
            pass

        if not self.fs.IsDirectory(albumpath):
            raise ValueError("Artist path " + artistpath + " is not a directory!")

        # Check if the album already exists in the database
        album = self.db.GetAlbumByPath(albumpath)
        if album != None:
            raise ValueError("Album \"" + album["name"] + "\" does already exist in the database.")

        # This album dictionary gets filled with all kind of infors during this method.
        # At the end they are written into the database
        album = {}
        album["name"]       = None
        album["path"]       = albumpath

        # get all songs from the albums - this is important to collect all infos for the album entry
        paths = self.fs.GetFiles(albumpath, self.ignoresongs) # ignores also all directories

        # remove files that are not music
        songpaths = []
        for path in paths:
            if self.fs.GetFileExtension(path) in ["mp3", "m4a", "aac", "flac"]:
                songpaths.append(path)

        # analyse the first one for the album-entry
        self.meta.Load(songpaths[0])
        tagmeta = self.meta.GetAllMetadata()
        fsmeta  = self.AnalysePath(songpaths[0])
        if fsmeta == None:
            raise AssertionError("Analysing path \"%s\" failed!", songpaths[0])

        # usually, the filesystem is always right, but in case of iTunes, the meta data are
        # FIX: NO! THEY ARE NOT! - THE FILESYSTEM IS _ALWAYS_ RIGHT!
        album["name"]    = fsmeta["album"]
        album["release"] = fsmeta["release"]
        album["origin"]  = tagmeta["origin"]
        
        if artistid == None:
            # the artistname IS the path, because thats how the fsmeta data came from
            artist = self.db.GetArtistByPath(fsmeta["artist"])
            if artist == None:
                raise AssertionError("Artist for the album \"" + album["name"] + "\" is not avaliable in the database.")
            artistid = artist["id"]

        # fix attributes to fit in mdb environment before adding it to the database
        try:
            self.FixAttributes(albumpath)
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

        self.db.WriteAlbum(album)
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
        album = self.db.GetAlbumById(albumid)
        try:
            newpath = self.fs.RemoveRoot(newpath) # remove the path to the musicdirectory
        except:
            pass

        album["path"] = newpath

        # get all songs from the albums - this is important to collect all infos for the album entry
        songpaths = self.fs.GetFiles(newpath, self.ignoresongs) # ignores also all directories

        # analyse the first one for the album-entry
        self.meta.Load(songpaths[0])
        tagmeta = self.meta.GetAllMetadata()
        fsmeta  = self.AnalysePath(songpaths[0])
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
            songpath[0] = newpath                   # [artist/album, song]  // add new artist/album string
            songpath    = os.sep.join(songpath)

            # If it does not work, it does not matter.
            # This can be fixed by the user later.
            # It may faile because not only the albumname changed,
            # but also the files inside
            if self.fs.IsFile(songpath):
                self.UpdateSong(song["id"], songpath)

        return None



    def AddSong(self, songpath, artistid=None, albumid=None):
        """
        This method adds a song to the MusicDB database.
        To do so, the following steps were done:

            #. Check if the song already exists in the database
            #. Load the metadata from the song using :meth:`lib.metatags.MetaTags.GetAllMetadata`
            #. Analyze the path of one of the song using :meth:`~mdbapi.database.MusicDBDatabase.AnalysePath`
            #. If *artistid* is not given as parameter, it gets read from the database identifying the artist by its path.
            #. If *albumid* is not given as parameter, it gets read from the database identifying the album by its path.
            #. Set file attributes and ownership using :meth:`~mdbapi.database.MusicDBDatabase.FixAttributes`
            #. Add song to database
            #. If the parameter *albumid* was ``None`` the *numofsongs* entry of the determined album gets incremented
            #. If there are lyrics in the song file, they get also inserted into the database

        In case the album ID is set, this method assumes that its database entry gets managed by the :meth:`~mdbapi.database.MusicDBDatabase.AddAlbum` method.
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
        try:
            songpath = self.fs.RemoveRoot(songpath) # remove the path to the musicdirectory
        except:
            pass

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
        fsmeta  = self.AnalysePath(songpath)
        if fsmeta == None:
            raise AssertionError("Invalid path-format: " + songpath)

        # Collect all data needed for the song-entry (except the song ID)
        # Remember! The filesystem is always right
        song = {}
        song["artistid"] = artistid # \_ In case they are None yet, they will be updated later in the code
        song["albumid"]  = albumid  # /
        song["path"]     = songpath
        song["number"]   = fsmeta["songnumber"]
        song["cd"]       = fsmeta["cdnumber"]
        song["disabled"] = 0
        song["playtime"] = tagmeta["playtime"]
        song["bitrate"]  = tagmeta["bitrate"]
        song["likes"]    = 0
        song["dislikes"] = 0
        song["qskips"]   = 0
        song["qadds"]    = 0
        song["qremoves"] = 0
        song["favorite"] = 0
        song["qrndadds"] = 0
        song["lyricsstate"] = SONG_LYRICSSTATE_EMPTY

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
            self.FixAttributes(songpath)
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
        try:
            newpath = self.fs.RemoveRoot(newpath) # remove the path to the musicdirectory
        except:
            pass
        song     = self.db.GetSongById(songid)
        songpath = newpath

        # Get all information from the songpath and its meta data
        try:
            self.meta.Load(songpath)
        except Exception as e:
            logging.excpetion("Metadata of file %s cannot be load. Error: %s", str(songpath), str(e))
            raise e

        tagmeta = self.meta.GetAllMetadata()
        fsmeta  = self.AnalysePath(songpath)
        if fsmeta == None:
            raise AssertionError("Invalid path-format: " + songpath)

        # Remember! The filesystem is always right
        song["path"]     = songpath
        song["name"]     = fsmeta["song"] 
        song["number"]   = fsmeta["songnumber"]
        song["cd"]       = fsmeta["cdnumber"]
        song["playtime"] = tagmeta["playtime"]
        song["bitrate"]  = tagmeta["bitrate"]

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
        tracker = TrackerDatabase(self.cfg.tracker.dbpath)

        # remove from music.db
        self.db.RemoveSong(songid)
        # remove from tracker.db
        tracker.RemoveSong(songid)

        return None



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
        try:
            songpath = self.fs.RemoveRoot(songpath) # remove the path to the musicdirectory
        except ValueError:
            # if RemoveRoot raises an ValueError, this only means that songpath is already a realtive path
            pass
        except Exception as e:
            logging.error("Invalid song path: %s. \033[1;30m(No lyrics will be loaded)", str(e))
            return False

        # Get all information from the songpath and its meta data
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



    def UpdateSongPath(self, newsongpath, oldsongpath):
        """
        This method can be used to update a song.

        The new song file must be names as necessary for MusicDB.
        It is OK when the songs filename changes, as long as the cd and track number are equal to the old file.

        The following steps will be done:

            #. Get database entry from old song
            #. Analyse new songs metatags and file name
            #. Check if it is a valid replacement
            #. Replace files (and creating a backup of the old song)
            #. Try to set file attributes
            #. Update database

        .. attention::

            If something went wrong, ``False`` gets returned.
            Then only the new file must be replaced by the backup file.
            The database is still consistent.

        .. warning::

            A single CD song cannot be updated to a multi CD one

            The old and new song must have the same track number

        Args:
            newsongpath (str): Absolute path to the new song
            oldsongpath (str): Absolute path to the current song

        Return:
            ``True`` on success, otherwise ``False``

        Example:

            .. code-block:: python
                
                # replace an old mp3 by a new flac file
                db.UpdateSongPath("/tmp/downloads/23 Is Everywhere.flac", "/data/music/Illuminati/2023 - Sheeple/23 Is Everwhere.mp3")
        """
        if type(newsongpath) != str or type(oldsongpath) != str:
            logging.error("Arguments of wrong type. Strings were expected")
            return False

        # Get song database entry
        logging.debug("Getting old song database entry …")
        try:
            relsongpath = self.fs.RemoveRoot(oldsongpath)
        except ValueError:
            logging.warning("The path \"%s\" is not inside the music root directory! \033[1;30m(Doing nothing)", oldsongpath)
            return False

        song = self.db.GetSongByPath(relsongpath)
        if not song:
            logging.warning("The song with path \"%s\" does not exist in the database. \033[1;30m(Doing nothing)", relsongpath)
            return False

        # Analyse new song
        logging.debug("Analysing new song …")
        newmetadata = MetaTags("/")
        try:
            print("source: " + newsongpath)
            newmetadata.Load(newsongpath)
        except Exception as e:
            logging.warning("Loading meta data from file \"%s\" failed with error: %s! \033[1;30m(Doing nothing)", newsongpath, str(e))
            return False
        tagmeta = newmetadata.GetAllMetadata()
        
        songfilename = newsongpath.split("/")[-1]
        fsmeta  = self.fs.AnalyseSongFileName(songfilename)
        if fsmeta == None:
            logging.warning("Analysing song file name \"%s\" failed! \033[1;30m(Doing nothing)", songfilename)
            return False

        # Check if this is a valid replacement
        logging.debug("Checking if replacement is valid …")
        if song["cd"]     != fsmeta["cdnumber"]:
            logging.warning("Old CD number (%s) is not equal to the new CD number (%s)! \033[1;30m(Doing nothing)", 
                    str(song["cd"]),
                    str(fsmeta["cdnumber"]))
            return False

        if song["number"] != fsmeta["number"]:
            logging.warning("Old song number (%s) is not equal to the new song number (%s)! \033[1;30m(Doing nothing)", 
                    str(song["number"]),
                    str(fsmeta["number"]))
            return False


        # Replace files
        logging.debug("Replacing song file …")
        albumpath      = self.db.GetAlbumById(song["albumid"])["path"]
        relbackup      = relsongpath + ".bak"
        newrelsongpath = albumpath + "/" + os.path.basename(newsongpath)

        logging.debug(" mv \"%s\" \"%s\"", relsongpath, relbackup)
        try:
            self.fs.MoveFile(relsongpath, relbackup)
        except Exception as e:
            logging.warning("Creating backup failed! \033[1;30m(Doning nothing)")
            return False

        logging.debug(" cp \"%s\" \"%s\"", newsongpath, newrelsongpath)
        try:
            self.fs.CopyFile(newsongpath, newrelsongpath)
        except Exception as e:
            logging.error("Copying new song fail failed! Trying to restore backup. Check if file \"%s\" is back in place!", oldsongpath)
            self.fs.MoveFile(relbackup, relsongpath)
            return False

        # Update database
        logging.debug("Updating database …")
        song["path"]     = newrelsongpath
        song["playtime"] = tagmeta["playtime"]
        song["bitrate"]  = tagmeta["bitrate"]
        song["name"]     = fsmeta["name"] 

        try:
            self.FixAttributes(newsongpath)
        except Exception as e:
            logging.warning("Fixing file attributes failed with error: %s \033[1;30m(leaving permissions as they are)",
                    str(e))

        # write to database
        self.db.WriteSong(song)
        return True



    def UpdateServerCache(self):
        """
        This method signals the MusicDB Websocket Server to update its caches.
        This should always be done when there are new artists, albums or songs added to the database.

        Returns:
            *Nothing*
        """
        serverpid = CheckPIDFile(self.cfg.server.pidfile)
        if not serverpid:
            return  # server not running, so no cacheupdate needed
        try:
            os.kill(serverpid, signal.SIGUSR1)
        except Exception as e:
            print("\033[1;33mWARNING:\033[0m Updating servercache failed with exception:")
            print(e)
            print("\033[1;34mTry to update manually: \033[1;36mkill -USR1 "+str(self.cfg.server.pidfile)+"\033[0m")


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

