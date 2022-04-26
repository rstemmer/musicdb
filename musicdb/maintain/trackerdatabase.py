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
This module can be used to check and maintain the MusicDB tracker database ``tracker.db``
"""

import logging
from musicdb.maintain.database  import DatabaseTools, DatabaseMaintainer


class TrackerDatabaseMaintainer(DatabaseMaintainer):
    """
    This class provides a basic set of tools to check and upgrade the MusicDB tracker databases.
    This class is derived from :class:`musicdb.maintain.database.DatabaseMaintainer`.

    Args:
        databasepath: Absolute path to the main database (tracker.db) to check/upgrade
        version (int): Expected version of the database
    """
    def __init__(self, databasepath, version):
        DatabaseMaintainer.__init__(self, databasepath, version)
        self.expuser     = "musicdb"
        self.expgroup    = "musicdb"
        self.expmode     = "rw-rw-r--"
        return



    def Validate(self):
        """
        This method checks if the database exists and checks its file attributes.
        If the database does not exist, a new database form ``/usr/share/muiscdb/sql/tracker.db.sql`` will be created.
        Invalid file attributes will be fixed.

        Returns:
            *Nothing*
        """
        self.CreateIfNotExisting("/usr/share/musicdb/sql/tracker.db.sql")
        self.ValidateAttributes(self.expuser, self.expgroup, self.expmode)
        return



    def Upgrade(self):
        """
        This method successively upgrades the database to the latest version number.
        Before the update process starts, a backup will be created

        Returns:
            *Nothing*
        """
        dbtool = self.GetDatabaseTool()
        dbtool.Backup()

        actualversion = dbtool.GetActualVersion()
        if actualversion < 2:
            logging.error("Database version too old!")
            return
        if actualversion < 3:
            self.UpgradeTo3()
        if actualversion < 4:
            self.UpgradeTo4()
        return



    def UpgradeTo3(self):
        """
        Creates a new table *videorelations* uses since MusicDB 7.0.0
        """
        dbtool = self.GetDatabaseTool()
        dbtool.CreateTable("videorelations", "id")
        dbtool.AddColumn("videorelations", "videoida", "INTEGER");
        dbtool.AddColumn("videorelations", "videoidb", "INTEGER");
        dbtool.AddColumn("videorelations", "weight  ", "INTEGER", "1");

        dbtool.SetDatabaseVersion(3)
        return

    def UpgradeTo4(self):
        """
        Creates a new tables *playedsongs* and *playedvideos* uses since MusicDB 8.1.0
        """
        dbtool = self.GetDatabaseTool()
        dbtool.CreateTable("playedsongs", "id")
        dbtool.AddColumn("playedsongs", "songid",    "INTEGER");
        dbtool.AddColumn("playedsongs", "timestamp", "INTEGER", "0");
        dbtool.AddColumn("playedsongs", "random",    "INTEGER", "0");

        dbtool.CreateTable("playedvideos", "id")
        dbtool.AddColumn("playedvideos", "videoid",    "INTEGER");
        dbtool.AddColumn("playedvideos", "timestamp", "INTEGER", "0");
        dbtool.AddColumn("playedvideos", "random",    "INTEGER", "0");

        dbtool.SetDatabaseVersion(4)
        return


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

