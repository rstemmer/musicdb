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
This module provides a tracker to track songs that were streamed.
The goal of the tracker is to collect information which songs can be played in series.
So the relation between two songs gets stored in a database - the Tracker Database.
The user can then get the information which song were played after (or before) a specific song.

The Tracker consists of two parts:

    * The **Tracker** class (:class:`~mdbapi.tracker.Tracker`) tracking songs with an internal queue that holds the last played songs.
    * The **Tracker Database** (:class:`~lib.db.trackerdb.TrackerDatabase`) that stores the tracked song relations.

Example:

    .. code-block:: python

        # Dependencies 
        cfg = MusicDBConfig("./musicdb.ini")

        # Create a new tracker
        tracker = Tracker(cfg)
        tracker.NewSong("Unicorn/2000 - Honey Horn/13 Rainbow Song.mp3")
        tracker.NewSong("Truther/2013 - Real Album/23 Illuminati.mp3")
        tracker.SongSkipped()

        # Stop Tracker
        StopTracker()

"""

import logging
import time
from lib.db.musicdb     import MusicDatabase
from lib.db.trackerdb   import TrackerDatabase
from lib.cfg.musicdb    import MusicDBConfig



class Tracker(object):
    """
    This class tracks songs that were played after each other.
    So it gets tracked what songs the user put together into the queue because their style fit to each other.
    It will also track randomly added songs assuming the user skips songs that don't fit.
    Only completely played songs were considered.
    Skipped songs get ignored.
    Beside the songs, also the artist relations get tracked.
    The artist relation gets derived from the song relations.

    It tracks the played songs in a local queue.
    Creating a new instance of this class also creates a further independent queue.

    The intern queue holds up to three entries. Each is the ID of a played or playing song.
    So the first and second (index 0 and index 1) have a connection that will be tracked
    when a third song gets added to the queue.

    So, the meaning of each entries of the three in the queue is:

        #. The song that was fully played before the last song
        #. The last song that was played completely
        #. The current playing song

    Args:
        config: :class:`~lib.cfg.musicdb.MusicDBConfig` object holding the MusicDB Configuration
        musicdb: Optional a :class:`~lib.db.musicdb.MusicDatabase` instance. When ``None`` a new instance will be created

    Raises:
        TypeError: When the arguments are not of the correct type.
    """
    def __init__(self, config, musicdb):
        if type(config) != MusicDBConfig:
            raise TypeError("config argument not of type MusicDBConfig")
        if type(musicdb) != MusicDatabase:
            raise TypeError("database argument not of type MusicDatabase")

        self.disabled   = config.debug.disabletracker
        self.queue      = []
        self.lastaction = time.time()

        # Open databases if not given as argument
        if not musicdb:
            self.musicdb   = MusicDatabase(self.cfg.database.path)
            self.trackerdb = TrackerDatabase(self.cfg.tracker.dbpath)



    def NewSong(self, songid):
        """
        This method adds a new song to the list of song tracked.

        If the time between this song, and the previous one exceeds 30 minutes, it gets ignored and the internal state gets reset.
        So the chain of songs get cut if the time between playing them is too long.
        The chain of songs gets also cut, if *songpath* is ``None`` or invalid.

        If the last song added to the playlist already exist, it gets ignored.

        After adding a song to the queue, the method checks for a new relation between two songs.
        This is the case if there are three entries in the internal queue.
        If there are less, or if the tracker was disabled by the configuration, 
        nothing will be done.
        The return value will be ``True`` anyway because this is not an error.

        If there are three entries in the queue, the songs get loaded from the :class:`lib.db.musicdb.MusicDatabase` to get the artist IDs.
        Then the relation gets added to the tracker database by calling :meth:`lib.db.tracker.TrackerDatabase.AddEdge`

        Args:
            songid: song ID of the song that gets currently played.

        Returns:
            ``True`` on success. ``False`` in case an error occurred.
        """
        # Check argument (A situation where songID was None leads to chaos.)
        if type(songid) != int:
            self.queue = []
            logging.warning("Song ID of new song is not an integer! The type was $s. \033[0;33m(Ignoring the NewSong-Call and clearing tracking list)", str(type(songid)))
            return False

        # If there is a 30 Minute gap, do not associate this song with the previous -> clear list
        timestamp = time.time()
        timediff  = int(timestamp - self.lastaction)
        
        if timediff > 30*60:  # TODO: make configurable!
            logging.debug("Resetting tracker history because of a time gap greater than %i minutes.", timediff//60)
            self.queue = []
        
        self.lastaction = timestamp

        # Adding new song to the history
        logging.debug("Track new song with ID %i", songid)

        if len(self.queue) > 0:
            if self.queue[-1] != songid:
                self.queue.append(songid)
            else:
                logging.debug("The new song to track (%i) is the same as the previous one - so it gets ignored", songid)
        else:
            self.queue.append(songid)


        # check if we got a new relation (two songs played completely - implies that a 3rd one is currently running)
        # If not, leave the method, otherwise store the connection in the database
        if len(playlist) < 3:
            return True

        songida = self.queue.pop(0)
        songidb = self.queue[0]     # do not remove this song, now its just the successor

        if self.disabled:
            # do not do anything further when tracer is deactivated
            logging.info("Updating tracker disabled. \033[1;33m!! \033[1;30m(Will not process relationship between %i and %i)", songida, songidb)
            return True

        # Get songs
        try:
            songa       = musicdb.GetSongById(songida)
            songb       = musicdb.GetSongById(songidb)
            artistida   = songa["artistid"]
            artistidb   = songb["artistid"]
        except Exception as e:
            # If one of the IDs is invalid, then here it will become noticed the first time.
            logging.error("musicdb.GetSongById failed with error \"%s\"!", str(e))
            return False

        # store relation
        try:
            trackerdb.AddRelation("song",   songida,   songidb)
            trackerdb.AddRelation("artist", artistida, artistidb)
        except Exception as e:
            logging.error("trackerdb.AddRelation failed with error \"%s\"!", str(e))
            return False

        return True



    # The playing song was skipped (undo NewSong-Call - ONCE)
    def SongSkipped(self):
        """
        This method skips the last song added via :meth:`~.mdbapi.tracker.Tracker.NewSong`.
        So that song gets removed from the internal queue of played/playing songs.

        Returns:
            ``None``
        """
        if len(self.queue) > 0:
            self.queue.pop()
            logging.debug("Last tracked song was skipped")
        return None


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

