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

Randy consists of two parts:

    * A global `Blacklist`_ for songs, albums and artists
    * A class :class:`~Randy` that provides methods to get random songs


Blacklist
---------

There are three FIFO organized blacklists: For songs, albums and artists.
Each blacklist holds the IDs of the last played songs, albums and artists.

Songs that will be selected by the :class:`~Randy` class will be added to the blacklists automatically.
If a user adds a song into the Queue, this song must be added manually by calling the :meth:`~mdbapi.randy.Randy.AddSongToBlacklist` method.

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

Song Selection Algorithm
------------------------

Selecting a random song is done in two stages, the `Database Stage`_ and the `Blacklist Stage`_
The first stage selects a song from a limited set of songs, the second stage checks if the song is on a blacklist.
In each stage, a song can be rejected and the algorithm starts at the beginning.


.. warning::

    The process of trying to get a good song gets repeated until a good song is found.
    If over constraint, this ends in an infinite loop!


Database Stage
^^^^^^^^^^^^^^

In the first stage, a song gets chosen by the database via :meth:`lib.db.musicdb.MusicDatabase.GetRandomSong`.
There are 4 parameters that define the constraints applied on set of possible songs:

    - The activated genres as maintained by the :mod:`lib.cfg.mdbstate` module.
    - The flag if *disabled* songs shall be excluded
    - The flag if *hated* songs shall be excluded
    - Minimum length of a song in seconds

Some of them can be configured in the MusicDB configuration file:

    .. code-block:: ini

        [Randy]
        nodisabled=True
        nohated=True
        minsonglen=120

Because the database only takes album tags into account, the song tags gets checked afterwards.
If the song has a confirmed genre tag, and if this tag does not match the filter, the song gets rejected.
Song genres set by the Music AI (see :doc:`/mdbapi/musicai`) will be ignored because the AI may be wrong.


Blacklist Stage
^^^^^^^^^^^^^^^

The selected song from the first stage now gets compared to the three blacklists.
If the song, or its album or artist, is listed in one of blacklist, 
then the song, a song from the same album or from the same artist was played recently.
So, the chosen song gets dropped and the finding-process starts again.

Is the blacklist length set to 0, the specific blacklist is disabled

