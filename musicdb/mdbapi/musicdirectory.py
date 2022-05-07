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
from musicdb.mdbapi.accesspermissions   import AccessPermissions


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
        self.ap  = AccessPermissions(self.cfg, self.cfg.directories.music)

        # read lists with files and directories that shall be ignored by the scanner
        self.ignoreartists = self.cfg.music.ignoreartists
        self.ignorealbums  = self.cfg.music.ignorealbums
        self.ignoresongs   = self.cfg.music.ignoresongs



    def RenameSongFile(self, oldpath, newpath):
        """
        Renames a song inside the Music Directory.
        In general it is not checked if the new path fulfills the Music Naming Scheme (See :doc:`/usage/music`).
        The position of the file should be plausible anyway.
        So a song file should be inside a artist/album/-directory.

        The complete path, relative to the Music Directory must be given.
        The artist and album directories must not be different.
        Only the file name can be different.

        If the old path does not address a file, the Method returns ``False``.
        If the new path does address an already existing file, the method returns ``False`` as well.
        No files will be overwritten.

        Args:
            oldpath (str): Path to the file that shall be renamed
            newpath (str): New name of the file

        Returns:
            ``True`` on success, otherwise ``False``

        Example:
            .. code-block:: Python

                // Will succeed
                oldpath = "Artist/2021 - Album Name/01 old file name.mp3"
                newpath = "Artist/2021 - Album Name/01 new file name.mp3"
                musicdirectory.RenameSongFile(oldpath, newpath)

                // Will succeed even when the song name does not fulfill the naming scheme for song files
                oldpath = "Artist/2021 - Album Name/old file name.mp3"
                newpath = "Artist/2021 - Album Name/new file name.mp3"
                musicdirectory.RenameSongFile(oldpath, newpath)

                // Will fail if because album name changed as well
                oldpath = "Artist/Old Album Name/Old Song Name.flac",
                newpath = "Artist/2021 - New Album Name/01 New Song Name.flac"
                musicdirectory.RenameSongFile(oldpath, newpath)

        """
        # Check if old path is a valid path to a file in the Music Directory
        if not self.IsFile(oldpath):
            logging.warning("Rename Music Path failed because old path \"%s\" does not exists inside the Music Directory", str(oldpath))
            return False

        # Check if new path addresses an already existing file
        if self.Exists(newpath):
            logging.warning("Rename Music Path failed because new path \"%s\" does already exist inside the Music Directory", str(newpath))
            return False

        # Check if path if path is plausible
        oldcontenttype = self.EstimateContentTypeByPath(oldpath)
        newcontenttype = self.EstimateContentTypeByPath(newpath)
        if oldcontenttype != "song":
            logging.warning("Old path (\"%s\") does not address a song. It was estimated as: %s \033[1;30m(Old path will not be renamed)", oldpath, oldcontenttype)
            return False

        if newcontenttype != "song":
            logging.warning("New path (\"%s\") does not address a song. It was estimated as: %s \033[1;30m(Old path will not be renamed)", newpath, newcontenttype)
            return False

        # Rename path
        logging.info("Renaming \033[0;36m%s\033[1;34m ➜ \033[0;36m%s", oldpath, newpath)
        try:
            success = self.Rename(oldpath, newpath)
        except Exception as e:
            logging.error("Renaming \"%s\" to \"%s\" failed with exception: %s \033[1;30m(Nothing changed, old path is still valid)", oldpath, newpath, str(e))
            success = False

        if not success:
            logging.warning("Renaming \"%s\" to \"%s\" failed. \033[1;30m(Nothing changed, old path is still valid)", oldpath, newpath)
            return False
        return True



    def RenameVideoFile(self, oldpath, newpath):
        """
        Renames a video inside the Music Directory.
        In general it is not checked if the new path fulfills the Music Naming Scheme (See :doc:`/usage/music`).
        The position of the file should be plausible anyway.
        So a song file should be inside a artist-directory.

        The complete path, relative to the Music Directory must be given.
        The artist and album directories must not be different.
        Only the file name can be different.

        If the old path does not address a file, the Method returns ``False``.
        If the new path does address an already existing file, the method returns ``False`` as well.
        No files will be overwritten.

        Args:
            oldpath (str): Path to the file that shall be renamed
            newpath (str): New name of the file

        Returns:
            ``True`` on success, otherwise ``False``

        Example:
            .. code-block:: Python

                // Will succeed
                oldpath = "Artist/2021 - old file name.m4v"
                newpath = "Artist/2021 - new file name.m4v"
                musicdirectory.RenameVideoFile(oldpath, newpath)

                // Will succeed even when the video name does not fulfill the naming scheme for video files
                oldpath = "Artist/old file name.m4v"
                newpath = "Artist/new file name.m4v"
                musicdirectory.RenameVideoFile(oldpath, newpath)

                // Will fail if because artist name changed as well
                oldpath = "Artist/Old Video Name.m4v",
                newpath = "Different Artist/2020 - New Video Name.m4v"
                musicdirectory.RenameVideoFile(oldpath, newpath)

        """
        # Check if old path is a valid path to a file in the Music Directory
        if not self.IsFile(oldpath):
            logging.warning("Rename Music Path failed because old path \"%s\" does not exists inside the Music Directory", str(oldpath))
            return False

        # Check if new path addresses an already existing file
        if self.Exists(newpath):
            logging.warning("Rename Music Path failed because new path \"%s\" does already exist inside the Music Directory", str(newpath))
            return False

        # Check if path if path is plausible
        oldcontenttype = self.EstimateContentTypeByPath(oldpath)
        newcontenttype = self.EstimateContentTypeByPath(newpath)
        if oldcontenttype != "video":
            logging.warning("Old path (\"%s\") does not address a video. It was estimated as: %s \033[1;30m(Old path will not be renamed)", oldpath, oldcontenttype)
            return False

        if newcontenttype != "video":
            logging.warning("New path (\"%s\") does not address a video. It was estimated as: %s \033[1;30m(Old path will not be renamed)", newpath, newcontenttype)
            return False

        # Rename path
        logging.info("Renaming \033[0;36m%s\033[1;34m ➜ \033[0;36m%s", oldpath, newpath)
        try:
            success = self.Rename(oldpath, newpath)
        except Exception as e:
            logging.error("Renaming \"%s\" to \"%s\" failed with exception: %s \033[1;30m(Nothing changed, old path is still valid)", oldpath, newpath, str(e))
            success = False

        if not success:
            logging.warning("Renaming \"%s\" to \"%s\" failed. \033[1;30m(Nothing changed, old path is still valid)", oldpath, newpath)
            return False
        return True



    def RenameAlbumDirectory(self, oldpath, newpath):
        """
        Renames an album directory.
        In general it is not checked if the new path fulfills the Music Naming Scheme (See :doc:`/usage/music`).
        The position of the album should be plausible anyway.
        So it must be placed inside an artist directory.

        The complete path, relative to the Music Directory must be given.
        Anyway, the artist directories must not be different.
        Only the album directory name can be different.

        If the old path does not address a directory, the Method returns ``False``.
        If the new path does address an already existing file or directory, the method returns ``False`` as well.
        No files will be overwritten.

        Args:
            oldpath (str): Path to the directory that shall be renamed
            newpath (str): New name of the file

        Returns:
            ``True`` on success, otherwise ``False``

        Example:
            .. code-block:: javascript

                // Will succeed
                oldpath = "Artist/2021 - Old Album Name"
                newpath = "Artist/2021 - New Album Name"
                musicdirectory.RenameAlbumDirectory(oldpath, newpath)

                // Will succeed even if the album name does not fulfill the naming requirements
                oldpath = "Artist/Old Album Name"
                newpath = "Artist/New Album Name"
                musicdirectory.RenameAlbumDirectory(oldpath, newpath)

                // Will fail because artist name changed as well.
                oldpath = "Artist/Old Album Name"
                newpath = "New Artist/2021 - New Album Name"
                musicdirectory.RenameAlbumDirectory(oldpath, newpath)

        """
        # Check if old path is a valid path to a file in the Music Directory
        if not self.IsDirectory(oldpath):
            logging.warning("Rename Album Path failed because old path \"%s\" does not exists inside the Music Directory", str(oldpath))
            return False

        # Check if new path addresses an already existing file
        if self.Exists(newpath):
            logging.warning("Rename Album Path failed because new path \"%s\" does already exist inside the Music Directory", str(newpath))
            return False

        # Check if path if path is plausible
        oldcontenttype = self.EstimateContentTypeByPath(oldpath)
        newcontenttype = self.EstimateContentTypeByPath(newpath)
        if oldcontenttype != newcontenttype:
            logging.warning("Old path (\"%s\") was estimated as \"%s\", the new one (\"%s\") as \"%s\". \033[1;30m(Old path will not be renamed)", oldpath, oldcontenttype, newpath, newcontenttype)
            return False

        if oldcontenttype != "album":
            logging.warning("Old path (\"%s\") was estimated as \"%s\". An Album was expected. \033[1;30m(Old path will not be renamed)", oldpath, oldcontenttype)
            return False

        # Rename path
        logging.info("Renaming \033[0;36m%s\033[1;34m ➜ \033[0;36m%s", oldpath, newpath)
        try:
            success = self.Rename(oldpath, newpath)
        except Exception as e:
            logging.error("Renaming \"%s\" to \"%s\" failed with exception: %s \033[1;30m(Nothing changed, old path is still valid)", oldpath, newpath, str(e))
            success = False

        if not success:
            logging.warning("Renaming \"%s\" to \"%s\" failed. \033[1;30m(Nothing changed, old path is still valid)", oldpath, newpath)
            return False
        return True



    def RenameArtistDirectory(self, oldpath, newpath):
        """
        Renames an artist directory.
        In general it is not checked if the new path fulfills the Music Naming Scheme (See :doc:`/usage/music`).
        The position of the artist should be plausible anyway.

        The complete path, relative to the Music Directory must be given.
        Anyway, the artist directories must not be different.
        Only the album directory name can be different.
        So it must be placed inside the music directory and not being a sub directory.

        If the old path does not address a directory, the Method returns ``False``.
        If the new path does address an already existing file or directory, the method returns ``False`` as well.
        No files will be overwritten.

        Args:
            oldpath (str): Path to the directory that shall be renamed
            newpath (str): New name of the file

        Returns:
            ``True`` on success, otherwise ``False``

        Example:
            .. code-block:: javascript

                oldpath = "Old Artist"
                newpath = "New Artist"
                musicdirectory.RenameArtistDirectory(oldpath, newpath)

        """
        # Check if old path is a valid path to a file in the Music Directory
        if not self.IsDirectory(oldpath):
            logging.warning("Rename Artist Path failed because old path \"%s\" does not exists inside the Music Directory", str(oldpath))
            return False

        # Check if new path addresses an already existing file
        if self.Exists(newpath):
            logging.warning("Rename Artist Path failed because new path \"%s\" does already exist inside the Music Directory", str(newpath))
            return False

        # Check if path if path is plausible
        oldcontenttype = self.EstimateContentTypeByPath(oldpath)
        newcontenttype = self.EstimateContentTypeByPath(newpath)
        if oldcontenttype != newcontenttype:
            logging.warning("Old path (\"%s\") was estimated as \"%s\", the new one (\"%s\") as \"%s\". \033[1;30m(Old path will not be renamed)", oldpath, oldcontenttype, newpath, newcontenttype)
            return False

        if oldcontenttype != "artist":
            logging.warning("Old path (\"%s\") was estimated as \"%s\". An Artist was expected. \033[1;30m(Old path will not be renamed)", oldpath, oldcontenttype)
            return False

        # Rename path
        logging.info("Renaming \033[0;36m%s\033[1;34m ➜ \033[0;36m%s", oldpath, newpath)
        try:
            success = self.Rename(oldpath, newpath)
        except Exception as e:
            logging.error("Renaming \"%s\" to \"%s\" failed with exception: %s \033[1;30m(Nothing changed, old path is still valid)", oldpath, newpath, str(e))
            success = False

        if not success:
            logging.warning("Renaming \"%s\" to \"%s\" failed. \033[1;30m(Nothing changed, old path is still valid)", oldpath, newpath)
            return False
        return True




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
        This method analyses a path to an artist, and album, a song or video and extracts all the information encoded in the path.
        For songs, path must consist of three parts: The artist directory, the album directory and the song file.
        For alums and videos only two parts are expected: The artist directory and the video file.
        For artist only one part.

        A valid path has one the following structures: 
        
            * ``{artistname}/{albumrelease} - {albumname}/{songnumber} {songname}.{extension}``
            * ``{artistname}/{albumrelease} - {albumname}/{cdnumber}-{songnumber} {songname}.{extension}``
            * ``{artistname}/{videorelease} - {videoname}.{extension}``
            * ``{artistname}/{albumrelease} - {albumname}``
            * ``{artistname}``

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
        This method also checks if the file or directory exists!

        The path must also address a file or directory inside the music directory.
        Anyway the path can be relative or absolute.

        Args:
            musicpath (str/Path): A path of a song including artist and album directory or a video including the artists directory.

        Returns:
            On success, a dictionary with information about the artist, album and song or video is returned.
            Otherwise ``None`` gets returned.
        """
        if not self.Exists(musicpath):
            logging.debug("Path \"%s\" does not exist in %s.", str(musicpath), self.GetRoot());

        path = self.TryRemoveRoot(musicpath)
        path = self.ToString(path)

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
        if parts == 0: # This must be an artist
            if self.IsDirectory(path):
                artist = path
        elif parts == 1: # This my be a video or an album (let's see if it is a directory)
            if self.IsDirectory(path):
                [artist, album] = path.split("/")[-2:]
            else:
                [artist, video] = path.split("/")[-2:]
        elif parts == 2: # This may be a song
            if self.IsFile(path):
                [artist, album, song] = path.split("/")[-3:]

        # analyze the artist information
        if artist:
            result["artist"] = artist
        else:
            logging.warning("Analysing \"%s\" failed!", path)
            logging.warning("Path cannot be split into three parts {artist}/{album}/{song} or two parts {artist}/{video}")
            return None

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
        logging.debug("Estimating content type: parts: %i, suffix: %s", parts, suffix)

        # Try to check if path addresses a file.
        # This only works when the path exists.
        # If path does not exists, use the suffix-knowledge and just guess.
        isfile = False
        if self.Exists(path):
            isfile = self.IsFile(path)
        elif suffix != None:
            # Now check if something points against a file
            if suffix in ["m4a", "flac", "aac", "mp4", "mp3", "m4v"]:
                isfile = True
            else:
                isfile = False

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



    def EvaluateAlbumDirectory(self, albumpath):
        """
        This method checks if a directory path is a valid album directory.
        Despite :meth:`~TryAnalysePath` and :meth:`AnalyseAlbumDirectoryName` this method does not care about the naming scheme.
        It checks the actual content and directory inside the file system.
        A valid album directory must fulfill the following criteria:

            * It must be an existing directory
            * MusicDB must have read and write access to this directory
            * The directory must only contain files, no sub directories
            * All files inside the directory must be readable and writable
            * At least one file inside the directory must be a song file

        Args:
            albumpath (str): Path to the album to check

        Returns:
            ``True if the directory is a valid album directory. Otherwise ``False``.
        """
        if not self.IsDirectory(albumpath):
            logging.debug("Invalid album directory: %s does not address an existing directory.", str(albumpath));
            return False

        if not self.ap.IsWritable(albumpath):
            logging.debug("Invalid album directory: MusicDB has no write access to %s.", albumpath);
            return False

        albumfiles = self.ListDirectory(albumpath)
        songfound  = False
        for albumfile in albumfiles:
            if not self.IsFile(albumfile):
                logging.debug("Invalid album directory: Album directory %s has at least one sub directory (%s) which should not be the case.", albumpath, albumfile);
                return False

            fileextension = self.GetFileExtension(albumfile)
            if fileextension in ["m4a", "flac", "aac", "mp4", "mp3"]:
                songfound = True

            if not self.ap.IsWritable(albumfile):
                logging.debug("Invalid album directory: Album directory %s has at least one read-only file (%s) which should not be the case.", albumpath, albumfile);
                return False

        if not songfound:
            logging.debug("Invalid album directory: Album directory %s has no song files.", albumpath);
            return False

        return True



    def EvaluateArtistDirectory(self, artistpath):
        """
        This method checks if a directory is a valid artist directory.
        In contrast to :meth:`~TryAnalysePath` this method does not care about the naming scheme.
        It checks the actual content, directory and sub directories inside the file system.

        A valid artist directory must fulfill the following criteria:

            * It must be an existing directory
            * MusicDB must have read and write access to this directory
            * All sub directories and files must be writable
            * There must be at least one valid album directory (Checked via :meth:`~EvaluateAlbumDirectory` or a video file

        Args:
            artistpath (str): Path to the artist to check

        Returns:
            ``True if the directory is a valid artist directory. Otherwise ``False``.
        """
        if not self.IsDirectory(artistpath):
            logging.debug("Invalid artist directory: %s does not address an existing directory.", str(artistpath));
            return False

        if not self.ap.IsWritable(artistpath):
            logging.debug("Invalid artist directory: MusicDB has no write access to %s.", artistpath);
            return False

        artistcontent = self.ListDirectory(artistpath)
        videofound    = False
        albumfound    = False
        for path in artistcontent:
            if not self.ap.IsWritable(path):
                logging.debug("Invalid artist directory: Artist directory %s has at least one read-only file or sub-directory (%s) which should not be the case.", artistpath, path);
                return False

            if self.IsFile(path):
                fileextension = self.GetFileExtension(path)
                if fileextension in ["webm", "mp4", "m4v"]:
                    videofound = True
            else:
                if self.EvaluateAlbumDirectory(path):
                    albumfound = True

        if not videofound and not albumfound:
            logging.debug("Invalid artist directory: Artist directory %s has no albums and no video files.", artistpath);
            return False

        return True



    def EvaluateMusicFile(self, musicpath):
        """
        This method checks if a file is a valid music file.
        In contrast to :meth:`~TryAnalysePath` this method does not care about the naming scheme.
        It checks the actual content inside the file system.

        A valid music file must fulfill the following criteria:

            * It must be an existing file
            * MusicDB must have read and write access to this file

        Args:
            musicpath (str): Path to the music file to check

        Returns:
            ``True if the file is a valid music file. Otherwise ``False``.
        """
        if not self.IsFile(musicpath):
            logging.debug("Invalid music file: %s does not address an existing file.", str(musicpath));
            return False

        if not self.ap.IsWritable(musicpath):
            logging.debug("Invalid music file: MusicDB has no write access to %s.", musicpath);
            return False

        return True



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

