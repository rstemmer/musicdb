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
This module provides a set of methods to manage the Music Directory.
The :class:`~MusicDirectory` is derived from :class:`musicdb.lib.filesystem.Filesystem`.
"""

import os
import shutil
import logging
import subprocess
from pathlib import Path
from typing  import Union, Optional
from musicdb.lib.fileprocessing import Fileprocessing


class MusicDirectory(Fileprocessing):
    """
    This class provides an interface to the Music Directory.
    The whole class assumes that it is used with an Unicode capable UNIX-style filesystem.
    It is derived from :class:`musicdb.lib.fileprocessing.Fileprocessing`.

    In comparison to the :class:`~musicdb.mdbapi.music.MusicDBMusic`, only the files are on focus, not the music database.
    Keep in mind that applying some of the methods of this class can harm the connection between the database entries and their associated files.

    Args:
        config: MusicDB configuration object
    """
    def __init__(self, config):
        Fileprocessing.__init__(self, config.directories.music)

        self.cfg = config

        # read lists with files and directories that shall be ignored by the scanner
        self.ignoreartists = self.cfg.music.ignoreartists
        self.ignorealbums  = self.cfg.music.ignorealbums
        self.ignoresongs   = self.cfg.music.ignoresongs




    def FixAttributes(self, path: Union[str, Path]):
        """
        This method changes the access permissions and ownership of a file or directory.
        Only the addressed files or directory's permissions gets changed, not their parents.

            * File permissions: ``rw-rw-r--``
            * Directory permissions: ``rwxrwxr-x``

        To update the access permissions the method :meth:`musicdb.lib.filesystem.Filesystem.SetAttributes` is used.

        Args:
            path (str/Path): Path to an artist, album or song, relative to the music directory

        Returns:
            ``True`` on success, otherwise ``False``

        Raises:
            ValueError: if path is neither a file nor a directory.
        """
        if self.IsDirectory(path):
            permissions = "rwxrwxr-x"
        elif self.IsFile(path):
            permissions = "rw-rw-r--"
        else:
            raise ValueError("Path \""+str(path)+"\" is not a directory or file")

        success = self.SetAccessPermissions(path, permissions)
        return success



    def AnalyseAlbumDirectoryName(self, albumdirname: str) -> dict:
        """
        This method analyses the name of an album directory.
        If it does not follow the scheme of an album directory name, ``None`` gets returned, otherwise the albumname and release year.

        The scheme is the following: ``{releaseyear} - {albumname}``.

        The return value is a dictionay with the following keys:

        release:
            An integer with the release year

        name:
            A string with the album name

        Args:
            albumdirname (str): Directory name of an album without any ``"/"``.

        Returns:
            A dictionary with release year and the album name, or ``None``

        Example:

            .. code-block:: python
                
                infos = fs.AnalyseAlbumDirectoryName("2000 - Testalbum")
                if infos:
                    print(infos["name"])    # 2000
                    print(infos["release"]) # Testalbum
        """
        album = {}
        try:
            album["release"] = int(albumdirname[0:4])

            if albumdirname[4:7] != " - ":
                return None

            album["name"] = albumdirname[7:]
        except:
            return None

        return album



    def AnalyseVideoFileName(self, videofilename: str) -> dict:
        """
        This method analyses the name of a video file.
        Only the file name is expected, not a whole path!
        If it does not follow the scheme, ``None`` gets returned, otherwise all information encoded in the name as dictionary.

        The scheme is the following: ``{release} - {videoname}.{extension}``

        The return value is a dictionary with the following keys:

        release:
            Release year as integer

        name:
            A string with the video name

        extension:
            file extension as string

        Args:
            videofilename (str): File name of an video without any ``"/"``.

        Returns:
            A dictionary on success, otherwise ``None``

        Example:

            .. code-block:: python
                
                infos = fs.AnalyseVideoFileName("2000 - This is a Video.m4v")
                if infos:
                    print(infos["release"])     # 2000
                    print(infos["name"])        # "This is a Video"
                    print(infos["extension"])   # "m4v"

        """
        if type(videofilename) == str:
            filename = videofilename
        else:
            filename = str(videofilename)

        video = {}

        # Check for " - " spacer
        try:
            if filename[4:7] != " - ":
                return None
        except:
            return None

        # Try to get the release year
        try:
            release = filename.split(" - ")[0]
            release = int(release)
        except:
            return None
        video["release"] = release

        # Extract name and extension
        try:
            filename           = filename.split(" - ")[1]   # remove release part
            video["name"]      = self.GetFileName(filename)
            video["extension"] = self.GetFileExtension(filename)
        except:
            return None

        # Check extension
        if not video["extension"] in ["m4v", "mp4", "webm"]:
            return None

        return video


    def AnalyseSongFileName(self, songfilename: str) -> dict:
        """
        This method analyses the name of a song file.
        If it does not follow the scheme, ``None`` gets returned, otherwise all information encoded in the name as dictionary.

        The scheme is the following: ``{songnumber} {songname}.{extension}`` or ``{cdnumber}-{songnumber} {songname}.{extension}``


        The return value is a dictionary with the following keys:

        cdnumber:
            CD number as integer or ``1`` if not given in the name

        number:
            Number of the song as integer

        name:
            A string with the song name

        extension:
            file extension as string

        Args:
            songfilename (str): File name of an song without any ``"/"``.

        Returns:
            A dictionary on success, otherwise ``None``

        Example:

            .. code-block:: python
                
                infos = fs.AnalyseSongFileName("05 This is a Song.mp3")
                if infos:
                    print(infos["cdnumber"])    # 1
                    print(infos["number"])      # 5
                    print(infos["name"])        # This is a Song
                    print(infos["extension"])   # mp3

        """
        song = {}

        # Split number and name
        name   = " ".join(songfilename.split(" ")[1:])
        number = songfilename.split(" ")[0]

        # Split name and file extension
        song["name"]      = self.GetFileName(name)
        song["extension"] = self.GetFileExtension(name)

        if not song["extension"] in [".flac", ".mp3", ".m4a", ".aac", ".MP3"]:
            return None

        # Split CD number and song number
        try:
            if "-" in number:
                [cdnumber, songnumber] = number.split("-")
                song["cdnumber"] = int(cdnumber)
                song["number"]   = int(songnumber)
            else:
                song["cdnumber"] = 1
                song["number"]   = int(number)
        except:
            return None

        return song 



    def AnalysePath(self, musicpath):
        """
        This method analyses a path to a song or video and extracts all the information encoded in the path.
        The path must consist of three parts: The artist directory, the album directory and the song file.
        For videos only two parts are expected: The artist directory and the video file

        A valid path has one the following structures: 
        
            * ``{artistname}/{albumrelease} - {albumname}/{songnumber} {songname}.{extension}``
            * ``{artistname}/{albumrelease} - {albumname}/{cdnumber}-{songnumber} {songname}.{extension}``
            * ``{artistname}/{videorelease} - {videoname}.{extension}``

        The returned dictionary holds all the extracted information from the scheme listed above.
        The following entries exists but may be ``None`` depending if the path addresses a video or song.

            * artist
            * release
            * album
            * song
            * video
            * songnumber
            * cdnumber
            * extension

        In case there is no *cdnumber* specified for a song, this entry is ``1``.
        The names can have all printable Unicode characters and of cause spaces.

        If an error occurs because the path does not follow the scheme, ``None`` gets returned.
        This method does not check if the path exists!

        Args:
            musicpath (str/Path): A path of a song including artist and album directory or a video including the artists directory.

        Returns:
            On success, a dictionary with information about the artist, album and song or video is returned.
            Otherwise ``None`` gets returned.
        """

        path = str(musicpath)

        # Define all possibly used variables to a avoid undefined behavior
        result = {}
        result["artist"]    = None
        result["album"]     = None
        result["song"]      = None
        result["video"]     = None
        result["release"]   = None
        result["songnumber"]= None
        result["cdnumber"]  = None
        result["extension"] = None
        artist = None
        album  = None
        song   = None
        video  = None

        # separate parts of the path
        parts = path.count("/")
        if parts == 1:  # This my be a video or an album (let's see if it is a directory)
            if self.IsDirectory(path):
                [artist, album] = path.split("/")[-2:]
            else:
                [artist, video] = path.split("/")[-2:]
        elif parts == 2: # This may be a song
            [artist, album, song] = path.split("/")[-3:]
        else:
            logging.warning("Analysing \"%s\" failed!", path)
            logging.warning("Path cannot be split into three parts {artist}/{album}/{song} or two parts {artist}/{video}")
            return None

        # analyze the artist information
        result["artist"] = artist

        # analyze the album information
        if album:
            albuminfos = self.AnalyseAlbumDirectoryName(album)
            if albuminfos == None:
                logging.warning("Analysing \"%s\" failed!", path)
                logging.warning("Unexpected album directory name. Expecting \"{year} - {name}\"")
                return None

            result["release"] = albuminfos["release"]
            result["album"]   = albuminfos["name"]

        # analyze the song information
        if song:
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

        # analyze the video information
        if video:
            videoinfos = self.AnalyseVideoFileName(video)
            if videoinfos == None:
                logging.warning("Analyzing \"%s\" failed!", path)
                logging.warning("Unexpected video file name. Expecting \"{year} - {name}.{extension}\"")
                return None

            result["release"]   = videoinfos["release"]
            result["video"]     = videoinfos["name"]
            result["extension"] = videoinfos["extension"]

        return result



    def TryAnalysePathFor(self, target="all", path=None):
        """
        This method checks if a path is valid for a specific target.

        The check is done in the following steps:

            #. Get all song paths
            #. Apply an information extraction on all found song paths using :meth:`~AnalysePath`

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
                artistpaths = self.GetSubdirectories(path,        self.ignoreartists)
                albumpaths  = self.GetSubdirectories(artistpaths, self.ignorealbums)
                songpaths   = self.GetFiles(albumpaths, self.ignoresongs)

            elif target == "artist":
                albumpaths  = self.GetSubdirectories(path, self.ignorealbums)
                songpaths   = self.GetFiles(albumpaths, self.ignoresongs)

            elif target == "album":
                songpaths   = self.GetFiles(path, self.ignoresongs)

            elif target == "song":
                songpaths   = [path]

            else:
                raise ValueError("target not in {all, artist, album, song}")

        except Exception as e:
            logging.error("The given path (\"%s\") was not a valid %s-path!\033[1;30m (%s)", path, target, str(e))
            return False

        n = len(songpaths)
        if n < 1:
            logging.error("No songs in %s-path (%s)", target, path)
            return False

        for songpath in songpaths:
            if not self.Exists(songpath):
                logging.error("The song path %s does not exist.", songpath)
                return False

        # Scan all song pathes - if they are not analysable, give an error
        for songpath in songpaths:
            result = self.AnalysePath(songpath)
            if result == False:
                logging.error("Invalid path: " + songpath)
                return False

        return True



    def EstimateContentTypeByPath(self, path):
        """
        This method tries to figure out if the path addresses an Artist, Album, Song or Video by analyzing the path.
        If is *not* checked if the path fulfills the Music Naming Scheme (See: :doc:`/usage/music`).

        The path must be relative.
        It is not checked if the file or directory exists.
        The result is just a guess an must be checked in detail for further processing.
        For example with :meth:`TryAnalysePathFor`.

        Args:
            path (str): Possible relative path for an Artist, Album, Song or Video

        Returns:
            A string ``"artist"``, ``"album"``, ``"song"``, ``"video"`` or ``None`` if none can be guessed.
        """
        contenttype = None
        parts       = path.count("/") + 1           # n slash means n+1 parts of a path
        suffix      = self.GetFileExtension(path)   # If there is a file extension, it may be a file

        # Try to check if path addresses a file.
        # This only works when the path exists.
        # If path does not exists, use the suffix-knowledge and just guess.
        isfile = False
        if self.Exists(path):
            isfile = self.IsFile(path)
        elif suffix != None:
            # Now check if something points against a file
            if len(suffix) != 3:
                isfile = False
            elif not suffix in ["m4a", "flac", "aac", "mp4", "mp3", "m4v"]:
                isfile = False
            else:
                iffile = True

        # Estimate path type
        if parts == 1:
            contenttype = "artist"
        elif parts == 2:
            if isfile:
                contenttype = "video"
            else:
                contenttype = "album"
        elif parts == 3:
            if isfile:
                contenttype = "song"

        return contenttype




    # TODO/FIXME: Sehr ähnlich zu TryAnalysePath aus mdbapi.database. Ggf irgendwie vereinen
    # -> no, they follow different ideas. But both require better documentation!

    # Check if a path is a valid artist path
    # The path should be relative to the music root directory, otherwise its obviously not valid
    # As all functions of this type, there is no guarantee
    def IsArtistPath(self, path, ignorealbums=None, ignoresongs=None, isabsolute=False):
        logging.warning("MusicDirectory.IsArtistPath is DEPRECATED")
        if isabsolute:
            path = self.RemoveRoot(path)

        if not self.IsDirectory(path):
            logging.debug("Artist path (%s) is not a directory!", path)
            return False

        if len(path.split("/")) != 1:
            logging.debug("Artist path (%s) is not inside music root directory!", path)
            return False

        albumpaths = self.GetSubdirectories(path, ignorealbums)
        for albumpath in albumpaths:
            #albumpath = os.path.join(path, albumdir)    # Create artist/album - path
            if not self.IsAlbumPath(albumpath, ignoresongs):
                return False
        return True


    def IsAlbumPath(self, path, ignoresongs=None, isabsolute=False):
        logging.warning("MusicDirectory.IsAlbumPath is DEPRECATED")
        if isabsolute:
            path = self.RemoveRoot(path)

        if not self.IsDirectory(path):
            logging.debug("Album path (%s) is not a directory!", path)
            return False

        # Check for "year - name of the album"
        try:
            [artist, album] = path.split("/")
        except:
            logging.debug("Album path (%s) is not inside an artist directory!", path)
            return False

        if not self.AnalyseAlbumDirectoryName(album):
            logging.debug("Album name (%s) does not follow the scheme!", album)
            return False

        # Check if there is at least one valid song
        songpaths = self.GetFiles(path, ignoresongs)
        for songpath in songpaths:
            if self.IsSongPath(songpath):
                return True
        return False



    def IsVideoPath(self, path: Union[str, Path], isabsolute: bool=False) -> bool:
        """
        This method checks if the given path is a possible path to a music video.
        It checks if the path follows the naming scheme and exists as file.

        Args:
            path (str): A path to a possible video file
            isabsolute (bool): Optional boolean in case the path is absolute. Then the root prefix gets removed.

        Returns:
            ``True`` if the path could be a video file, otherwise ``False``
        """
        logging.warning("MusicDirectory.IsAlbumPath is DEPRECATED")
        if isabsolute:
            path = self.RemoveRoot(path)

        if not self.IsFile(path):
            logging.debug("Video path (%s) is not a file!", path)
            return False

        # Check path structure
        try:
            [artist, video] = str(path).split("/")
        except:
            logging.debug("Video path (%s) is not inside an artist directory!", path)
            return False

        if not self.AnalyseVideoFileName(video):
            logging.debug("Video name (%s) does not follow the scheme!", video)
            return False

        return True



    def IsSongPath(self, path, isabsolute=False):
        logging.warning("MusicDirectory.IsAlbumPath is DEPRECATED")
        if isabsolute:
            path = self.RemoveRoot(path)

        if not self.IsFile(path):
            logging.debug("Song path (%s) is not a file!", path)
            return False

        try:
            [artist, album, song] = path.split("/")
            _ = int(album[0:4])
            number = song.split(" ")[0]
        except:
            logging.debug("Song path (%s) is not inside an artist/album-directory tree!", path)
            return False

        if album[4:7] != " - ":
            logging.debug("Album name (%s) does not follow the scheme!", album)
            return False

        try:
            if "-" in number:
                [cdnumber, songnumber] = number.split("-")
                _ = int(cdnumber)
                _ = int(songnumber)
            else:
                _ = int(number)
        except:
            logging.debug("Song name (%s) does not follow the scheme!", song)
            return False

        ext = os.path.splitext(song)[1]
        if not ext in [".flac", ".mp3", ".m4a", ".aac", ".MP3"]:
            logging.debug("Song file (%s) has an unsupported extension!", song)
            return False

        return True


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

