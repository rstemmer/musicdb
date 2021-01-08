# MusicDB,  a music manager with web-bases UI that focus on music.
# Copyright (C) 2017-2021  Ralf Stemmer <ralf.stemmer@gmx.net>
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

import os
import shutil
import logging
import subprocess


class Filesystem(object):
    """
    This class provides an interface to the filesystem.
    The whole class assumes that it is used with an Unicode capable unix-style filesystem.

    Whenever I write about *root director* the path set in this class as root is meant.
    Otherwise I would call it *system root directory*.

    Some naming conventions:

        * **abspath:** Absolute path. They *always* start with a ``"/"``.
        * **relpath:** Relative path - Relative to the root directory. They should *not* start with a ``"./"``. This leads to undefined behavior!
        * **xpath:** Can be absolute or relative.


    Args:
        root(str): Path to the internal used root directory. It is allowd to start with "./".

    Raises:
        ValueError: if the root path does not start with ``"/"`` or does not exist
    """
    def __init__(self, root="/"):
        if root[0:2] == "./":
            root = os.path.abspath(root)

        if root[0] != "/":
            raise ValueError("invalid root-path: \""+root+"\" does not start with \"/\"")
        if not os.path.isdir(root):
            logging.error("invalid root-path: \""+root+"\"")
            raise ValueError("invalid root-path: \""+root+"\" does not exist")

        self._root = root



    def RemoveRoot(self, abspath):
        """
        This method makes a path relative to the root path.
        The existence of the path gets not checked!

        Args:
            abspath (str): A path that shall be made relative

        Returns:
            A relative path to the root directory

        Raises:
            ValueError: If the path is not inside the root path

        Example:

            .. code-block:: python
                
                fs = Filesystem("/data/music")

                abspath = "/data/music/Artist/Album"
                relpath = fs.RemoveRoot(abspath)
                print(relpath)  # > Artist/Album

                _ = fs.RemoveRoot("/data/backup/Artist/Album")
                # -> ValueError-Excpetion
        """
        if abspath[0:len(self._root)] != self._root:
            raise ValueError("Path \""+abspath+"\" has not the expected root of \""+self._root+"\"")

        relpath = abspath[len(self._root) + 1:] # +1 to remove the / between root and subdir
        return relpath
        


    def AbsolutePath(self, xpath):
        """
        This method returns an absolute path by adding the root directory to the path.
        If the path is already absolute (starts with ``"/"``) it gets returned as it is.

        If the path starts with ``"./"`` the root path gets prepended.

        If path is exact ``"."``, the root path gets returned.

        Args:
            xpath (str): A relative or absolute path

        Returns:
            An absolute path

        Raises:
            TypeError: If *xpath* is ``None``
        """
        if xpath == None:
            TypeError("xpath must have a value!")

        if xpath[0] == "/":
            abspath = xpath
        elif xpath[0:2] == "./":
            abspath = os.path.join(self._root, xpath[2:])
        elif xpath == ".":
            abspath = self._root
        else:
            abspath = os.path.join(self._root, xpath)
        return abspath



    def AssertDirectory(self, xpath):
        """
        Raises an AssertionError if :meth:`~lib.filesystem.Filesystem.IsDirectory` fails.
        """
        retval = self.IsDirectory(xpath)
        if retval == False:
            raise AssertionError("invalid path: \""+xpath+"\"")

        return True

    
    def IsDirectory(self, xpath):
        """
        This method checks if a directory exists.

        Args:
            xpath (str): A relative or absolute path to a directory

        Returns:
            ``True`` if the directory exists, otherwise ``False``.
        """
        abspath = self.AbsolutePath(xpath)

        if not os.path.isdir(abspath):
            return False
        return True



    def AssertFile(self, xpath):
        """
        Raises an AssertionError if :meth:`~lib.filesystem.Filesystem.IsFile` fails.
        """
        retval = self.IsFile(xpath)
        if retval == False:
            raise AssertionError("invalid file: \""+realpath+"\"")
        return True

    def IsFile(self, xpath):
        """
        This method checks if a file exists.

        Args:
            xpath (str): A relative or absolute path to a directory

        Returns:
            ``True`` if the directory exists, otherwise ``False``.
        """
        abspath = self.AbsolutePath(xpath)

        if not os.path.isfile(abspath):
            return False
        return True



    def Exists(self, xpath):
        """
        This method checks if a path exist. It can be a file or a directory

        Args:
            xpath (str): A relative or absolute path

        Returns:
            ``True`` if the path exists, otherwise ``False``.
        """
        abspath = self.AbsolutePath(xpath)
        return os.path.exists(abspath)



    def RemoveFile(self, xpath):
        """
        This method removes a file from the filesystem.

        .. warning::

            **Handle with care!**

        If the file does not exist, ``False`` gets returned

        Args:
            xpath (str): A relative or absolute path to a file

        Returns:
            ``False`` if the file does not exist.
        """
        abspath = self.AbsolutePath(xpath)
        
        if not self.IsFile(abspath):
            return False

        os.remove(abspath)
        return True



    def RemoveDirectory(self, xpath):
        """
        This method removes a directory tree from the filesystem.

        .. warning::

            **Handle with care!**

        If the file does not exist, ``False`` gets returned

        Args:
            xpath (str): A relative or absolute path to a directory

        Returns:
            ``False`` if the directory does not exist.
        """
        abspath = self.AbsolutePath(xpath)
        
        if not self.IsDirectory(abspath):
            return False

        shutil.rmtree(abspath, ignore_errors=True)
        return True



    def MoveFile(self, xsrcpath, xdstpath):
        """
        This method moves a file in the filesystem.
        **Handle with care!**

        If the source file does not exist, ``False`` gets returned.
        To move directories, see :meth:`~MoveDirectory`

        Args:
            xsrcpath (str): A relative or absolute path of the source
            xdstpath (str): A relative or absolute path where the source file shall be moves to

        Returns:
            ``False`` if the file does not exist.
        """
        abssource = self.AbsolutePath(xsrcpath)
        absdest   = self.AbsolutePath(xdstpath)

        if not self.IsFile(abssource):
            return False

        shutil.move(abssource, absdest)
        return True

    def MoveDirectory(self, xsrcpath, xdstpath):
        """
        This method moves a directory in the file system.
        **Handle with care!**

        If the source directory does not exist, ``False`` gets returned.
        To move files, see :meth:`~MoveFile`

        Args:
            xsrcpath (str): A relative or absolute path of the source
            xdstpath (str): A relative or absolute path where the source file shall be moves to

        Returns:
            ``False`` if the file does not exist.
        """
        abssource = self.AbsolutePath(xsrcpath)
        absdest   = self.AbsolutePath(xdstpath)

        if not self.IsDirectory(abssource):
            return False

        shutil.move(abssource, absdest)
        return True


    def CopyFile(self, xsrcpath, xdstpath):
        """
        This method copies a file.
        **Handle with care!**

        If the source file does not exist, ``False`` gets returned.
        If the destination file exists, it gets overwritten!
        When the destination path is a directory, the file gets copied into the directory.
        Filesystem metadata are copied as well.
        The UNIX shell alternative would be like the following line:

        .. code-block:: bash

            cp -p $SRCPATH $DSTPATH

        Args:
            xsrcpath (str): A relative or absolute path of the source
            xdstpath (str): A relative or absolute path where the source file shall be copied to

        Returns:
            ``False`` if the file does not exist.
        """
        abssource = self.AbsolutePath(xsrcpath)
        absdest   = self.AbsolutePath(xdstpath)

        if not self.IsFile(abssource):
            return False

        shutil.copyfile(abssource, absdest)
        return True


    

    def CreateSubdirectory(self, xnewpath):
        """
        This method creates a subdirectory.
        The directories are made recursively.
        So *xnewpath* can address the last directory of a path that will be created.

        Args:
            xnewpath: A path that addresses a new directory

        Returns:
            ``True``
        """
        absnewpath = self.AbsolutePath(xnewpath)
        os.makedirs(absnewpath, exist_ok=True)
        return True



    def GetFileExtension(self, xpath):
        """
        This method returns the file extension of the file addressed by *xpath*.
        The file must *not* exist.

        If xpath does not address a file or the file does not have an extension, ``None`` gets returned.
        Otherwise only the extension without the leading ``"."`` gets returned.

        Args:
            xpath (str): A path or name of a file that extension shall be returned

        Returns:
            The file extension without the leading dot, or ``None`` if the file does not have an extension.

        Example:
            
            .. code-block:: python

                fs  = FileSystem("/tmp")
                ext = fs.GetFileExtension("test.txt")
                if ext:
                    print("File Extension is: \"%s\""%(ext))    # in this example: "txt"

        """
        extension = os.path.splitext(xpath)[1]  # ([1] to get the extension from the returned tuple)
        if not extension:
            return None

        extension = extension[1:]               # remove the "." (".py"->"py")
        return extension



    def GetFileName(self, xpath):
        """
        This method returns the file name of the file addressed by *xpath*.
        It is not required and not checked that the file exist.
        The name of a file does not include the file extension.

        Args:
            xpath (str): A path or name of a file that name shall be returned

        Returns:
            The name of the file.

        Example:

            .. code-block:: python

                name = fs.GetFileName("this/is/a/test.txt")
                print(name) # "this/is/a/test"

        """
        name = os.path.split(xpath)[1]          # [1] get the filename from the returned tuple
        name = os.path.splitext(name)[0]        # [0] to get the name from the returned tuple
        return name



    def GetDirectory(self, xpath):
        """
        This method returns the directory a file or folder is stored in.

        Args:
            xpath (str): A path to a file (path must not exist)

        Returns:
            The directory of that file
        """
        return os.path.split(xpath)[0]



    def SetAttributes(self, xpath, owner, group, mode):
        """
        This method sets attributes for a file or directory.
        The *mode* is the access permissions as defined in the *stats* module.

        When *mode* is ``None``, the permissions will not be changed.
        When *owner* **or** *group* are ``None``, the ownership will not be changed.

        Mode-attributes can be an bitwise-OR combination of the following flags:

            * ``stat.S_ISUID``
            * ``stat.S_ISGID``
            * ``stat.S_ENFMT``
            * ``stat.S_ISVTX``
            * ``stat.S_IREAD``
            * ``stat.S_IWRITE``
            * ``stat.S_IEXEC``
            * ``stat.S_IRWXU``
            * ``stat.S_IRUSR``
            * ``stat.S_IWUSR``
            * ``stat.S_IXUSR``
            * ``stat.S_IRWXG``
            * ``stat.S_IRGRP``
            * ``stat.S_IWGRP``
            * ``stat.S_IXGRP``
            * ``stat.S_IRWXO``
            * ``stat.S_IROTH``
            * ``stat.S_IWOTH``
            * ``stat.S_IXOTH``


        Args:
            xpath (str): Path to the file or directory
            owner (str): Name of the owner of the file or directory
            group (str): Name of the group
            mode: Access permissions

        Returns:
            ``None``

        Example:

            .. code-block:: python
                
                import stat
                fs = Filesystem("/tmp")
                
                # -rw-rw-r--
                permissions = stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH
                fs.SetAttributes("test.txt", "user", "group", permissions)

                # drwxrwxr-x
                mode = stat.S_IRWXU | stat.S_IRWXG | stat.S_IROTH | stat.S_IXOTH
                fs.SetAttributes("testdirectory", None, None, mode) # make directory writeable for group members

        """
        abspath = self.AbsolutePath(xpath)
        if mode != None:
            os.chmod(abspath, mode)
        if owner != None and group != None:
            shutil.chown(abspath, owner, group)
        return None



    def GetModificationDate(self, xpath):
        """
        This method returns the date when a file or directory was modified the last time.
        (See `os.path.getmtime <https://docs.python.org/3/library/os.path.html#os.path.getmtime>`_)

        Args:
            xpath (str): Path to the file or directory

        Returns:
            The modification date of the file or directory as unix time value in seconds (integer)

        Example:
            
            .. code-block:: python

                fs = Filesystem("/data/music/")
                cdate = fs.GetModificationDate("Rammstein") # Possible creation date of /data/music/Rammstein directory
                print(cdate)

        """
        abspath = self.AbsolutePath(xpath)
        mtime = int(os.path.getmtime(abspath))
        return mtime



    def ListDirectory(self, xpath=None):
        """
        This method returns a list of entries in the directory addressed by *xpath*.
        The list can contain files and directories.
        If *xpath* is not a directory, an empty list will be returned.
        If *xpath* is ``None``, the root directory will be used.
        The list contains only the names including hidden files that starts with a ``"."``.
        The special directories ``"."`` and ``".."`` are not included.

        Args:
            xpath (str): Path to a directory. If ``None`` the root directory will be used

        Returns:
            A list of entries in the directory.
        """
        if xpath == None:
            xpath = self._root

        abspath = self.AbsolutePath(xpath)
        if not self.IsDirectory(xpath):
            return []

        retval  = os.listdir(abspath)
        return retval



    # Returns a list with directories
    def GetSubdirectories(self, xparents=None, ignore=None):
        """
        This method returns a filtered list with subdirectories for one or more parent directories.
        If *xparents* is ``None``, the root directory will be used.
        Using the root directory leads to returning absolute paths!

        The *ignore* parameter is a list of names that will be ignored and won't appear in the returned list of subdirectories.

        Args:
            xparents: A parent directory or a list of parent directories
            ignore: A list of entries to ignore

        Returns:
            A list of paths being the parent directory plus the child directory

        Example:

            Get the subdirectories of the following file structure:

            .. code-block:: bash

                dir1/subdir/*
                dir1/testdir/*
                dir1/files
                dir2/test/*
                dir2/tmp/*

            .. code-block:: python

                subdirs = fs.GetSubdirectories(["dir1", "dir2"], ["tmp"])
                print(subdirs)  # > ['dir1/subdir', 'dir1/testdir', 'dir2/test']

        """

        if xparents == None:
            xparents = [self._root]
        elif type(xparents) != list:
            xparents = [xparents]

        if type(ignore) != list:
            ignore = [ignore]
        
        pathlist  = []

        for parent in xparents:
            self.AssertDirectory(parent)

            paths = []

            entries = self.ListDirectory(parent)
            for entry in entries:
                # check if entry shall be ignored
                if ignore and entry in ignore:
                    continue

                # create a complete path out of the enty-name (file or dir name)
                path = os.path.join(parent, entry)
                
                # check if this is a valid subdir
                if not self.IsDirectory(path):
                    continue

                # append valid path to the pathlist
                paths.append(path)

            pathlist.extend(paths)

        return pathlist



    def GetFiles(self, xparents=None, ignore=None):
        """
        This method returns a filtered list with files for one or more parent directories.
        If *xparents* is ``None``, the root directory will be used.
        If a parent path does not exist, an exception gets raised.

        The *ignore* parameter is a list of names that will be ignored and won't appear in the returned list of subdirectories.

        This method works like :meth:`~lib.filesystem.Filesystem.GetSubdirectories` but with files

        Args:
            xparents: A parent directory or a list of parent directories
            ignore: A list of entries to ignore

        Returns:
            A list of paths relative to the root directory, including the parent directory ("parent/filename")

        """

        if xparents == None:
            xparents = [self._root]
        elif type(xparents) != list:
            xparents = [xparents]

        if type(ignore) != list:
            ignore = [ignore]

        pathlist = []

        for parent in xparents:
            self.AssertDirectory(parent)

            paths = []

            entries = self.ListDirectory(parent)
            for entry in entries:
                # check if entry shall be ignored
                if ignore and entry in ignore:
                    continue

                # create a complete path
                path = os.path.join(parent, entry)

                # if it's a file, add it to the paths list, otherwise ignore it
                if not self.IsFile(path):
                    continue

                # append valid path to the pathlist
                paths.append(path)

            pathlist.extend(paths)

        return pathlist



    def Execute(self, commandline):
        """
        Executes an external program.
        The command line is a list of arguments with the executable name as first element.
        So ``commandline[0]`` is the program name like ``"ls"`` and the next elements are a list of arguments to this program (like ``"-l", "-h"``).
        All entries in this list must be of type string.

        The I/O interfaces *stderr*, *stdout* and *stdin* are piped to ``/dev/null``

        After executing the command line, a ``sync`` command gets executed.
        In the past there were lots of problems because a second process wanted to process data preprocessed from the first one,
        but those data were not completely written to the disk.        

        Args:
            commandline (list): command line split into the executable name and individual arguments

        Returns:
            *Nothing*

        Raises:
            TypeError: When one entry of the commandline list is not of type string
            ChildProcessError: If the return value of the executed program is not 0

        Example:

            The following python code results in the following command line

            .. code-block:: python
                
                try:
                    fs.Execute(["ls", "-l", "-h"])
                except ChildProcessError as e:
                    print(e)

            .. code-block:: bash

                ls -l -h 2> /dev/null > /dev/null < /dev/null
                sync

        """
        for entry in commandline:
            if type(entry) is not str:
                raise TypeError("All entries in the command line list must be of type string!")
        devnull = open(os.devnull, "w")
        retval = subprocess.run(commandline, stdin=devnull, stdout=devnull, stderr=devnull).returncode
        if retval != 0:
            raise ChildProcessError("%s returned %d" % (commandline[0], retval))
        # Make sure the data processed by the commandline is global available
        os.sync()


    ## returns an absolute path of PATH. If necessary, ROOT will automatically be added
    #def AbsolutePath(self, path):
    #    if path[0:len(self._root)] != self._root:
    #        path = os.path.join(self._root, path)
    #def IsDirectory(self, path, isabsolute=False):
    #def IsFile(self, path, isabsolute=False):
    #def ListDirectory(self, path):

    # TODO/FIXME: Sehr ähnlich zu TryAnalysePath aus mdbapi.database. Ggf irgendwie vereinen
    # -> no, they follow different ideas. But both require better documentation!

    # Check if a path is a valid artist path
    # The path should be relative to the music root directory, otherwise its obviously not valid
    # As all functions of this type, there is no guarantee
    def IsArtistPath(self, path, ignorealbums=None, ignoresongs=None, isabsolute=False):
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


    def AnalyseAlbumDirectoryName(self, albumdirname):
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
        


    def IsVideoPath(self, path, isabsolute=False):
        """
        This method checks if the given path is a possible path to a music video.
        It checks if the path follows the naming scheme and exists as file.

        Args:
            path (str): A path to a possible video file
            isabsolute (bool): Optional boolean in case the path is absolute. Then the root prefix gets removed.

        Returns:
            ``True`` if the path could be a video file, otherwise ``False``
        """
        if isabsolute:
            path = self.RemoveRoot(path)

        if not self.IsFile(path):
            logging.debug("Video path (%s) is not a file!", path)
            return False

        # Check path structure
        try:
            [artist, video] = path.split("/")
        except:
            logging.debug("Video path (%s) is not inside an artist directory!", path)
            return False

        if not self.AnalyseVideoFileName(video):
            logging.debug("Video name (%s) does not follow the scheme!", video)
            return False

        return True


    def AnalyseVideoFileName(self, videofilename):
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
        video = {}

        # Check for " - " spacer
        try:
            if videofilename[4:7] != " - ":
                return None
        except:
            return None

        # Try to get the release year
        try:
            release = videofilename.split(" - ")[0]
            release = int(release)
        except:
            return None
        video["release"] = release

        # Extract name and extension
        try:
            videofilename      = videofilename.split(" - ")[1]   # remove release part
            video["name"]      = self.GetFileName(videofilename)
            video["extension"] = self.GetFileExtension(videofilename)
        except:
            return None

        # Check extension
        if not video["extension"] in ["m4v", "mp4", "webm"]:
            return None

        return video



    def IsSongPath(self, path, isabsolute=False):
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


    def AnalyseSongFileName(self, songfilename):
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

        name         = " ".join(songfilename.split(" ")[1:])
        song["name"] = os.path.splitext(name)[0]

        number = songfilename.split(" ")[0]
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

        song["extension"] = os.path.splitext(songfilename)[1]
        if not song["extension"] in [".flac", ".mp3", ".m4a", ".aac", ".MP3"]:
            return None

        return song 


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

