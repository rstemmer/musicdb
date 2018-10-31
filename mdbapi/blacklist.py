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
Their values are lists holding the IDs of the songs, albums and artists.
"""

import logging
import threading        # for Lock
from lib.cfg.musicdb    import MusicDBConfig
from lib.db.musicdb     import MusicDatabase
from lib.cfg.mdbstate   import MDBState

BlacklistLock = threading.Lock()
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
                loadedlists = self.mdbstate.LoadBlacklists()

                # First, create a clean blacklist
                Blacklist = {}
                Blacklist["songs"]   = [None] * self.songbllen
                Blacklist["albums"]  = [None] * self.albumbllen
                Blacklist["artists"] = [None] * self.artistbllen
                
                # Now fill the blacklist considering changes in their size
                for key in loadedlists:
                    if key not in ["songs", "albums", "artists"]:
                        logging.error("Unexpected key \"%s\" in loaded blacklist dictionary! \033[1;30(Will be discard)", str(key))
                        continue

                    dst = Blacklist[key]
                    src = loadedlists[key]
                    if not src:
                        continue    # when there are no entries loaded, keep the generated list of None-entries

                    # The following python magic inserts as much of src at the end of dst, as fits.
                    # if src must be cut, the first elements get removed
                    # So, case 1: len(dst) > len(src)
                    #   dst = [None, None, None, None, None]
                    #   src = [1, 2, 3]
                    #   Results in [None, None, 1, 2, 3]
                    #
                    # Case 2: len(dst) < len(src)
                    #   dst = [None, None]
                    #   src = [1, 2, 3]
                    #   Results in [2, 3]
                    #
                    # >>> l = [1,2,3]
                    # >>> d = [0]*3
                    # >>> d[-len(l):] = l[-len(d):]
                    # >>> l
                    # [1, 2, 3]
                    # >>> d
                    # [1, 2, 3]
                    # >>> d = [0]*2
                    # >>> d[-len(l):] = l[-len(d):]
                    # >>> l
                    # [1, 2, 3]
                    # >>> d
                    # [2, 3]
                    # >>> d = [0]*4
                    # >>> d[-len(l):] = l[-len(d):]
                    # >>> l
                    # [1, 2, 3]
                    # >>> d
                    # [0, 1, 2, 3]
                    # >>> 
                    dst = dst[-len(src):] = src[-len(dst):]

                    Blacklist[key] = dst



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

        global BlacklistLock
        global Blacklist

        with BlacklistLock:
            if self.artistbllen > 0 and song["artistid"] in Blacklist["artists"]:
                logging.debug("artist on blacklist")
                return True
            if self.albumbllen > 0 and song["albumid"] in Blacklist["albums"]:
                logging.debug("album on blacklist")
                return True
            if self.songbllen > 0 and song["id"] in Blacklist["songs"]:
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

        global BlacklistLock
        global Blacklist

        with BlacklistLock:
            if self.songbllen > 0 and song["id"] in Blacklist["songs"]:
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

        with BlacklistLock:
            if self.artistbllen > 0:
                Blacklist["artists"].pop(0)
                Blacklist["artists"].append(song["artistid"])
            if self.albumbllen > 0:
                Blacklist["albums"].pop(0)
                Blacklist["albums"].append(song["albumid"])
            if self.songbllen > 0:
                Blacklist["songs"].pop(0)
                Blacklist["songs"].append(song["id"])

            # Save blacklists to files 
            self.mdbstate.SaveBlacklists(Blacklist)



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

