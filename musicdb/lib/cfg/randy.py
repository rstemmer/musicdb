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
"""
This module takes care that the configuration of the random song selection algorithm (Randy) will persist over several sessions.
This is *not done automatically* by the :class:`~RandyConfiguration` class.
Each read or write process to the files that hold the state will be triggered by the classes who manage the related information.

The configuration is stored in a files ``randy.ini`` in a sub-directory ``config`` inside the MusicDB data directory.
More details can be found in :doc:`/basics/data`.

Possible configurations
-----------------------

NoDisabled (boolean):
   If ``true`` no disabled songs will be chosen

NoHated (boolean):
   If ``true`` no hated songs will be chosen

NoHidden (boolean):
   If ``True`` no hidden albums will be considered

Nobadfile (boolean):
   If ``True`` no songs marked as "bad file" will be selected

NoLiveMusic (boolean):
   If ``True`` no songs marked as "live recording" will be selected

MinSongLength (number ∈ ℕ):
   Determines the minimum length of a song in seconds to be in the set of possible songs

MaxSongLength (number ∈ ℕ):
   Determines the maximum length of a song in seconds to be in the set of possible songs

SongListLength (number ∈ ℕ):
   Blacklist length for songs (``0`` to disable the blacklist)

AlbumListLength (number ∈ ℕ):
   Blacklist length for albums (``0`` to disable the blacklist)

ArtistListLength (number ∈ ℕ):
   Blacklist length for artists (``0`` to disable the blacklist)

VideoListLength (number ∈ ℕ):
   Blacklist length for videos (``0`` to disable the blacklist)

MaxAge (time in hours as integer):
   The highest age an entry in one of the three blacklist can have until it gets automatically removed.

MaxTries (number ∈ ℕ):
   Maximum amount of tries to find a valid random songs.
   This prevents spending infinite amount of time getting a song even if the data base does not provide enough songs.
"""

from musicdb.lib.cfg.config import Config
import logging

class SECTION:
    pass

