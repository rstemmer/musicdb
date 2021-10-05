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
This module can be used to check and maintain the MusicDB main database ``music.db``
"""

import logging
from musicdb.maintain.database  import DatabaseTools


class MusicDatabaseMaintainer(DatabaseTools):
    """
    This class provides a basic set of tools to check and upgrade the MusicDB main databases.

    Args:
        databasepath: Absolute path to the main database (music.db) to check/upgrade
        version (int): Expected version of the database
    """
    def __init__(self, databasepath, version):
        DatabaseTools.__init__(self, databasepath, version)
        return



    def Upgrade(self):
        """
        This method successively upgrades the database to the latest version number.
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
        Creates the *videos* and *videotags* table uses since MusicDB 7.0.0.
        It adds a *hidden* column to *albums*.
        Furthermore a *liverecording* and *badaudio* column gets added to the *songs* table.
        """
        self.AddColumn("songs", "liverecording", "INTEGER", "0");
        self.AddColumn("songs", "badaudio     ", "INTEGER", "0");

        self.AddColumn("albums", "hidden       ", "INTEGER", "0");

        self.CreateTable("videos", "videoid")
        self.AddColumn("videos", "songid       ", "INTEGER", "NULL");
        self.AddColumn("videos", "albumid      ", "INTEGER", "NULL");
        self.AddColumn("videos", "artistid     ", "INTEGER");
        self.AddColumn("videos", "name         ", "TEXT   ");
        self.AddColumn("videos", "path         ", "TEXT   ");
        self.AddColumn("videos", "disabled     ", "INTEGER", "0");
        self.AddColumn("videos", "playtime     ", "INTEGER");
        self.AddColumn("videos", "origin       ", "TEXT   ");
        self.AddColumn("videos", "release      ", "INTEGER");
        self.AddColumn("videos", "added        ", "INTEGER");
        self.AddColumn("videos", "codec        ", "TEXT   ");
        self.AddColumn("videos", "xresolution  ", "INTEGER");
        self.AddColumn("videos", "yresolution  ", "INTEGER");
        self.AddColumn("videos", "thumbnailpath", "TEXT   ", "\"default.jpg\"");
        self.AddColumn("videos", "likes        ", "INTEGER", "0");
        self.AddColumn("videos", "dislikes     ", "INTEGER", "0");
        self.AddColumn("videos", "favorite     ", "INTEGER", "0");
        self.AddColumn("videos", "livevideo    ", "INTEGER", "0");
        self.AddColumn("videos", "badaudio     ", "INTEGER", "0");
        self.AddColumn("videos", "checksum     ", "TEXT   ", "\"\"");
        self.AddColumn("videos", "lastplayed   ", "INTEGER", "0");

        self.CreateTable("videotags", "entryid")
        self.AddColumn("videotags", "videoid   ", "INTEGER");
        self.AddColumn("videotags", "tagid     ", "INTEGER");
        self.AddColumn("videotags", "confidence", "REAL   ", "0.0");
        self.AddColumn("videotags", "approval  ", "INTEGER", "1  ");

        self.SetDatabaseVersion(5)
        return


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

