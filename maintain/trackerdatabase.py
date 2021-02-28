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
This module can be used to check and maintain the MusicDB tracker database ``tracker.db``
"""

import logging
from maintain.database  import DatabaseTools


class TrackerDatabaseMaintainer(DatabaseTools):
    """
    This class provides a basic set of tools to check and upgrade the MusicDB tracker databases.

    Args:
        databasepath: Absolute path to the main database (tracker.db) to check/upgrade
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
        if actualversion == 2:
            self.UpgradeTo3()
        return



    def UpgradeTo3(self):
        """
        Creates a new table *videorelations* uses since MusicDB 7.0.0
        """
        self.CreateTable("videorelations", "id")
        self.AddColumn("videorelations", "videoida", "INTEGER");
        self.AddColumn("videorelations", "videoidb", "INTEGER");
        self.AddColumn("videorelations", "weight  ", "INTEGER", "1");

        self.SetDatabaseVersion(3)
        return


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

