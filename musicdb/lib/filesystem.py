# MusicDB,  a music manager with web-bases UI that focus on music.
# Copyright (C) 2017 - 2022  Ralf Stemmer <ralf.stemmer@gmx.net>
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
import stat
import grp
import pwd
import logging
import subprocess
from pathlib import Path
from typing  import Union, Optional

import mimetypes
mimetypes.init()

class Filesystem(object):
    """
    This class provides an interface to the filesystem.
    The whole class assumes that it is used with an Unicode capable UNIX-style filesystem.

    Whenever I write about *root director* the path set in this class as root is meant.
    Otherwise I would call it *system root directory*.

    The root path must exist and must be a directory.

    Some naming conventions:

        * **abspath:** Absolute path. They *always* start with a ``"/"``.
        * **relpath:** Relative path - Relative to the root directory. They should *not* start with a ``"./"``. This leads to undefined behavior!
        * **xpath:** Can be absolute or relative.


    Args:
        root (str/Path): Path to the internal used root directory. It is allowed to start with "./".

    Raises:
        ValueError: If the root path does not exist
        TypeError: If root is not of type ``str`` or ``Path``.
    """
    def __init__(self, root="/"):
        if type(root) != Path and type(root) != str:
            raise TypeError("root path must be of type str or pathlib.Path");

        if type(root) == str:
            self._root = Path(root)
        else:
            self._root = root

        self._root = self._root.expanduser()
        self._root = self._root.resolve()

        if not self._root.is_dir():
            logging.error("root path \"%s\" is not an existing directory!", str(root))
            raise ValueError("root path \"%s\" is not an existing directory!"%(str(root)))



    def GetRoot(self):
        """
        Returns the root path.
        User name directories are resolved. The path is absolute.

        Returns:
            Returns a pathlib.Path object with the root path
        """
        return self._root



    def ToString(self, paths: Union[str, Path, list[Union[str, Path]]]) -> Union[str, list[str]]:
        """
        Converts a Path object or a list of path objects into a string or a list of strings

        Args:
            paths (str,Path,list): A single path or a list of paths

        Returns:
            A single string or a list of strings
        """
        if type(paths) != list:
            return str(paths)
        strings = [str(path) for path in paths]
        return strings



    def RemoveRoot(self, path: Union[str, Path]) -> Path:
        """
        This method makes a path relative to the root path.
        The existence of the path gets not checked!

        It is assumed that ``path`` is an absolute path.
        Anyway it will be processed by :meth:`~AbsolutePath` to resolve
        a user directory ``~``.

        Args:
            abspath (str, Path): A path that shall be made relative

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
        abspath = self.AbsolutePath(path)
        relpath = abspath.relative_to(self._root)   # Raises ValueError
        return relpath

    def TryRemoveRoot(self, path: Union[str, Path]) -> Path:
        """
        Like :meth:`~RemoveRoot` just that exceptions are suppressed.
        If an exception occurs, ``path`` gets returned as it is.
        """
        try:
            retval = self.RemoveRoot(path)
        except Exception:
            retval = Path(path)
        return retval
        


    def AbsolutePath(self, xpath: Union[str, Path]) -> Path:
        """
        This method returns an absolute path by adding the root directory to the path.
        If the path is already absolute (starts with ``"/"``) it gets returned as it is.
        
        If the path starts with a ``~`` the user home directories will be resolved.

        If path is exact ``"."``, the root path gets returned.

        In all other cases the root path gets prepended.

        Args:
            xpath (str/Path): A relative or absolute path

        Returns:
            An absolute path as Path object

        Raises:
            TypeError: If *xpath* is ``None``

        Example:

            .. code-block:: python

                fs   = Filesystem()
                home = fs.AbsolutePath("~")
                # PosixPath('/home/ralf')
                home = fs.ToString(home)
                # '/home/ralf'
        """
        if type(xpath) == str:
            path = Path(xpath)
        else:
            path = xpath

        # Check if already absolute
        if path.is_absolute():
            return path

        # Check if user directory
        if str(path)[0] == "~":
            return path.expanduser()

        # Make absolute
        path = self._root / path
        path = path.resolve()
        return path



    def AssertDirectory(self, xpath: Union[str, Path]) -> bool:
        """
        Raises an AssertionError if :meth:`~IsDirectory` fails.
        """
        retval = self.IsDirectory(xpath)
        if retval == False:
            raise AssertionError("Path \""+xpath+"\" is not a Directory")

        return True

    
    def IsDirectory(self, xpath: Union[str, Path]) -> bool:
        """
        This method checks if a directory exists.

        Args:
            xpath (str/Path): A relative or absolute path to a directory

        Returns:
            ``True`` if the directory exists, otherwise ``False``.
        """
        abspath = self.AbsolutePath(xpath)
        return abspath.is_dir()



    def AssertFile(self, xpath: Union[str, Path]):
        """
        Raises an AssertionError if :meth:`~musicdb.lib.filesystem.Filesystem.IsFile` fails.
        """
        retval = self.IsFile(xpath)
        if retval == False:
            raise AssertionError("Path \""+xpath+"\" is not a File")
        return True


    def IsFile(self, xpath: Union[str, Path]) -> bool:
        """
        This method checks if a file exists.

        Args:
            xpath (str/Path): A relative or absolute path to a directory

        Returns:
            ``True`` if the file exists, otherwise ``False``.
        """
        abspath = self.AbsolutePath(xpath)
        return abspath.is_file()



    def Exists(self, xpath: Union[str, Path]) -> bool:
        """
        This method checks if a path exist. It can be a file or a directory

        Args:
            xpath (str): A relative or absolute path

        Returns:
            ``True`` if the path exists, otherwise ``False``.
        """
        abspath = self.AbsolutePath(xpath)
        return abspath.exists()



    def RemoveFile(self, xpath: Union[str, Path]) -> bool:
        """
        This method removes a file from the filesystem.

        .. warning::

            **Handle with care!**

        If the file does not exist, ``False`` gets returned

        Args:
            xpath (str/Path): A relative or absolute path to a file

        Returns:
            ``False`` if the file does not exist.
        """
        abspath = self.AbsolutePath(xpath)
        
        if not self.IsFile(abspath):
            return False

        abspath.unlink()
        return True



    def RemoveDirectory(self, xpath: Union[str, Path]) -> bool:
        """
        This method removes a directory from the filesystem.

        .. warning::

            **Handle with care!**

        If the file does not exist, ``False`` gets returned

        Args:
            xpath (str/Path): A relative or absolute path to a directory

        Returns:
            ``False`` if the directory does not exist
        """
        abspath = self.AbsolutePath(xpath)
        
        if not self.IsDirectory(abspath):
            return False

        shutil.rmtree(abspath, ignore_errors=True)
        return True



    def MoveFile(self, xsrcpath: Union[str, Path], xdstpath: Union[str, Path]) -> bool:
        """
        This method moves a file in the filesystem.
        **Handle with care!**

        If the source file does not exist, ``False`` gets returned.
        To move directories, see :meth:`~MoveDirectory`.
        The directory in that the file shall be moved must exist.

        Args:
            xsrcpath (str/Path): A relative or absolute path of the source
            xdstpath (str/Path): A relative or absolute path where the source file shall be moves to

        Returns:
            ``False`` if the file or the destination directory does not exist
        """
        abssource = self.AbsolutePath(xsrcpath)
        absdest   = self.AbsolutePath(xdstpath)

        if not self.IsFile(abssource):
            return False

        try:
            shutil.move(abssource, absdest)
        except FileNotFoundError as e:
            return False
        return True

    def MoveDirectory(self, xsrcpath: Union[str, Path], xdstpath: Union[str, Path]) -> bool:
        """
        This method moves a directory in the filesystem.
        **Handle with care!**

        If the source directory does not exist, ``False`` gets returned.
        To move files, see :meth:`~MoveFile`.
        The directory in that the directory shall be moved in must exist.

        Args:
            xsrcpath (str/Path): A relative or absolute path of the source
            xdstpath (str/Path): A relative or absolute path where the source file shall be moves to

        Returns:
            ``False`` if the source directory does not exist.

        Example:

            .. code-block:: python

                # Tree:
                # dira/subdira/fa1.txt
                # dirb/

            fs.MoveDirectory("dira/subdira", "dirb")

                # Tree:
                # dira/
                # dirb/subdira/fa1.txt
        """
        abssource = self.AbsolutePath(xsrcpath)
        absdest   = self.AbsolutePath(xdstpath)

        if not self.IsDirectory(abssource):
            return False

        try:
            shutil.move(abssource, absdest)
        except FileNotFoundError as e:
            return False
        return True



    def Rename(self, xsrcpath: Union[str, Path], xdstpath: Union[str, Path]) -> bool:
        """
        Renames a file or a directory.
        If the destination path name exists, the method returns ``False``.
        Only the last part of a path is allowed to be different, otherwise the renaming fails.

        If the source file or directory does not exist, ``False`` gets returned.
        To move a file or directory to different places see :meth:`~MoveFile` or :meth:`~MoveDirectory`.

        Args:
            xsrcpath (str/Path): A relative or absolute path of the source
            xdstpath (str/Path): A relative or absolute path where the source file shall be moves to

        Returns:
            ``False`` if the source file or directory does not exist.

        Exception:
            OSError: When renaming is not possible

        Example:

            .. code-block:: python

                # Tree:
                # dira/fa1.txt
                # dira/fa2.txt
                # dirb/fb1.txt
                # dirb/fb2.txt

            fs.Rename("dira", "dirb")                   # -> Returns False, does nothing
            fs.Rename("dira", "dirc")                   # -> Returns True, renames dira to dirc
            fs.Rename("dira/fa1.txt", "dira/fa3.txt")   # -> Returns True, renames fa1.txt to fa3.txt
            fs.Rename("dira/fa1.txt", "dirb/fa3.txt")   # -> Returns False, does nothing
        """
        abssource = self.AbsolutePath(xsrcpath)
        abstarget = self.AbsolutePath(xdstpath)

        # Check that only the last part changed
        sourcebase = self.GetDirectory(abssource)
        targetbase = self.GetDirectory(abstarget)
        if sourcebase != targetbase:
            return False

        # if target exists, or source does not, do nothing
        if not self.Exists(abssource):
            return False
        if self.Exists(abstarget):
            return False

        abssource.rename(abstarget)
        return True



    def CopyFile(self, xsrcpath: Union[str, Path], xdstpath: Union[str, Path]) -> bool:
        """
        This method copies a file.
        **Handle with care!**

        If the source file does not exist, ``False`` gets returned.
        If the destination file exists, it gets overwritten!
        When the destination path is a directory, the file gets copied into the directory.
        All parent directories must exist, otherwise a ``FileNotFoundError`` exception gets raised.

        The UNIX shell alternative would be like the following line:

        .. code-block:: bash

            cp $SRCPATH $DSTPATH

        Args:
            xsrcpath (str/Path): A relative or absolute path of the source
            xdstpath (str/Path): A relative or absolute path where the source file shall be copied to

        Returns:
            ``False`` if the file does not exist.

        Excpetions:
            PermissionError: When there is no write access to the destination directory
            FileNotFoundError: When the destination directory does not exist
        """
        abssource = self.AbsolutePath(xsrcpath)
        absdest   = self.AbsolutePath(xdstpath)

        if not self.IsFile(abssource):
            return False

        shutil.copyfile(abssource, absdest)
        return True


    

    def CreateSubdirectory(self, xnewpath: Union[str, Path]) -> bool:
        """
        This method creates a subdirectory.
        The directories are made recursively.
        So *xnewpath* can address the last directory of a path that will be created.

        Args:
            xnewpath (str/Path): A path that addresses a new directory

        Returns:
            ``True``
        """
        absnewpath = self.AbsolutePath(xnewpath)
        absnewpath.mkdir(parents=True, exist_ok=True)
        return True



    def GetFileExtension(self, xpath: Union[str, Path]) -> str:
        """
        This method returns the file extension of the file addressed by *xpath*.
        It will not be checked if the file exists.

        If xpath does not address a file or the file does not have an extension, ``None`` gets returned.
        Otherwise only the extension without the leading ``"."`` gets returned.

        Args:
            xpath (str/Path): A path or name of a file that extension shall be returned

        Returns:
            The file extension without the leading dot, or ``None`` if the file does not have an extension.

        Example:
            
            .. code-block:: python

                fs  = FileSystem("/tmp")
                ext = fs.GetFileExtension("test.txt")
                if ext:
                    print("File Extension is: \"%s\""%(ext))    # in this example: "txt"

        """
        if type(xpath) == str:
            path = Path(xpath)
        else:
            path = xpath

        extension = path.suffix
        if extension == "":
            return None

        extension = extension[1:]               # remove the "." (".py"->"py")
        return extension


    def GuessMimeType(self, xpath: Union[str, Path]) -> str:
        """
        Derives the mime type based on the file extension.

        Args:
            xpath (str/Path): A path or name of a file

        Returns:
            The mime type as ``"type/subtype"``, or ``None`` if the mime type cannot be determined.

        Example:

            .. code-block:: python

                fs   = FileSystem("/tmp")

                type = fs.GuessMimeType("test.txt")
                print("MIME type is: \"%s\""%(type))    # in this example: "text/plain"

                type = fs.GuessMimeType("README")
                print("MIME type is: \"%s\""%(type))    # in this example: "None"

        """
        path = self.AbsolutePath(xpath)
        mimetype = mimetypes.guess_type(path)[0]
        return mimetype



    def GetFileName(self, xpath: Union[str, Path], incldir=True) -> str:
        """
        This method returns the file name of the file addressed by *xpath*.
        It is not required and not checked that the file exist.
        The name of a file does not include the file extension.

        If ``incldir`` is ``True`` (default), the full path including the directories is returd.
        So the returned path is the argument without any suffix.
        When ``xpath`` addresses a directory and ``inclddir`` is ``True``, the behavior is not defined!

        If ``incldir`` is ``False`` only the file name is returned without suffix and without directories.

        The return type is a string.

        Args:
            xpath (str/Path): A path or name of a file that name shall be returned

        Returns:
            The name of the file including directories if ``incldir==True``.

        Example:

            .. code-block:: python

                name = fs.GetFileName("this/is/a/test.txt")
                print(name) # "this/is/a/test"

                name = fs.GetFileName("this/is/a/test.txt", incldir=False)
                print(name) # "test"

                name = fs.GetFileName("this/is/a", incldir=False)
                print(name) # "a"

        """
        if type(xpath) == str:
            path = Path(xpath)
        else:
            path = xpath

        if incldir:
            suffix = path.suffix
            name   = str(path)[:-len(suffix)]
        else:
            file = Path(path.name)  # Get full file name from path
            name = file.stem        # Get only the name without suffix

        return str(name)

    def GetDirectoryName(self, xpath: Union[str, Path]) -> str:
        """
        See :meth:`~GetFileName`, but ``incldir`` is always ``False``.
        So this method returns the last directory of a path.
        """
        return self.GetFileName(xpath, incldir=False)



    def GetDirectory(self, xpath: Union[str, Path]) -> Path:
        """
        This method returns the directory a file or folder is stored in.
        If is not required and not checked if the path exists.

        Args:
            xpath (str/Path): A path to a file or directory

        Returns:
            The directory of that file

        Example:

            .. code-block:: python

                directory = fs.GetDirectory("this/is/a/test.txt")
                print(str(directory)) # "this/is/a"
        """
        directory = os.path.split(xpath)[0]
        return Path(directory)



    def GetOwner(self, xpath: Union[str, Path]) -> tuple[str,str]:
        """
        This method returns the owner of a file or directory.
        The owner is a tuple of a UNIX user and group as string

        Args:
            xpath (str/Path): Path to the file or directory

        Returns:
            A tuple (user, group) to which the file belongs to

        Example:

            .. code-block:: python

                fs = Filesystem("/tmp")
                user,group = fs.GetOwner("testfile.txt")
                print("User: " + user)      # "User: root"
                print("Group: " + group)    # "Group: root"
        """
        abspath = self.AbsolutePath(xpath)
        user    = abspath.owner()
        group   = abspath.group()
        return (user, group)



    def SetOwner(self, xpath: Union[str, Path], user: str, group: str) -> bool:
        """
        This method changes the ownership of a file or directory.

        Args:
            xpath (str/Path): Path to the file or directory
            user (str): Name of a valid UNIX user
            group (str): Name of a valid UNIX group

        Returns:
            ``True`` on success, otherwise ``False``
        """
        abspath = self.AbsolutePath(xpath)
        try:
            shutil.chown(abspath, user, group)
        except PermissionError as e:
            logging.error("Setting ownership of %s to %s:%s failed with error %s", abspath, user, group, str(e))
            return False

        return True



    def GetMode(self, xpath: Union[str, Path]) -> int:
        """
        This method returns the mode of a file.
        The mode consists of the ``stat`` attributes as listed in :meth:`~SetAttributes`.

        Only the first four octal digits will be returned.

        Args:
            xpath (str/Path): Path to the file or directory

        Returns:
            An integer with ``st_mode & 0o7777`` of the addressed file or directory.

        Example:

            .. code-block:: python

                fs = Filesystem("/tmp")
                mode = fs.GetMode("testfile.txt")
        """
        logging.warning("Filesystem.GetMode is DEPRECATED. Better use Filesystem.GetAccessPermissions")
        abspath  = self.AbsolutePath(xpath)
        mode     = abspath.stat()
        return mode.st_mode & 0o7777

    def GetAccessPermissions(self, xpath: Union[str, Path]) -> str:
        """
        This method returns the access mode (access permissions) of a file or a directory.
        The mode is represented as string as it is used to be when calling ``ls -l``.

        The returned string is defined as follows:

        * It consists of exact 9 characters.
        * 0…2: User access permissions (2: Set UID when ``"s"``)
        * 3…5: Group access permissions (5: Set GID when ``"s"``)
        * 6…8: Access permissions for others (8: Sticky when ``"t"``)
        * It uses the following set of characters: ``"rwxst-"``.

        Args:
            xpath (str/Path): Path to the file or directory

        Returns:
            A string representing the files/directories access mode

        Example:

            .. code-block:: python
                
                fs = Filesystem("/tmp")
                
                # Files at /tmp:
                # rw-rw-r-- test1.txt
                # rwxr-xr-x directory1
                # rwsr-x--t directory2
                fs.GetAccessPermissions("test1.txt")    # "rw-rw-r--"
                fs.GetAccessPermissions("directory1")   # "rwxr-xr-x"
                fs.GetAccessPermissions("directory2")   # "rwsr-x--t"
        """
        abspath  = self.AbsolutePath(xpath)
        perm     = abspath.stat()
        mode     = perm.st_mode
        string   = ""

        # user
        if(mode & stat.S_IRUSR):    string += "r"
        else:                       string += "-"
        if(mode & stat.S_IWUSR):    string += "w"
        else:                       string += "-"
        if(mode & stat.S_ISUID):    string += "s"
        elif(mode & stat.S_IXUSR):  string += "x"
        else:                       string += "-"
        # group
        if(mode & stat.S_IRGRP):    string += "r"
        else:                       string += "-"
        if(mode & stat.S_IWGRP):    string += "w"
        else:                       string += "-"
        if(mode & stat.S_ISGID):    string += "s"
        elif(mode & stat.S_IXGRP):  string += "x"
        else:                       string += "-"
        # other
        if(mode & stat.S_IROTH):    string += "r"
        else:                       string += "-"
        if(mode & stat.S_IWOTH):    string += "w"
        else:                       string += "-"
        if(mode & stat.S_ISVTX):    string += "t"
        elif(mode & stat.S_IXOTH):  string += "x"
        else:                       string += "-"

        return string



    def SetAccessPermissions(self, xpath: Union[str, Path], mode: str) -> bool:
        """
        This method sets the access mode (access permissions) of a file or directory.
        The mode is represented as string as it is used to be when calling ``ls -l``.

        The access mode string must fulfill the following specification:

        * It consists of exact 9 characters.
        * 0…2: User access permissions (2: Set UID when ``"s"``)
        * 3…5: Group access permissions (5: Set GID when ``"s"``)
        * 6…8: Access permissions for others (8: Sticky when ``"t"``)
        * It uses the following set of characters: ``"rwxst-"``.

        Unknown characters will be ignored as well as characters at unexpected positions.

        Args:
            xpath (str/Path): The file or directory that mode shall be changed
            mode (str): The new permissions to set
        
        Returns:
            ``True`` on success, otherwise ``False``

        Raises:
            ValueError: When *mode* does not have exact 9 characters.
            PermissionError: When setting mode is not allowed

        Example:

            .. code-block:: python

                fs.SetAccessPermissions("test.txt", "rwxr-x---")
                fs.SetAccessPermissions("test",     "rwxr-s--t")
        """
        if len(mode) != 9:
            raise ValueError("File access mode needs to have exact 9 characters (for example \"rwxrwxrwx\")");

        permissions = 0
        # user
        if(mode[0] == "r"): permissions |= stat.S_IRUSR
        if(mode[1] == "w"): permissions |= stat.S_IWUSR
        if(mode[2] == "x"): permissions |= stat.S_IXUSR
        if(mode[2] == "s"): permissions |= stat.S_ISUID
        # group
        if(mode[3] == "r"): permissions |= stat.S_IRGRP
        if(mode[4] == "w"): permissions |= stat.S_IWGRP
        if(mode[5] == "x"): permissions |= stat.S_IXGRP
        if(mode[5] == "s"): permissions |= stat.S_ISGID
        # other
        if(mode[6] == "r"): permissions |= stat.S_IROTH
        if(mode[7] == "w"): permissions |= stat.S_IWOTH
        if(mode[8] == "x"): permissions |= stat.S_IXOTH
        if(mode[8] == "t"): permissions |= stat.S_ISVTX

        abspath = self.AbsolutePath(xpath)

        try:
            logging.debug("Changing access permissions of %s to %s (%s)", abspath, mode, oct(permissions))
            abspath.chmod(permissions)
        except PermissionError as e:
            logging.debug("Setting mode of %s to %s failed with error %s", abspath, oct(permissions), str(e))
            raise e

        return True



    def CheckAccessPermissions(self, xpath: Union[str, Path] = ".") -> str:
        """
        This method can be used to check if a file or directory can be accessed.
        It returns a string with 3 characters that represent the read, write and execute flags.
        The returned string is specified as follows:

        * 3 Characters wide string
        * ``[0]``: ``"r"`` when read access is possible, otherwise ``"-"``
        * ``[1]``: ``"w"`` when write access is possible, otherwise ``"-"``
        * ``[2]``: ``"r"`` when the file can be executed or the directory can be entered. Otherwise ``"-"``

        The access is checked for the user ID and group ID of the process that calls this method.

        Args:
            xpath (str/Path): The file or directory that mode shall be changed. (Optional, default is ``"."``)
        
        Returns:
            A 3 character string representing the ``"rwx"`` access permissions.

        Example:

            .. code-block::

                fs.CheckAccessPermissions("test.txt") # "rw-"
                fs.CheckAccessPermissions("dir")      # "r-x"
                fs.CheckAccessPermissions("mydir")    # "rwx"
                fs.CheckAccessPermissions()           # "rwx"
        """
        # Get user, group
        owneruser, ownergroup = self.GetOwner(xpath)

        userid    = os.geteuid()
        thisuser  = pwd.getpwuid(userid).pw_name
        gid       = os.getegid()
        thisgroup = grp.getgrgid(gid).gr_name

        # Get permissions
        perm = list("---")
        mode = self.GetAccessPermissions(xpath)

        if thisuser == owneruser:
            if mode[0] == "r":  perm[0] = "r"
            if mode[1] == "w":  perm[1] = "w"
            if mode[2] != "-":  perm[2] = "x"

        if thisgroup == ownergroup:
            if mode[3] == "r":  perm[0] = "r"
            if mode[4] == "w":  perm[1] = "w"
            if mode[5] != "-":  perm[2] = "x"

        if mode[6] == "r":  perm[0] = "r"
        if mode[7] == "w":  perm[1] = "w"
        if mode[8] != "-":  perm[2] = "x"

        return "".join(perm)



    def SetAttributes(self, xpath: Union[str, Path], owner: Optional[str]=None, group: Optional[str]=None, mode: Optional[int]=None) -> bool:
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
            xpath (str/Path): Path to the file or directory
            owner (str): Name of the owner of the file or directory
            group (str): Name of the group
            mode: Access permissions

        Returns:
            ``False`` when updating the mode or ownership fails

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
        logging.warning("Filesystem.SetAttributes is DEPRECATED. Better use Filesystem.SetAccessPermissions")
        abspath = self.AbsolutePath(xpath)

        if mode != None:
            try:
                abspath.chmod(mode)
            except PermissionError as e:
                logging.error("Setting mode of %s to %s failed with error %s", abspath, oct(mode), str(e))
                return False

        if owner != None and group != None:
            try:
                shutil.chown(abspath, owner, group)
            except PermissionError as e:
                logging.error("Setting ownership of %s to %s:%s failed with error %s", abspath, owner, group, str(e))
                return False

        return True



    def GetModificationDate(self, xpath: Union[str, Path]) -> int:
        """
        This method returns the date when a file or directory was modified the last time.
        (See `os.path.getmtime <https://docs.python.org/3/library/os.path.html#os.path.getmtime>`_)

        Args:
            xpath (str/Path): Path to the file or directory

        Returns:
            The modification date of the file or directory as UNIX time value in seconds (integer)

        Example:
            
            .. code-block:: python

                fs = Filesystem("/data/music/")
                cdate = fs.GetModificationDate("Rammstein") # Possible creation date of /data/music/Rammstein directory
                print(cdate)

        """
        abspath = self.AbsolutePath(xpath)
        mtime   = int(os.path.getmtime(abspath))
        return mtime



    def ListDirectory(self, xpath: Union[str, Path, None]=None) -> list[Path]:
        """
        This method returns a list of entries in the directory addressed by *xpath*.
        The list can contain files and directories.
        If *xpath* is not a directory, an empty list will be returned.
        If *xpath* is ``None``, the root directory will be used.

        The list contains only the names (relative to root directory) including hidden files that starts with a ``"."``.
        The special directories ``"."`` and ``".."`` are not included.

        Args:
            xpath (str/Path): Path to a directory. If ``None`` the root directory will be used

        Returns:
            A list of entries (files and directories) in the directory.
        """
        if xpath == None:
            abspath = self._root
        else:
            abspath = self.AbsolutePath(xpath)

        if not self.IsDirectory(abspath):
            return []

        paths = [path for path in abspath.iterdir()]
        paths = [self.TryRemoveRoot(path) for path in paths]
        return paths



    def GetSubdirectories(self, xparents: Optional[list[Union[str, Path]]]=None, ignore: Optional[list[str,Path]]=None) -> list[Path]:
        """
        This method returns a filtered list with sub-directories for one or more parent directories.
        If *xparents* is ``None``, the root directory will be used.

        This method returns relative ``Path`` objects.
        If a path is not relative to the root path, then an absolute path is returned.

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

                fs = Filesystem("/tmp")

                subdirs = fs.GetSubdirectories(["dir1", "dir2"], ["tmp"])

                print(subdirs)  # > ['dir1/subdir', 'dir1/testdir', 'dir2/test']

        """

        if xparents == None:
            parents = [self._root]
        elif type(xparents) != list:
            parents = [xparents]
        else:
            parents = xparents

        # Make sure all paths are of type Path and relative
        parents = [Path(parent) for parent in parents]
        parents = [self.TryRemoveRoot(parent) for parent in parents]

        if type(ignore) != list:
            ignore = [ignore]
        
        pathlist  = []

        for parent in parents:
            self.AssertDirectory(parent)

            paths = []

            entries = self.ListDirectory(parent)
            for entry in entries:
                # check if entry shall be ignored
                name = self.GetDirectoryName(entry)
                if ignore and name in ignore:
                    continue

                # check if this is a valid sub-directory
                if not self.IsDirectory(entry):
                    continue

                # append valid path to the pathlist
                paths.append(entry)

            pathlist.extend(paths)

        return pathlist



    def GetFiles(self, xparents: Union[str,Path,None]=None, ignore: Optional[list[str,Path]]=None) -> list[Path]:
        """
        This method returns a filtered list with files for one or more parent directories.
        If *xparents* is ``None``, the root directory will be used.
        If a parent path does not exist, an exception gets raised.

        The *ignore* parameter is a list of names that will be ignored and won't appear in the returned list of subdirectories.

        All paths returned are relative to the root directory if possible.
        If not, the they are absolute.

        This method works like :meth:`~GetSubdirectories` but with files

        Args:
            xparents: A parent directory or a list of parent directories
            ignore: A list of entries to ignore

        Returns:
            A list of paths relative to the root directory, including the parent directory ("parent/filename")

        """
        if xparents == None:
            parents = [self._root]
        elif type(xparents) != list:
            parents = [xparents]
        else:
            parents = xparents

        # Make sure all paths are of type Path and relative
        parents = [Path(parent) for parent in parents]
        #parents = [self.TryRemoveRoot(parent) for parent in parents] # Removed for speed optimization reasons

        if type(ignore) != list:
            ignore = [ignore]

        pathlist = []

        for parent in parents:
            paths   = []
            entries = self.ListDirectory(parent)
            for entry in entries:
                # check if entry shall be ignored
                if ignore and entry.name in ignore:
                    continue

                # if it's a file, add it to the paths list, otherwise ignore it
                if not self.IsFile(entry):
                    continue

                # append valid path to the path list
                paths.append(entry)

            pathlist.extend(paths)

        return pathlist



    def Execute(self, commandline: list[str]):
        """
        Executes an external program.
        The command line is a list of arguments with the executable name as first element.
        So ``commandline[0]`` is the program name like ``"ls"`` and the next elements are a list of arguments to this program (like ``"-l", "-h"``).
        All entries in this list must be representable as string.

        The I/O interfaces *stderr*, *stdout* and *stdin* are piped to ``/dev/null``

        After executing the command line, a ``sync`` command gets executed.
        In the past there were lots of problems because a second process wanted to process data preprocessed from the first one,
        but those data were not completely written to the disk.        

        Args:
            commandline (list): command line split into the executable name and individual arguments

        Returns:
            *Nothing*

        Raises:
            TypeError: When one entry of the commandline list can not be converted to string
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
        commandline = [str(entry) for entry in commandline]

        devnull = open(os.devnull, "w")
        retval = subprocess.run(commandline, stdin=devnull, stdout=devnull, stderr=devnull).returncode
        if retval != 0:
            raise ChildProcessError("%s returned %d" % (commandline[0], retval))
        # Make sure the data processed by the commandline is global available
        os.sync()



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

