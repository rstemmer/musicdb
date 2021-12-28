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
This module provides a set of methods to check and manage the access permissions to several files and directories maintained by MusicDB.
"""

import logging
from musicdb.lib.filesystem import Filesystem


class AccessPermissions(object):
    """
    Args:
        config: MusicDB configuration object
        rootdirectory: When paths are give, they are all considered relative to this root directory (optional, default is ``"/"``)
    """
    def __init__(self, config, rootdirectory="/"):
        self.cfg = config
        self.fs  = Filesystem(rootdirectory)
        #self.musicdir   = Filesystem(self.cfg.directories.music)
        #self.artworkdir = Filesystem(self.cfg.directories.artwork)
        #self.webdatadir = Filesystem(self.cfg.directories.webdata)
        #self.tasksdir   = Filesystem(self.cfg.directories.tasks)
        #self.uploadsdir = Filesystem(self.cfg.directories.uploads)
        #self.statedir   = Filesystem(self.cfg.directories.state)



    def IsReadable(self, path):
        """
        This method returns ``True`` when the file or directory addressed by *path* is readable.
        If it is directory, the read and execute flag is checked.

        Args:
            path: A string, path-like object or a :class:`~musicdb.lib.filesystem.Filesystem` object.

        Returns:
            ``True`` if the file or directory is readable, otherwise ``False``

        Example:

            .. code-block:: python

                ac = AccessPermissions()
                ac.IsReadable("/etc/passwd")        # False
                ac.IsReadable(Path("~"))            # True
                musicdir = Filesystem("/var/music")
                ac.IsReadable(musicdir)             # True

        """
        if type(path) == Filesystem:
            isdir = True
            mode  = path.CheckAccessPermissions()
        else:
            isdir = self.fs.IsDirectory(path)
            mode  = self.fs.CheckAccessPermissions(path)

        if isdir and mode[0] == "r" and mode[2] == "x":
            return True
        elif mode[0] == "r":
            return True
        return False

    def IsWritable(self, path):
        """
        This method returns ``True`` when the file or directory addressed by *path* is writable.
        If it is directory, the read and execute flag is checked.
        This method implies that the file or directory is not only writable but also readable.

        Args:
            path: A string, path-like object or a :class:`~musicdb.lib.filesystem.Filesystem` object.

        Returns:
            ``True`` if the file or directory is writable, otherwise ``False``

        Example:

            .. code-block:: python

                ac = AccessPermissions()
                ac.IsWritable("/etc/passwd")        # False
                ac.IsWritable(Path("~"))            # True
                musicdir = Filesystem("/var/music")
                ac.IsWritable(musicdir)             # True

        """
        if type(path) == Filesystem:
            isdir = True
            mode  = path.CheckAccessPermissions()
        else:
            isdir = self.fs.IsDirectory(path)
            mode  = self.fs.CheckAccessPermissions(path)

        if isdir and mode == "rwx":
            return True
        elif mode[0] == "r" and mode[1] == "w":
            return True
        return False



    def EvaluateTasksDirectory(self):
        """
        This method checks if the tasks directory has the correct permissions.

        Returns:
            ``True`` when the MusicDB has read and write access to that directory.
        """
        tasksdir    = Filesystem(self.cfg.directories.tasks)
        readaccess  = self.IsReadable(tasksdir)
        writeaccess = self.IsWritable(tasksdir)

        if not (readaccess or writeaccess):
            logging.error("MusicDB requires read and write access to the tasks directory at %s! \033[1;30m(Task Management will not work properly without R/W access)", tasksdir.GetRoot());
            return False
        return True


    def EvaluateUploadsDirectory(self):
        """
        This method checks if the uploads directory has the correct permissions.

        Returns:
            ``True`` when the MusicDB has read and write access to that directory.
        """
        uploadsdir  = Filesystem(self.cfg.directories.uploads)
        readaccess  = self.IsReadable(uploadsdir)
        writeaccess = self.IsWritable(uploadsdir)

        if not (readaccess or writeaccess):
            logging.warning("MusicDB requires read and write access to the uploads directory at %s! \033[1;30m(Uploading files is not possible)", uploadsdir.GetRoot());
            return False
        return True


    def EvaluateStateDirectory(self):
        """
        This method checks if the state directory has the correct permissions.

        Returns:
            ``True`` when the MusicDB has read and write access to that directory.
        """
        statedir    = Filesystem(self.cfg.directories.state)
        readaccess  = self.IsReadable(statedir)
        writeaccess = self.IsWritable(statedir)

        if not (readaccess or writeaccess):
            logging.critical("MusicDB requires read and write access to the state directory at %s! \033[1;30m(MusicDB does not function properly without R/W access to the state directory)", statedir.GetRoot());
            return False
        return True


    def EvaluateArtworkDirectory(self):
        """
        This method checks if the artwork directory has the correct permissions.

        Returns:
            ``True`` when the MusicDB has read and write access to that directory.
        """
        artworkdir  = Filesystem(self.cfg.directories.artwork)
        readaccess  = self.IsReadable(self.artworkdir)
        writeaccess = self.IsWritable(self.artworkdir)

        if not (readaccess or writeaccess):
            logging.critical("MusicDB requires read and write access to the artwork directory at %s! \033[1;30m(MusicDB does not function properly without R/W access to the artwork directory)", artworkdir.GetRoot());
            return False
        return True



    # TODO: This function is from mdbapi.musicdirectory. It is better placed in this class.
    #def FixAttributes(self, path: Union[str, Path]):
    #    """
    #    This method changes the access permissions and ownership of a file or directory.
    #    Only the addressed files or directory's permissions gets changed, not their parents.

    #        * File permissions: ``rw-rw-r--``
    #        * Directory permissions: ``rwxrwxr-x``

    #    To update the access permissions the method :meth:`musicdb.lib.filesystem.Filesystem.SetAttributes` is used.

    #    Args:
    #        path (str/Path): Path to an artist, album or song, relative to the music directory

    #    Returns:
    #        ``True`` on success, otherwise ``False``

    #    Raises:
    #        ValueError: if path is neither a file nor a directory.
    #    """
    #    if self.IsDirectory(path):
    #        permissions = "rwxrwxr-x"
    #    elif self.IsFile(path):
    #        permissions = "rw-rw-r--"
    #    else:
    #        raise ValueError("Path \""+str(path)+"\" is not a directory or file")

    #    success = self.SetAccessPermissions(path, permissions)
    #    return success



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

