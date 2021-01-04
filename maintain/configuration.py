# MusicDB,  a music manager with web-bases UI that focus on music.
# Copyright (C) 2017-2020  Ralf Stemmer <ralf.stemmer@gmx.net>
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
This module provides a class to maintain the MusicDB configuration (musicdb.ini)
"""

import logging
import configparser
from datetime       import datetime
from lib.filesystem import Filesystem


class ConfigurationMaintainer(object):
    """
    This class provides a basic set of tools to check and upgrade the MusicDB configuration.

    Args:
        configpath (str): Absolute path to the configuration to check/upgrade
        version (int): Expected version of the database

    Raises:
        TypeError: When *version* is not an integer
    """
    def __init__(self, configpath, version):
        if type(version) != int:
            raise TypeError("Version number must be of type integer")

        self.expectedversion = version
        self.configpath      = configpath
        self.config = configparser.ConfigParser()
        self.config.read(self.configpath)



    def GetExpectedVersion(self):
        return self.expectedversion



    def GetActualVersion(self):
        """
        This method returns the version number stored in the configuration file.

        The version number is expected to be in the ``meta`` section behind the key ``version``.

        Returns:
            Version number as Integer
        """
        version = self.config.get("meta", "version", fallback="1")
        version = int(version)
        return version



    def SaveConfiguration(self, version):
        """
        This method updates the version number of the in configuration file.
        The version number is expected to be in the ``meta`` section behind the key ``version``.
        After updating the version number all changes are saved in the file.

        Args:
            version (int): Version number

        Raises:
            TypeError: When *version* is not an integer
            ValueError: When *version* is less than the actual database version

        Returns:
            *Nothing*
        """
        if type(version) != int:
            raise TypeError("Version must be of type integer")
        if version < self.GetActualVersion():
            raise ValueError("Version must not be less than the actual database version")

        self.config.set("meta", "version", str(version))
        with open(self.configpath, "w") as configfile:
            self.config.write(configfile)
            
        return



    def CheckVersion(self):
        """
        Checks if the version of the database is the latest one

        Returns:
            ``True`` if the database is valid, ``False`` if not.
        """
        actualversion = self.GetActualVersion()
        return self.expectedversion == actualversion



    def Upgrade(self):
        """
        This method successively upgrades the configuration to the latest version number.
        Before the update process starts, a backup will be created

        Returns:
            *Nothing*
        """
        self.Backup()

        actualversion = self.GetActualVersion()
        if actualversion == 4:
            self.UpgradeTo5()
        return


    def UpgradeTo5(self):
        """
        Creates the *videoframes* section uses since MusicDB 7.0.0.
        The videoframs directory will have the same root as the artwork directory.
        """
        artworkpath = self.config.get("artwork", "path")
        datapath    = "/".join(artworkpath.split("/")[:-1])
        videoframespath = datapath + "/videoframes"
        temppath    = datapath + "/upload"
        webuicfgpath= datapath + "/webui.ini"

        self.CreateSection("videoframes")
        self.AddValue("videoframes", "path",          videoframespath);
        self.AddValue("videoframes", "frames",        "5");
        self.AddValue("videoframes", "scales",        "150x83");
        self.AddValue("videoframes", "previewlength", "3");

        self.CreateSection("uploads")
        self.AddValue("uploads", "allow",  "True");
        self.AddValue("uploads", "path",   temppath);

        self.AddValue("debug", "disableicecast", "0");
        self.AddValue("debug", "disablevideos",  "1");

        self.AddValue("server", "webuiconfig",  webuicfgpath);

        self.SaveConfiguration(5)
        return



    def CreateSection(self, sectionname):
        """
        Create a new and section.

        Args:
            sectionname (str): Name of the new section

        Returns:
            *Nothing*

        Raises:
            TypeError: When the *sectionname* argument is not of type string
            ValueError: When *sectionname* is an empty string
        """
        if type(sectionname) != str:
            raise TypeError("Section name must be of type string")
        if sectionname == "":
            raise ValueError("Section name must not be an empty string")

        self.config.add_section(sectionname)
        return



    def AddValue(self, sectionname, keyname, value):
        """
        Add a new value *keyname* to a section *sectionname* with the data *value*.

        Args:
            sectionname (str): Name of the section to extend
            keyname (str): Name of the key
            value (str): Value to store

        Returns:
            *Nothing*

        Raises:
            TypeError: When one of the parameters is not of type string (except for *default*)
            ValueError: When one of the parameters is an empty string (except for *default*)
        """
        if type(sectionname) != str or type(keyname) != str:
            raise TypeError("Parameters must be of type string")
        if sectionname == "" or keyname == "":
            raise ValueError("Parameters must not be an empty string")

        self.config.set(sectionname, keyname, value)
        return;


    def Backup(self):
        """
        Creates a backup of the configuration file.
        The path of the backup will be the same as the source file.
        It gets the following extension: ``.YYYY-MM-DDTHH:MM.bak``

        Returns:
            *Nothing*
        """
        backuppath  = self.configpath
        backuppath += "."
        backuppath += datetime.now().isoformat(timespec='minutes')
        backuppath += ".bak"

        fs = Filesystem()
        try:
            fs.CopyFile(self.configpath, backuppath)
        except Exception as e:
            logging.warning("creating backup of configuration failed with error %s. Writing backup to /tmp/configbackup.ini", str(e))
            fs.CopyFile(self.configpath, "/tmp/configbackup.ini")
        return

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

