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

The state is stored in a files ``randy.ini`` in a sub-directory ``state`` inside the MusicDB data directory.
More details can be found in :doc:`/basics/data`.
"""

from musicdb.lib.cfg.config import Config
import logging

class SECTION:
    pass

class RandyConfiguration(Config):
    """
    This class holds the Randy configuration.

    TODO: Explain each setting - for example that MaxAge must be given in hours

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



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