If a song is found. The oldest entries of the blacklist get dropped, and the new song, album, artist get pushed on top of the list.
"""

import logging
import threading        # for Lock
import datetime
from lib.cfg.musicdb    import MusicDBConfig
from lib.db.musicdb     import MusicDatabase
from lib.cfg.mdbstate   import MDBState

BlacklistLock = threading.Lock()
Blacklist     = None



class Randy(object):
    """
    This class provides methods to get a random song under certain constraints.

    This class is made to access the thread form all over the code simultaneously.

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
        self.mdbstate   = MDBState(self.cfg.server.statefile, self.db)

        # Load most important keys
        self.nodisabled  = self.cfg.randy.nodisabled
        self.nohated     = self.cfg.randy.nohated
        self.minlen      = self.cfg.randy.minsonglen
        self.songbllen   = self.cfg.randy.songbllen
        self.albumbllen  = self.cfg.randy.albumbllen
        self.artistbllen = self.cfg.randy.artistbllen

        # Check blacklist and create new one if there is none yet
        # TODO: load last state from file?
        global Blacklist
        global BlacklistLock

        with BlacklistLock:
            if not Blacklist:
                Blacklist = {}
                Blacklist["songs"]   = [None] * self.songbllen
                Blacklist["albums"]  = [None] * self.albumbllen
                Blacklist["artists"] = [None] * self.artistbllen



    def AddSongToBlacklist(self, song):
        """
        This method pushes a song onto the blacklists.
        If the song is ``None`` nothing happens.

        Args:
            song (dict): A song from the :class:`~lib.db.musicdb.MusicDatabase`

        Returns:
            *Nothing*
        """
        if not song:
            return

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



    def GetSong(self):
        """
        This method chooses a random song in a two-stage process as described in the module description.

        Returns:
            A song from the :class:`~lib.db.musicdb.MusicDatabase` or ``None`` if an error occurred.
        """
        global BlacklistLock
        global Blacklist

        filterlist = self.mdbstate.GetFilterList()
        if not filterlist:
            logging.warning("No Genre selected! \033[1;30(Selecting random song from the whole collection)")

        # Get Random Song - this may take several tries 
        logging.debug("Randy starts looking for a random song …")
        t_start = datetime.datetime.now()
        song    = None
        while not song:
            # STAGE 1: Get Mathematical random song (under certain constraints)
            try:
                song = self.db.GetRandomSong(filterlist, self.nodisabled, self.nohated, self.minlen)
            except Exception as e:
                logging.error("Getting random song failed with error: \"%s\"!", str(e))
                return None

            if not song:
                logging.error("There is no song fulfilling the constraints! \033[1;30(Check the stage 1 constraints)")
                return None

            logging.debug("Candidate for next song: \033[0;35m" + song["path"])

            # GetRandomSong only looks for album genres.
            # The song genre may be different and not in the set of the filerlist.
            try:

                songgenres = self.db.GetTargetTags("song", song["id"], MusicDatabase.TAG_CLASS_GENRE)
                # Create a set of tagnames if there are tags for this song.
                # Ignore AI set tags because they may be wrong
                if songgenres:
                    tagnames = { songgenre["name"] for songgenre in songgenres if songgenre["approval"] >= 1 }
                else:
                    tagnames = { }

                # If the tag name set was successfully created, compare it with the selected genres
                if tagnames:
                    if not tagnames & set(filterlist):
                        logging.debug("song is of different genre than album and not in activated genres. (Song genres: %s)", str(tagnames))
                        song = None
                        continue

            except Exception as e:
                logging.error("Song tag check failed with exception: \"%s\"!", str(e))
                return None


            # STAGE 2: Make randomness feeling random by checking if the song was recently played
            with BlacklistLock:
                if self.artistbllen > 0 and song["artistid"] in Blacklist["artists"]:
                    logging.debug("artist on blacklist")
                    song = None
                    continue
                if self.albumbllen > 0 and song["albumid"] in Blacklist["albums"]:
                    logging.debug("album on blacklist")
                    song = None
                    continue
                if self.songbllen > 0 and song["id"] in Blacklist["songs"]:
                    logging.debug("song on blacklist")
                    song = None
                    continue 

        # New song found \o/
        # Add song into blacklists
        self.AddSongToBlacklist(song)

        t_stop = datetime.datetime.now()
        logging.debug("Randy found the following song after %s : \033[0;36m%s", str(t_stop-t_start), song["path"])
        return song



    def GetSongFromAlbum(self, albumid):
        """
        Get a random song from a specific album.

        If the selected song is listed in the blacklist for songs, a new one will be selected.
        Entries in the album and artist blacklist will be ignored because the artist and album is forced by the user.
        But the song gets added to the blacklist for songs, as well as the album and artist gets added.

        The genre of the song gets completely ignored.
        The user wants to have a song from the given album, so it gets one.

        .. warning::

            This is a dangerous method.
            An album only has a very limited set of songs.

            If all the songs are listed in the blacklist, the method would get caught in an infinite loop.
            To avoid this, there are only 10 tries to find a random song.
            If after the tenth try, the method leaves returning ``None``

        Args:
            albumid (int): ID of the album the song shall come from

        Returns:
            A song from the :class:`~lib.db.musicdb.MusicDatabase` or ``None`` if an error occurred.
        """
        global BlacklistLock
        global Blacklist

        # Get parameters
        song       = None
        tries      = 0  # there is just a very limited set of possible songs. Avoid infinite loop when all songs are on the blacklist

        while not song and tries <= 10:
            tries += 1
            # STAGE 1: Get Mathematical random song (under certain constraints)
            try:
                song = self.db.GetRandomSong(None, self.nodisabled, self.nohated, self.minlen, albumid)
            except Exception as e:
                logging.error("Getting random song failed with error: \"%s\"!", str(e))
                return None
            logging.debug("Candidate for next song: \033[0;35m" + song["path"])
            
            # STAGE 2: Make randomness feeling random by checking if the song was recently played
            # only check, if that song is in the blacklist. Artist and album is forced by the user
            with BlacklistLock:
                if self.songbllen > 0 and song["id"] in Blacklist["songs"]:
                    logging.debug("song on blacklist")
                    song = None
                    continue 

        if not song:
            logging.warning("The loop that should find a new random song did not deliver a song! \033[1;30m(This happens when there are too many songs of the given album are already on the blacklist)")
            return None

        # maintain blacklists
        self.AddSongToBlacklist(song)

        # Add song to queue
        logging.debug("Randy adds the following song after %s tries: \033[0;36m%s", tries, song["path"])
        return song



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