class RandyConfiguration(Config):
    """
    This class holds the Randy configuration.

    Args:
        configpath: Absolute path to the Randy configuration file.
    """

    def __init__(self, configpath):

        Config.__init__(self, configpath)
        self.meta       = SECTION()
        self.constraints= SECTION()
        self.blacklists = SECTION()
        self.limits     = SECTION()

        self.meta.version = self.Get(int, "meta", "version", 0) # 0 = inf
        if self.meta.version < 1:
            logging.info("Updating %s to version 1", configpath)
            self.Set("meta", "version", 1)
            self.Set("Constraints", "NoDisabled",       True)
            self.Set("Constraints", "NoHated",          True)
            self.Set("Constraints", "NoBadFile",        True)
            self.Set("Constraints", "NoLiveMusic",      False)
            self.Set("Constraints", "MinSongLength",    120)
            self.Set("Constraints", "MaxSongLength",    600)
            self.Set("BlackLists",  "SongListLength",     5)
            self.Set("BlackLists",  "AlbumListLength",    2)
            self.Set("BlackLists",  "ArtistListLength",   1)
            self.Set("BlackLists",  "VideoListLength",    3)
            self.Set("BlackLists",  "MaxAge",            24)
            self.Set("Limits",      "MaxTries",          10)

        self.Reload()



    def Reload(self):
        """
        This method reloads the current randy configuration from the state directory

        Returns:
            *Nothing*
        """
        self.meta.version = self.Get(int, "meta", "version", 0)

        self.constraints.nodisabled    = self.Get(bool, "Constraints",  "NoDisabled",       True)
        self.constraints.nohated       = self.Get(bool, "Constraints",  "NoHated",          True)
        self.constraints.nobadfile     = self.Get(bool, "Constraints",  "NoBadFile",        True)
        self.constraints.nolivemusic   = self.Get(bool, "Constraints",  "NoLiveMusic",      True)
        self.constraints.minsonglength = self.Get(int,  "Constraints",  "MinSongLength",    120)
        self.constraints.maxsonglength = self.Get(int,  "Constraints",  "MaxSongLength",    600)

        self.blacklists.songlistlength   = self.Get(int,  "BlackLists",  "SongListLength",     5)
        self.blacklists.albumlistlength  = self.Get(int,  "BlackLists",  "AlbumListLength",    2)
        self.blacklists.artistlistlength = self.Get(int,  "BlackLists",  "ArtistListLength",   1)
        self.blacklists.videolistlength  = self.Get(int,  "BlackLists",  "VideoListLength",    3)
        self.blacklists.maxage           = self.Get(int,  "BlackLists",  "MaxAge",            24)

        self.limits.maxtries = self.Get(int,  "Limits",      "MaxTries",          10)




    def LoadConfig(self):
        """
        This method loads the current randy configuration and returns them in a dictionary.

        This method is mainly available to provide the Randy configuration to the WebUI.

        Returns:
            dict with the whole WebUI configuration
        """
        self.Reload()

        cfg = {}
        cfg["meta"] = {}
        cfg["meta"]["version"] = self.meta.version

        cfg["Constraints"] = {}
        cfg["Constraints"]["NoDisabled"]    = self.constraints.nodisabled
        cfg["Constraints"]["NoHated"]       = self.constraints.nohated
        cfg["Constraints"]["NoBadFile"]     = self.constraints.nobadfile
        cfg["Constraints"]["NoLiveMusic"]   = self.constraints.nolivemusic
        cfg["Constraints"]["MinSongLength"] = self.constraints.minsonglength
        cfg["Constraints"]["MaxSongLength"] = self.constraints.maxsonglength

        cfg["BlackLists"] = {}
        cfg["BlackLists"]["SongListLength"]     = self.blacklists.songlistlength
        cfg["BlackLists"]["AlbumListLength"]    = self.blacklists.albumlistlength
        cfg["BlackLists"]["ArtistListLength"]   = self.blacklists.artistlistlength
        cfg["BlackLists"]["VideoListLength"]    = self.blacklists.videolistlength
        cfg["BlackLists"]["MaxAge"]             = self.blacklists.maxage

        cfg["Limits"] = {}
        cfg["Limits"]["MaxTries"] = self.limits.maxtries

        return cfg
    

    def SaveConfig(self, cfg):
        """
        This method saves the given Randy configuration.
        It is important that the whole configuration is included in *cfg*.

        This method is mainly provided as interface to the WebUI configuration View.

        Args:
            cfg (dict): Dictionary with the whole configuration

        Returns:
            *Nothing*
        """
        self.Set("meta",        "version",          cfg["meta"]["version"])
        self.Set("Constraints", "NoDisabled",       cfg["Constraints"]["NoDisabled"])
        self.Set("Constraints", "NoHated",          cfg["Constraints"]["NoHated"])
        self.Set("Constraints", "NoBadFile",        cfg["Constraints"]["NoBadFile"])
        self.Set("Constraints", "NoLiveMusic",      cfg["Constraints"]["NoLiveMusic"])
        self.Set("Constraints", "MinSongLength",    cfg["Constraints"]["MinSongLength"])
        self.Set("Constraints", "MaxSongLength",    cfg["Constraints"]["MaxSongLength"])
        self.Set("BlackLists",  "SongListLength",   cfg["BlackLists"]["SongListLength"])
        self.Set("BlackLists",  "AlbumListLength",  cfg["BlackLists"]["AlbumListLength"])
        self.Set("BlackLists",  "ArtistListLength", cfg["BlackLists"]["ArtistListLength"])
        self.Set("BlackLists",  "VideoListLength",  cfg["BlackLists"]["VideoListLength"])
        self.Set("BlackLists",  "MaxAge",           cfg["BlackLists"]["MaxAge"])
        self.Set("Limits",      "MaxTries",         cfg["Limits"]["MaxTries"])

        self.Reload()
        return

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

