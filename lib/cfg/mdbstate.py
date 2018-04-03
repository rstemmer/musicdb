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
"""
This module takes care that the state of MusicDB will persist over several sessions.
This is not done automatically by the :class:`~MDBState` class.
Each read or write process to the files that hold the state will be triggered by the classes who manage the related information.

The state is stored in several files in a directory that can be configured via ``[server]->statedir``

All files inside the state directory are managed by the :class:`~MDBState` class.
The content of those files should not be changed by any user because its content gets not validated.
"""

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

    The following table shows which method is responsible for which file in the MusicDB State Directory.

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
        musicdb: Instance of the MusicDB Database (can be None)
    """

    def __init__(self, path, musicdb=None):

        Config.__init__(self, os.path.join(path, "state.ini"))
        self.musicdb = musicdb;
        self.path    = path;
        self.queue   = QUEUE()


    def ReadList(self, listname):
        """
        Reads a list from the mdbstate directory.
        The ``listname`` argument defines which file gets read: ``config.server.statedir/listname.csv``.

        This method should only be used by class internal methods.

        Args:
            listname (str): Name of the list to read without trailing .csv

        Returns:
            A list of rows from the file.
        """
        path = os.path.join(self.path, listname + ".csv")
        csv  = CSVFile(path)
        rows = csv.Read()
        return rows


    def WriteList(self, listname, rows):
        """
        This method write a list of rows into the related file.
        The ``listname`` argument defines which file gets written: ``config.server.statedir/listname.csv``.

        This method should only be used by class internal methods.

        Args:
            listname (str): Name of the list to read without trailing .csv
            rows(list): The list that shall be stored

        Returns:
            ``None``
        """
        path = os.path.join(self.path, listname + ".csv")
        csv  = CSVFile(path)
        csv.Write(rows)
        return None


    def LoadSongQueue(self):
        """
        This method reads the song queue from the state directory.

        The method returns the queue as needed inside :meth:`mdbapi.songqueue.SongQueue`:
        A list of tuple, each containing the entryid and songid as integers.

        The UUIDs of the queue entries remain.

        Returns:
            A stored song queue
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
        This method saves a song queue.
        The data structure of the queue must be exact as the one expected when the queue shall be loaded.

        Args:
            queue (list): The song queue to save.

        Returns:
            *Nothing*
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

