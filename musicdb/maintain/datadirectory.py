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
        self.user       = self.config.musicdb.username
        self.group      = self.config.musicdb.groupname

        # Collect all sub-directories
        self.subdirpaths = []
        self.AddDirectory(self.config.directories.state,   self.user, self.group, 0o755)
        self.AddDirectory(self.config.directories.webdata, self.user, self.group, 0o755)
        self.AddDirectory(self.config.directories.artwork, self.user, self.group, 0o775) # TODO include sub directories
        self.AddDirectory(self.config.directories.uploads, self.user, self.group, 0o750)
        self.AddDirectory(self.config.directories.tasks,   self.user, self.group, 0o750)

        # Collect all files (expected directory, initial file source)
        sourcedir = self.config.directories.share
        self.filepaths = []
        self.AddFile(self.config.files.webuiconfig,       self.user, self.group, 0o664, sourcedir + "/webui.ini")
        self.AddFile(self.config.files.defaultalbumcover, self.user, self.group, 0o644, sourcedir + "/default.jpg")
        self.AddFile(self.config.files.webuijsconfig,     self.user, self.group, 0o664, sourcedir + "/config.js")


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



    def InsertWSAPIKey(self, wsapikey: str, configjs: str) -> bool:
        """
        This method copies the WebSocket API Key given by the parameter ``wsapikey``
        into a new generated WebUI ``config.js`` file addressed by the ``configjs`` parameter.
        The API key should be read from ``/etc/musicdb.ini``: ``[websocket]->apikey``.

        It is expected that the addressed file in ``configjs`` exists.
        If not a ``FileNotFound`` exception will raise.

        The WebUI JavaScript configuration must already exist.
        If that file already has a key, it will not be replaced.
        If no key exists yet (a dummy key ``WSAPIKEY`` is expected in place) the key will be set.

        Args:
            wsapikey (str): The API key to set
            configjs (str): Path to the config.js file of the WebUI client that shall use the API Key

        Returns:
            *Nothing*
        """
        # Read file
        with open(configjs) as file:
            lines = file.read()

        # Process file: Replace WSAPIKEY dummy by actual key
        lines = lines.splitlines()
        lines = [line.replace("WSAPIKEY", wsapikey) for line in lines]
        lines = "\n".join(lines)

        # Write file
        with open(configjs, "w") as file:
            file.write(lines)
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

        # Make sure the WebSocket API Key is set in the config.js file
        self.InsertWSAPIKey(self.config.websocket.apikey, self.config.files.webuijsconfig)
        return



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

