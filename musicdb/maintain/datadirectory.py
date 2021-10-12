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
This module maintains the MusicDB Data Directory.
It checks the existence of files and sub-directories and creates them if they do not exists.
"""

import logging
import stat
from datetime           import datetime
from musicdb.lib.filesystem     import Filesystem


class DataDirectoryMaintainer(object):
    """
    This class provides a basic set of tools to check and create required files for MusicDB.
    The certificate files are checked independently by the :mod:`musicdb.maintain.sslcert` module.
    The database files are checked by the :mod:`musicdb.maintain.musicdatabase` and :mod:`musicdb.maintain.trackeratabase` modules.

    Args:
        config (MusicDBConfig): Configuration object for MusicDB

    """
    def __init__(self, config):
        self.config     = config
        self.filesystem = Filesystem()
        # TODO: Use user name and group from config
        # TODO: Make paths configurable

        # Collect all sub-directories
        self.subdirpaths = []
        self.AddDirectory(self.config.server.statedir, "musicdb", "musicdb", 0o755)
        self.AddDirectory("/var/lib/musicdb/webdata",  "musicdb", "musicdb", 0o755) # TODO: -> Configuration file
        self.AddDirectory(self.config.artwork.path,    "musicdb", "musicdb", 0o775) # TODO include sub directories
        self.AddDirectory(self.config.uploads.path,    "musicdb", "musicdb", 0o750)

        # Collect all files (expected directory, initial file source)
        self.filepaths = []
        self.AddFile(self.config.server.webuiconfig,            "musicdb", "musicdb", 0o664, "/usr/share/musicdb/webui.ini")
        self.AddFile(self.config.artwork.path + "/default.jpg", "musicdb", "musicdb", 0o644, "/usr/share/musicdb/default.jpg")
        self.AddFile("/var/lib/musicdb/webdata/config.js",      "musicdb", "musicdb", 0o664, "/usr/share/musicdb/config.js")


    def AddDirectory(self, expectedpath, user, group, mode):
        entry = {}
        entry["path"]   = expectedpath
        entry["user"]   = user
        entry["group"]  = group
        entry["mode"]   = mode
        self.subdirpaths.append(entry)
        return

    def AddFile(self, expectedpath, user, group, mode, sourcepath):
        entry = {}
        entry["path"]   = expectedpath
        entry["user"]   = user
        entry["group"]  = group
        entry["mode"]   = mode
        entry["source"] = sourcepath
        self.filepaths.append(entry)
        return



    def Check(self):
        """
        This method just checks if everything is correct including existence, ownership and access mode.
        If not, ``False`` gets returned.

        Returns:
            ``True`` if everything is correct. Otherwise ``False``.
        """
        success = True
        for subdir in self.subdirpaths:
            if not self.filesystem.IsDirectory(subdir["path"]):
                logging.warning("Sub-directory \"%s\" missing. \033[1;30m(Directory will be created)", subdir["path"])
                success = False
                continue

            if not self.CheckPath(subdir["path"], subdir["user"], subdir["group"], subdir["mode"]):
                success = False


        for file in self.filepaths:
            if not self.filesystem.IsFile(file["path"]):
                logging.warning("File \"%s\" missing. \033[1;30m(File will be created from %s)", file["path"], file["source"])
                success = False
                continue

            if not self.CheckPath(file["path"], file["user"], file["group"], file["mode"]):
                success = False
        return success



    def Validate(self):
        """
        This method checks if all required directories and files exist.
        If not they will be created.
        If they exists, their user, group and mode settings will be checked and adjusted.

        Returns:
            *Nothing*
        """
        for subdir in self.subdirpaths:
            if not self.filesystem.IsDirectory(subdir["path"]):
                logging.warning("Sub-directory \"%s\" missing. \033[1;30m(Directory will be created)", subdir["path"])
                self.filesystem.CreateSubdirectory(subdir["path"])

            if not self.CheckPath(subdir["path"], subdir["user"], subdir["group"], subdir["mode"]):
                logging.info("Updating attributes of %s", subdir["path"])
                self.filesystem.SetAttributes(subdir["path"], subdir["user"], subdir["group"], subdir["mode"])


        for file in self.filepaths:
            if not self.filesystem.IsFile(file["path"]):
                logging.warning("File \"%s\" missing. \033[1;30m(File will be created from %s)", file["path"], file["source"])
                self.filesystem.CopyFile(file["source"], file["path"])

            if not self.CheckPath(file["path"], file["user"], file["group"], file["mode"]):
                logging.info("Updating attributes of %s", file["path"])
                self.filesystem.SetAttributes(file["path"], file["user"], file["group"], file["mode"])



    def CheckPath(self, path, expuser, expgroup, expmode):
        user, group = self.filesystem.GetOwner(path)
        mode        = self.filesystem.GetMode(path)
        success     = True

        if user != expuser:
            logging.warning("User of %s is %s but should be %s!", path, user, expuser)
            success = False
        if group != expgroup:
            logging.warning("Group of %s is %s but should be %s!", path, group, expgroup)
            success = False
        if mode != expmode:
            logging.warning("Access mode of %s is %s but should be %s!", path, oct(mode), oct(expmode))
            success = False
        return success



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

