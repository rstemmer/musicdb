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
from musicdb.maintain.database  import DatabaseTools, DatabaseMaintainer
from musicdb.lib.filesystem     import Filesystem


class MusicDatabaseMaintainer(DatabaseMaintainer):
    """
    This class provides a basic set of tools to check and upgrade the MusicDB main databases.
    This class is derived from :class:`musicdb.maintain.database.DatabaseMaintainer`.

    Args:
        databasepath: Absolute path to the main database (music.db) to check/upgrade
        version (int): Expected version of the database
    """
    def __init__(self, databasepath, version):
        DatabaseMaintainer.__init__(self, databasepath, version)
        self.expuser     = "musicdb"
        self.expgroup    = "musicdb"
        self.expmode     = 0o664



    def Validate(self):
        """
        This method checks if the database exists and checks its file attributes.
        If the database does not exist, a new database form ``/usr/share/muiscdb/sql/music.db.sql`` will be created.
        Invalid file attributes will be fixed.

        Returns:
            *Nothing*
        """
        self.CreateIfNotExisting("/usr/share/musicdb/sql/music.db.sql")
        self.ValidateAttributes(self.expuser, self.expgroup, self.expmode)
        return



    def Upgrade(self):
        """
        This method successively upgrades the database to the latest version number.
        Before the update process starts, a backup will be created.

        Returns:
            *Nothing*
        """
        dbtool = self.GetDatabaseTool()
        dbtool.Backup()

        actualversion = dbtool.GetActualVersion()
        if actualversion == 4:
            dbtool.UpgradeTo5()
        return



    def UpgradeTo5(self, dbtools):
        """
        Creates the *videos* and *videotags* table uses since MusicDB 7.0.0.
        It adds a *hidden* column to *albums*.
        Furthermore a *liverecording* and *badaudio* column gets added to the *songs* table.
        """
        dbtool = self.GetDatabaseTool()
        dbtool.AddColumn("songs", "liverecording", "INTEGER", "0");
        dbtool.AddColumn("songs", "badaudio     ", "INTEGER", "0");

        dbtool.AddColumn("albums", "hidden       ", "INTEGER", "0");

        dbtool.CreateTable("videos", "videoid")
        dbtool.AddColumn("videos", "songid       ", "INTEGER", "NULL");
        dbtool.AddColumn("videos", "albumid      ", "INTEGER", "NULL");
        dbtool.AddColumn("videos", "artistid     ", "INTEGER");
        dbtool.AddColumn("videos", "name         ", "TEXT   ");
        dbtool.AddColumn("videos", "path         ", "TEXT   ");
        dbtool.AddColumn("videos", "disabled     ", "INTEGER", "0");
        dbtool.AddColumn("videos", "playtime     ", "INTEGER");
        dbtool.AddColumn("videos", "origin       ", "TEXT   ");
        dbtool.AddColumn("videos", "release      ", "INTEGER");
        dbtool.AddColumn("videos", "added        ", "INTEGER");
        dbtool.AddColumn("videos", "codec        ", "TEXT   ");
        dbtool.AddColumn("videos", "xresolution  ", "INTEGER");
        dbtool.AddColumn("videos", "yresolution  ", "INTEGER");
        dbtool.AddColumn("videos", "thumbnailpath", "TEXT   ", "\"default.jpg\"");
        dbtool.AddColumn("videos", "likes        ", "INTEGER", "0");
        dbtool.AddColumn("videos", "dislikes     ", "INTEGER", "0");
        dbtool.AddColumn("videos", "favorite     ", "INTEGER", "0");
        dbtool.AddColumn("videos", "livevideo    ", "INTEGER", "0");
        dbtool.AddColumn("videos", "badaudio     ", "INTEGER", "0");
        dbtool.AddColumn("videos", "checksum     ", "TEXT   ", "\"\"");
        dbtool.AddColumn("videos", "lastplayed   ", "INTEGER", "0");

        dbtool.CreateTable("videotags", "entryid")
        dbtool.AddColumn("videotags", "videoid   ", "INTEGER");
        dbtool.AddColumn("videotags", "tagid     ", "INTEGER");
        dbtool.AddColumn("videotags", "confidence", "REAL   ", "0.0");
        dbtool.AddColumn("videotags", "approval  ", "INTEGER", "1  ");

        dbtool.SetDatabaseVersion(5)
        return


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

