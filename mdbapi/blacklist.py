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
The *randy* module provides a way to select random songs that can be put into the Song Queue.
The selection of random songs follows certain constraints.

The *blacklist* module provides an interface to the blacklists of artist, albums and songs
that shall not be played for a certain (configured) time.


Blacklist
---------

There are three FIFO organized blacklists: For songs, albums and artists.
Each blacklist holds the IDs of the last played songs, albums and artists.

If a user adds a song into the Queue, this song must be added manually by calling the :meth:`~mdbapi.blacklist.BlacklistInterface.AddSong` method.
This must also be done if the song got selected by :class:`~mdbapi.randy.Randy`.

Once a song got added to the blacklist, it remains even if the song got removed from the queue.

The length of those blacklist can be configured in the MusicDB Configuration:

    .. code-block:: ini

            [Randy]
            songbllen=50
            albumbllen=20
            artistbllen=10

For small music collections, the lengths should not exceed the possibility to provide individual data.
For medium collections and above, the default values as shown in the example are good.
When set to ``0``, the blacklist for the songs, albums or artists will be disabled.

The blacklists get maintained by the :class:`~Randy` class.
Each instance of this class accesses the same global blacklist.

The blacklist is implemented as a dictionary with the keys ``"songs"``, ``"albums"`` and ``"artists"``.
Their values are lists of dictionaries.
The key of the dictionary are:

    id:
        holding the IDs of the songs, albums and artists.

    timestamp:
        storing the UNIX time stamp when the ID got on the blacklist.

