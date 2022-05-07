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
This module provides a basic set of maintenance tools for checking and upgrading the databases
used by MusicDB.
"""

import logging
import sqlite3
from datetime           import datetime
from musicdb.lib.db.database    import Database
from musicdb.lib.filesystem     import Filesystem


class DatabaseMaintainer(object):
    """
    This class is a base class for maintaining MusicDB databases.

    Args:
        databasepath (str): Absolute path to the database to check/upgrade
        version (int): Expected version of the database

    Raises:
        TypeError: When *version* is not an integer
    """
    def __init__(self, databasepath, version):
        self.databasepath = databasepath
        self.version      = version
        self.filesystem   = Filesystem()
        self.databasetool = None



    def GetDatabaseTool(self):
        """
        This method returns an instance of the :class:`~DatabaseTools` class to access the database.
        If the database does not exists yet, ``None`` is returned.

        Returns:
            Instance of the :class:`~DatabaseTools` or ``None``
        """
        if not self.filesystem.IsFile(self.databasepath):
            return None

        if self.databasetool == None:
            self.databasetool = DatabaseTools(self.databasepath, self.version)

        return self.databasetool



    def CheckVersion(self) -> bool:
        """
        Checks if the version of the database is the latest one via :meth:`DatabaseTools.CheckVersion`

        Returns:
            ``True`` if the database is valid, ``False`` if not.
        """
        databasetool = self.GetDatabaseTool()
        if databasetool:
            return databasetool.CheckVersion()
        else:
            return False



    def CreateIfNotExisting(self, sqlscriptpath: str) -> bool:
        """
        If the database does not exist, a new database form,
        for example, ``/usr/share/muiscdb/sql/*.db.sql`` will be created.
        The full path must be given via ``sqlscriptpath`` parameter

        Args:
            sqlscriptpath (str): Path to a SQL script that can be executed by ``sqlite3``

        Returns:
            ``True`` on success, otherwise ``False``
        """
        if not self.filesystem.IsFile(self.databasepath):
            if not self.filesystem.IsFile(sqlscriptpath):
                logging.error("The database %s does not exist and cannot be created because the scheme %s does not exist as well!", self.databasepath, sqlscriptpath)
                return False

            logging.info("Creating %s from scheme %s …", self.databasepath, sqlscriptpath)
            with open(sqlscriptpath) as sqlfile:
                sqlcommand = sqlfile.read()

            connection = sqlite3.connect(self.databasepath)
            cursor = connection.cursor()
            cursor.executescript(sqlcommand)

        return True



    def ValidateAttributes(self, expuser: str, expgroup: str, expmode: str):
        """
        This method check if the database file has the correct ownership and access mode.
        If not, it will be set.

        Args:
            expuser (str): Expected UNIX user
            expgroup (str): Expected UNIX group
            expmode (str): Expected access mode (for example ``rw-rw-r--`` for files)

        Returns:
            *Nothing*
        """
        user, group = self.filesystem.GetOwner(self.databasepath)
        mode        = self.filesystem.GetAccessPermissions(self.databasepath)
        success     = True

        if user != expuser:
            logging.warning("User of %s is %s but should be %s! \033[1;30m(Will be updated)", self.databasepath, user, expuser)
            success = False
        if group != expgroup:
            logging.warning("Group of %s is %s but should be %s! \033[1;30m(Will be updated)", self.databasepath, group, expgroup)
            success = False
        if mode != expmode:
            logging.warning("Access mode of %s is %s but should be %s! \033[1;30m(Will be updated)", self.databasepath, mode, expmode)
            success = False

        if not success:
            self.filesystem.SetAccessPermissions(self.databasepath, expmode)
            self.filesystem.SetOwner(self.databasepath, expuser, expgroup)

        return




class DatabaseTools(Database):
    """
    This class provides a basic set of tools to check and upgrade the MusicDB databases.

    Args:
        databasepath (str): Absolute path to the database to check/upgrade
        version (int): Expected version of the database

    Raises:
        TypeError: When *version* is not an integer
    """
    def __init__(self, databasepath, version):
        Database.__init__(self, databasepath)

        if type(version) != int:
            raise TypeError("Version number must be of type integer")

        self.expectedversion = version
        self.databasepath    = databasepath



    def GetExpectedVersion(self):
        return self.expectedversion



    def GetActualVersion(self):
        """
        This method returns the version number stored in the database.
        If there is no version number, a KeyError exception will be raised.

        The version number is expected to be in the table ``mete`` behind the key ``version``.

        Returns:
            Version number as Integer

        Raises:
            KeyError: When there is no version number.
            ValueError: When the value behind the key ``version`` is not an integer
        """
        try:
            result = self.GetFromDatabase("SELECT value FROM meta WHERE key = 'version'")
        except Exception as e:
            logging.error("Unable to read version number from Database. Does the table \"meta\" exist with a key \"version\"?")
            raise KeyError("Unable to read version number from Database.")

        try:
            version = int(result[0][0])
        except Exception as e:
            logging.error("Invalid value behind key \"version\"");
            raise ValueError("Invalid value behind key \"version\"")

        return version



    def SetDatabaseVersion(self, version):
        """
        This method updates the version number of the database.
        The version number is expected to be in the table ``mete`` behind the key ``version``.

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

        sql = "UPDATE meta SET value = ? WHERE key = 'version'"
        self.Execute(sql, (version,))

        logging.info("Upgraded database %s to version %s", str(self.databasepath), str(version))
        return



    def CheckVersion(self):
        """
        Checks if the version of the database is the latest one

        Returns:
            ``True`` if the database is valid, ``False`` if not.
        """
        actualversion = self.GetActualVersion()
        return self.expectedversion == actualversion



    def CreateTable(self, tablename, firstcolumn=""):
        """
        Create a new and table.
        If *firstcolumn* is defined, the new table will be created with the name in *firstcolumn*
        as ``INTEGER PRIMARY KEY AUTOINCREMENT`` column.

        When the table exists, nothing happens.
        The table will be creates using the following statement:

        .. code-block:: sql

            CREATE TABLE IF NOT EXISTS tablename ();

        Args:
            tablename (str): Name of the new table
            firstcolumn (str): (optional) Name of the first column in the table

        Returns:
            *Nothing*

        Raises:
            TypeError: When the *tablename* argument is not of type string
            ValueError: When *tablename* is an empty string
        """
        if type(tablename) != str:
            raise TypeError("Table name must be of type string")
        if tablename == "":
            raise ValueError("Table name must not be an empty string")

        sql  = "CREATE TABLE IF NOT EXISTS " + tablename
        sql += "("
        if type(firstcolumn) == str and len(firstcolumn) > 0:
            sql += firstcolumn + " INTEGER PRIMARY KEY AUTOINCREMENT"
        sql += ");"

        self.Execute(sql)
        return



    def AddColumn(self, tablename, columnname, datatype, default=""):
        """
        Add a new column *columnname* to a table *tablename* with the data type *datatype*.
        If *default* is defined, a default value will be assigned to the column.

        This function executed the following statement:

        .. code-block:: sql

            ALTER TABLE tablename ADD COLUMN columnname datatype DEFAULT default;

        Example:

            .. code-block:: python

                database.AddColumn("testtable", "newcolumn", "TEXT", "\"\""

        Args:
            tablename (str): Name of the table to extend
            columnname (str): Name of the new column
            datatype (str): SQL Data type of the new column
            default (str): (optional) default initialization value

        Returns:
            *Nothing*

        Raises:
            TypeError: When one of the parameters is not of type string (except for *default*)
            ValueError: When one of the parameters is an empty string (except for *default*)
        """
        if type(tablename) != str or type(columnname) != str or type(datatype) != str:
            raise TypeError("Parameters must be of type string")
        if tablename == "" or columnname == "" or datatype == "":
            raise ValueError("Parameters must not be an empty string")

        sql  = "ALTER TABLE " + tablename
        sql += " Add COLUMN " + columnname
        sql += " " + datatype
        if type(default) == str and len(default) > 0:
            sql += " DEFAULT " + default
        sql += ";"

        self.Execute(sql)
        return;


    def Backup(self):
        """
        Creates a backup of the database file.
        The path of the backup will be the same as the source file.
        It gets the following extension: ``.YYYY-MM-DDTHH:MM.bak``

        Returns:
            *Nothing*
        """
        backuppath  = self.databasepath
        backuppath += "."
        backuppath += datetime.now().isoformat(timespec='minutes')
        backuppath += ".bak"

        fs = Filesystem()
        fs.CopyFile(self.databasepath, backuppath)
        return

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

