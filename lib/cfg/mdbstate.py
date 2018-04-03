# MusicDB,  a music manager with web-bases UI that focus on music.
# Copyright (C) 2017,2018  Ralf Stemmer <ralf.stemmer@gmx.net>
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

from lib.cfg.config import Config
from lib.cfg.csv    import CSVFile
from lib.db.musicdb import MusicDatabase
import logging
import os

class QUEUE:
    pass

class MDBState(Config, object):
    """
    This class holds the MusicDB internal state.

    +------------------------+------------------------+------------------------+
    | File Name              | Read Method            | Write Method           |
    +========================+========================+========================+
    | songqueue.csv          | :meth:`~LoadSongQueue` | :meth:`~SaveSongQueue` |
    +------------------------+------------------------+------------------------+
    | artistblacklist.csv    | :meth:`~LoadBlacklist` |                        |
    +------------------------+------------------------+------------------------+
    | albumblacklist.csv     | :meth:`~LoadBlacklist` |                        |
    +------------------------+------------------------+------------------------+
    | songblacklist.csv      | :meth:`~LoadBlacklist` |                        |
    +------------------------+------------------------+------------------------+

    Args:
        path: Absolute path to the MusicDB state directory
        musicdb: instance of the MusicDB Database (can be None)
    """

    def __init__(self, path, musicdb=None):

        Config.__init__(self, os.path.join(path, "state.ini"))
        self.musicdb = musicdb;
        self.path    = path;
        self.queue   = QUEUE()


    def ReadList(self, listname):
        """
        Reads a list from the mdbstate directory.
        The name is ``config.server.statedir/listname.csv``

        Args:
            listname (str): Name of the list to read without trailing .csv
        """
        path = os.path.join(self.path, listname + ".csv")
        csv  = CSVFile(path)
        rows = csv.Read()
        return rows


    def WriteList(self, listname, rows):
        """
        """
        path = os.path.join(self.path, listname + ".csv")
        csv  = CSVFile(path)
        csv.Write(rows)


    def LoadSongQueue(self):
        """
        This method reads the song queue from the state directory
        """
        rows  = self.ReadList("songqueue")
        queue = []
        for row in rows:
            entryid = int(row[0])
            songid  = int(row[1])
            queue.append((entryid, songid))
        return queue


    def SaveSongQueue(self, queue):
        """
        """
        self.WriteList("songqueue", queue)
        return


    def LoadBlacklists(self):
        """
        Returns:
            (artistblacklist, albumblacklist, songblacklist)
        """
        artists = self.ReadList("artistblacklist")
        albums  = self.ReadList("albumblacklist")
        songs   = self.ReadList("songblacklist")
        return artists, albums, songs


    def GetFilterList(self):
        """
        This method returns a list of the activated genre

        Returns:
            A list of main genre names that are activated
        """
        if not self.musicdb:
            raise ValueError("Music Database object required but it is None.")
        filterlist = []
        genretags   = self.musicdb.GetAllTags(MusicDatabase.TAG_CLASS_GENRE)
        
        self.Reload()
        for tag in genretags:
            state = self.Get(bool, "albumfilter", tag["name"], False)
            if state:
                filterlist.append(tag["name"])

        return filterlist

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