Both entries can be ``None`` when not set.
"""

import logging
import threading        # for Lock
import time
from lib.cfg.musicdb    import MusicDBConfig
from lib.db.musicdb     import MusicDatabase
from lib.cfg.mdbstate   import MDBState

BlacklistLock = threading.RLock()
Blacklist     = None



class BlacklistInterface(object):
    """
    This class provides methods to manage the blacklists used by :class:`~mdbapi.randy.Randy`.

    Args:
        config: :class:`~lib.cfg.musicdb.MusicDBConfig` object holding the MusicDB Configuration
        database: A :class:`~lib.db.musicdb.MusicDatabase` instance

    Raises:
        TypeError: When the arguments are not of the correct type.
    """

    def __init__(self, config, database):
        if type(config) != MusicDBConfig:
            raise TypeError("config argument not of type MusicDBConfig")
        if type(database) != MusicDatabase:
            raise TypeError("database argument not of type MusicDatabase")

        self.db         = database
        self.cfg        = config
        self.mdbstate   = MDBState(self.cfg.server.statedir, self.db)

        # Load most important keys
        self.songbllen   = self.cfg.randy.songbllen
        self.albumbllen  = self.cfg.randy.albumbllen
        self.artistbllen = self.cfg.randy.artistbllen

        # Check blacklist and create new one if there is none yet
        global Blacklist
        global BlacklistLock

        with BlacklistLock:
            if not Blacklist:
                # try to load the blacklist from MusicDB State
                Blacklist = self.mdbstate.LoadBlacklists(self.songbllen, self.albumbllen, self.artistbllen)



    def ValidateBlacklist(self, blacklistname):
        """
        This method validates a specific blacklist.
        It checks each entry in the list if its time stamp is still in the configured time range.
        If not, the entry gets set to ``None``.

        Args:
            blacklistname (str): A valid name for the blacklist. Valid names are: ``"songs"``, ``"albums"``, ``"artists"``

        Returns:
            *Nothing*

        Raises:
            ValueError: When blacklistname is not ``"songs"``, ``"albums"`` or ``"artists"``
        """
        if blacklistname not in ["songs", "albums", "artists"]:
            raise ValueError("blacklistname must be \"songs\", \"albums\" or \"artists\"!")

        timelimit = time.time() - self.cfg.randy.maxblage*60*60;

        global BlacklistLock
        global Blacklist

        removed = 0
        with BlacklistLock:
            for entry in Blacklist[blacklistname]:
                if entry["timestamp"] == None:
                    continue

                if entry["timestamp"] < timelimit:
                    entry["id"]        = None
                    entry["timestamp"] = None
                    removed           += 1

        if removed > 0:
            logging.debug("%d entries from blacklist \"%s\" removed because their lifetime exceeded",
                    removed, blacklistname)
        return



    def GetIDsFromBlacklist(self, blacklistname):
        """
        This method returns a list of IDs (as Integer) from the blacklist.
        It checks each entry in the list if it is ``None``.
        If it is ``None``, it gets ignored.
        
        .. info::
            This method does not check if the IDs time stamp is in a valid range.
            Call :meth:`~mdbapi.blacklist.BlacklistInterface.ValidateBlacklist` before to make sure
            all entries in the blacklist are valid.

        Args:
            blacklistname (str): A valid name for the blacklist. Valid names are: ``"songs"``, ``"albums"``, ``"artists"``

        Returns:
            A list of valid IDs as integers.

        Raises:
            ValueError: When blacklistname is not ``"songs"``, ``"albums"`` or ``"artists"``
        """
        if blacklistname not in ["songs", "albums", "artists"]:
            raise ValueError("blacklistname must be \"songs\", \"albums\" or \"artists\"!")

        global BlacklistLock
        global Blacklist

        with BlacklistLock:
            idlist = [ entry["id"] for entry in Blacklist[blacklistname] if entry["id"] != None ]

        return idlist



    def GetValidIDsFromBlacklists(self):
        """
        Returns all Song, Album and Artist IDs from the blacklist.
        The IDs are separated into three lists.
        This method checks the time stamp and removes all IDs that are older than configured.

        This method combines the following methods for all three blacklists (songs, albums, artists):
        
            #. :meth:`~mdbapi.blacklist.BlacklistInterface.ValidateBlacklist`
            #. :meth:`~mdbapi.blacklist.BlacklistInterface.GetIDsFromBlacklist`

        Returns:
            A tupel ``(SongIDs, AlbumIDs, ArtistIDs)`` of lists of IDs that are temporal still valid.
        """
        songids   = []
        albumids  = []
        artistids = []

        self.ValidateBlacklist("songs")
        self.ValidateBlacklist("albums")
        self.ValidateBlacklist("artists")

        songids   = self.GetIDsFromBlacklist("songs")
        albumids  = self.GetIDsFromBlacklist("albums")
        artistids = self.GetIDsFromBlacklist("artists")

        return (songids, albumids, artistids)



    def CheckAllLists(self, song):
        """
        This method checks if a song, its album or artist is on one of the blacklists.
        If it is so, the method returns ``True``.
        If none are on the blacklists, ``False`` gets returned.

        If the song is ``None`` nothing happens.

        Args:
            song (dict/int): A song from the :class:`~lib.db.musicdb.MusicDatabase` or the song ID

        Returns:
            ``True`` if song, album or artist is on blacklist. ``False`` otherwise.

        Raises:
            TypeError: When ``song`` is not of type ``dict`` or ``int``
        """
        if not song:
            return

        if type(song) == int:
            song = self.db.GetSongById(song)
        elif type(song) != dict:
            raise TypeError("song argument must be of type dict or a song ID (int). Actual type was %s!"%(str(type(song))))

        songbl, albumbl, artistbl = self.GetValidIDsFromBlacklists()

        if self.artistbllen > 0 and song["artistid"] in artistbl:
            logging.debug("artist on blacklist")
            return True
        if self.albumbllen > 0 and song["albumid"] in albumbl:
            logging.debug("album on blacklist")
            return True
        if self.songbllen > 0 and song["id"] in songbl:
            logging.debug("song on blacklist")
            return True
        return False



    def CheckSongList(self, song):
        """
        This method checks if a song is on the song blacklists.
        If it is so, the method returns ``True``.

        If the song is ``None`` nothing happens.

        Args:
            song (dict/int): A song from the :class:`~lib.db.musicdb.MusicDatabase` or the song ID

        Returns:
            ``True`` if song is on blacklist. ``False`` otherwise.

        Raises:
            TypeError: When ``song`` is not of type ``dict`` or ``int``
        """
        if not song:
            return

        if type(song) == int:
            song = self.db.GetSongById(song)
        elif type(song) != dict:
            raise TypeError("song argument must be of type dict or a song ID (int). Actual type was %s!"%(str(type(song))))

        songbl, albumbl, artistbl = self.GetValidIDsFromBlacklists()

        if self.songbllen > 0 and song["id"] in songbl:
            logging.debug("song on blacklist")
            return True
        return False



    def AddSong(self, song):
        """
        This method pushes a song onto the blacklists.
        If the song is ``None`` nothing happens.

        This method should be the only place where the blacklist gets changed.
        After adding a song, the lists get stored in the MusicDB State Directory to be persistent
        
        If the length of the blacklist exceeds its limit, the oldest entry gets dropped.

        Args:
            song (dict/int): A song from the :class:`~lib.db.musicdb.MusicDatabase` or the song ID

        Returns:
            *Nothing*

        Raises:
            TypeError: When ``song`` is not of type ``dict`` or ``int``
        """
        if not song:
            return

        if type(song) == int:
            song = self.db.GetSongById(song)
        elif type(song) != dict:
            raise TypeError("song argument must be of type dict or a song ID (int). Actual type was %s!"%(str(type(song))))

        global BlacklistLock
        global Blacklist

        logging.debug("Setting song \"%s\" onto the blacklist.", song["path"])
        with BlacklistLock:
            if self.artistbllen > 0:
                entry = {}
                entry["timestamp"] = int(time.time())
                entry["id"]        = song["artistid"]
                Blacklist["artists"].pop(0)
                Blacklist["artists"].append(entry)
            if self.albumbllen > 0:
                entry = {}
                entry["timestamp"] = int(time.time())
                entry["id"]        = song["albumid"]
                Blacklist["albums"].pop(0)
                Blacklist["albums"].append(entry)
            if self.songbllen > 0:
                entry = {}
                entry["timestamp"] = int(time.time())
                entry["id"]        = song["id"]
                Blacklist["songs"].pop(0)
                Blacklist["songs"].append(entry)

            # Remove outdated entries before saving
            self.ValidateBlacklist("songs")
            self.ValidateBlacklist("albums")
            self.ValidateBlacklist("artists")

            # Save blacklists to files 
            self.mdbstate.SaveBlacklists(Blacklist)



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

