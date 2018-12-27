# MusicDB,  a music manager with web-bases UI that focus on music.
# Copyright (C) 2017  Ralf Stemmer <ralf.stemmer@gmx.net>
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
"""

import argparse
import configparser
import os
import base64
from lib.modapi         import MDBModule
from lib.filesystem     import Filesystem
from mdbapi.database    import MusicDBDatabase
from lib.db.trackerdb   import TrackerDatabase
from lib.db.lycradb     import LycraDatabase
from lib.cfg.musicdb    import MusicDBConfig


class upgrade(MDBModule, MusicDBDatabase):
    def __init__(self, config, database):
        MDBModule.__init__(self)

        self.db  = database
        self.cfg = config
        self.fs  = None


    @staticmethod
    def MDBM_CreateArgumentParser(parserset, modulename):
        parser = parserset.add_parser(modulename, help="Upgrade MusicDB's internal files to the current version")
        parser.set_defaults(module=modulename)
        return parser


    def PrintCheckFile(self, filename):
        print("\033[1;35m * \033[1;34mChecking \033[0;36m%s\033[1;34m: "%(filename), end="")

    def PrintGood(self):
        print("\033[1;32mOK\033[0m")

    def PrintError(self, error):
        print("\033[1;31mFailed! \033[1;30m(%s)\033[0m"%(str(error)))

    def PrintUpgrade(self, fromversion, toversion):
        print("\033[1;33mOutdated\033[0m")
        print("\033[1;34m\tUpgrading from \033[0;33m%i\033[1;34m to \033[0;32m%i\033[1;34m: "%(fromversion, toversion), end="")


    def GetDatabaseVersion(self, database):
        try:
            result = self.db.GetFromDatabase("SELECT value FROM meta WHERE key = 'version'")
            version = int(result[0][0])
        except Exception as e:
            version = 0
        return version


    def AddMetaTableToDatabase(self, database):
        # This needs to be done for all three databases, music.db, lycra.db and tracker.db
        # to upgrade them to version 2
        try:
            self.db.Execute("CREATE TABLE IF NOT EXISTS meta (id INTEGER PRIMARY KEY AUTOINCREMENT, key TEXT, VALUE TEXT DEFAULT '')")
            self.db.Execute("INSERT INTO meta (key, value) VALUES (\"version\", 2)")
        except Exception as e:
            self.PrintError(str(e))
            return False
        return True


    def UpgradeMusicDB(self):
        self.PrintCheckFile("music.db")
        newversion = 2

        # Check version of MusicDB
        version = self.GetDatabaseVersion(self.db)

        # Check if good
        if version == newversion:
            self.PrintGood()
            return True

        # Upgrade if too old
        self.PrintUpgrade(version, newversion)
        if version == 1:
            retval = self.AddMetaTableToDatabase(self.db)
            if not retval:
                return False
            version = 2

        self.PrintGood()
        return True


    def UpgradeTrackerDB(self):
        self.PrintCheckFile("tracker.db")
        trackerdb  = TrackerDatabase(self.cfg.tracker.dbpath)
        newversion = 2

        # Check current version
        version = self.GetDatabaseVersion(trackerdb)

        # Check if good
        if version == newversion:
            self.PrintGood()
            return True

        # Upgrade if too old
        self.PrintUpgrade(version, newversion)
        if version == 1:
            retval = self.AddMetaTableToDatabase(trackerdb)
            if not retval:
                return False
            version = 2

        self.PrintGood()
        return True


    def UpgradeLycraDB(self):
        self.PrintCheckFile("lycra.db")
        lycradb    = TrackerDatabase(self.cfg.lycra.dbpath)
        newversion = 2

        # Check current version
        version = self.GetDatabaseVersion(lycradb)

        # Check if good
        if version == newversion:
            self.PrintGood()
            return True

        # Upgrade if too old
        self.PrintUpgrade(version, newversion)
        if version == 1:
            retval = self.AddMetaTableToDatabase(lycradb)
            if not retval:
                return False
            version = 2

        self.PrintGood()
        return True



    def UpgradeConfiguration(self):
        self.PrintCheckFile("musicdb.ini")
        filename   = "/etc/musicdb.ini"
        musicdbini = configparser.ConfigParser()
        musicdbini.read(filename)
        newversion = 2

        # Check current version
        version = musicdbini.get("meta", "version", fallback="1")
        version = int(version)

        # Check if good
        if version == newversion:
            self.PrintGood()
            return True

        # Upgrade if too old
        self.PrintUpgrade(version, newversion)
        if version == 1:
            wsapikey = base64.b64encode(os.urandom(32)).decode()    # Use an base64 encoded 32 byte random number
            musicdbini.add_section("meta")
            musicdbini.set("meta", "version", "2")
            musicdbini.set("websocket", "apikey", wsapikey)
            musicdbini.remove_option("server", "maxcallthreads")
            musicdbini.remove_option("server", "statefile")
            try:
                with open(filename, "w") as configfile:
                    musicdbini.write(configfile)
            except Exception as e:
                self.PrintError(str(e))
                return False
            version = 2

        if version == 2:
            musicdbini.set("meta", "version", "3")
            musicdbini.set("tracker", "cuttime",    "30")
            musicdbini.set("Randy",   "maxage",     "24")
            musicdbini.set("Randy",   "maxsonglen", "600")
            try:
                with open(filename, "w") as configfile:
                    musicdbini.write(configfile)
            except Exception as e:
                self.PrintError(str(e))
                return False
            version = 3


        # Reload configuration
        self.cfg = MusicDBConfig(filename)

        self.PrintGood()
        return True






    #def UpgradeWebUIConfiguration(self):
    #    self.PrintCheckFile("WebUI")
    #    newversion = 2

    #    # Check current version
    #    version = # TODO

    #    # Check if good
    #    if version == newversion:
    #        self.PrintGood()
    #        return True

    #    # Upgrade if too old
    #    self.PrintUpgrade(version, newversion)
    #    if version == 1:
    #        # TODO

    #    self.PrintGood()
    #    return True



    # return exit-code
    def MDBM_Main(self, args):

        self.UpgradeConfiguration()
        self.UpgradeMusicDB()
        self.UpgradeTrackerDB()
        self.UpgradeLycraDB()
        #self.UpgradeWebUIConfiguration()
        return 0

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

