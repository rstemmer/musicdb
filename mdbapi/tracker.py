# MusicDB,  a music manager with web-bases UI that focus on music.
# Copyright (C) 2017 - 2020  Ralf Stemmer <ralf.stemmer@gmx.net>
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
Beside the songs, also the artist relations are tracked.

The Tracker consists of two parts:

    * The **Tracker** class (:class:`~mdbapi.tracker.Tracker`) tracking songs with an internal queue that holds the last played songs.
    * The **Tracker Database** (:class:`~lib.db.trackerdb.TrackerDatabase`) that stores the tracked song relations.

Example:

    .. code-block:: python

        # Dependencies 
        cfg = MusicDBConfig("./musicdb.ini")

        # Create a new tracker
        tracker = Tracker(cfg)
        tracker.AddSong("Unicorn/2000 - Honey Horn/13 Rainbow Song.mp3")
        tracker.AddSong("Truther/2013 - Real Album/23 Illuminati.mp3")

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
    It should also track randomly added songs assuming the user skips or removes songs that don't fit.
    Only completely played songs should considered.
    Skipped songs should be ignored.
    Beside the songs, also the artist relations get tracked.
    The artist relation gets derived from the song relations.

    .. warning::

        It tracks the played songs using a local state.
        Creating a new instance of this class also creates a further independent tracker.
        This could mess up the database with relations that were counted twice!

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

        self.config     = config
        self.disabled   = config.debug.disabletracker
        self.lastsongid = None
        self.lastaction = time.time()

        # When tracking is disabled, don't even instantiate the databases.
        # Tracking is disabled for a reason, so protect the databases as good as possible!
        if not self.disabled:
            self.trackerdb = TrackerDatabase(config.tracker.dbpath)
            if musicdb:
                self.musicdb = musicdb
            else:
                self.musicdb = MusicDatabase(config.database.path)




    def AddSong(self, songid):
        """
        This method tracks the relation to the given song with the last added song.
        This new song should be a song that was recently and completely played.

        If the time between this song, and the previous one exceeds *N* minutes, it gets ignored and the internal state gets reset.
        So the chain of songs get cut if the time between playing them is too long.
        The chain of songs gets also cut, if *songid* is ``None`` or invalid.
        The amount of time until this cut takes place can be configured: :doc:`/basics/config`

        If the given song is the same as the last song, then it gets ignored.

        After adding a song, the method checks for a new relation between two songs.
        This is the case when there was previously a song added.

        If there is a relation to track then the songs get loaded from the :class:`lib.db.musicdb.MusicDatabase` to get the artist IDs.
        The relation gets added to the tracker database by calling :meth:`lib.db.trackerdb.TrackerDatabase.AddRelation`

        Args:
            songid: song ID of the song that gets currently played, ``None`` to cut the chain of consecutive songs.

        Returns:
            ``True`` on success. ``False`` in case an error occurred.
        """
        # Check argument (A situation where songID was None leads to chaos.)
        if type(songid) != int:
            self.lastsongid = None
            if songid == None:
                return True # None is allowed to cut a song chain.
            logging.warning("Song ID of new song is not an integer! The type was $s. \033[0;33m(Ignoring the NewSong-Call and clearing tracking list)", str(type(songid)))
            return False

        # If there is a *cuttime* Minute gap, do not associate this song with the previous -> clear list
        timestamp = time.time()
        timediff  = int(timestamp - self.lastaction)
        
        if timediff > self.config.tracker.cuttime * 60:
            logging.debug("Resetting tracker history because of a time gap greater than %i minutes.", timediff//60)
            self.queue = []
        
        self.lastaction = timestamp

        if self.lastsongid == songid:
            logging.debug("The new song to track (%i) is the same as the previous one - so it gets ignored", songid)
            return True

        # Adding new song to the history
        logging.debug("Tracking new song with ID %i", songid)

        # If there was no previous song, initialize the tracker.
        if not self.lastsongid:
            self.lastsongid = songid
            return True

        if self.disabled:
            # do not do anything further when tracer is deactivated
            logging.info("Updating tracker disabled. \033[1;33m!! \033[1;30m(Will not process relationship between %i and %i)", self.lastsongid, songid)
            self.lastsongid = songid    # fake the last step for better debugging
            return True

        # Get songs
        try:
            songa       = self.musicdb.GetSongById(self.lastsongid)
            songb       = self.musicdb.GetSongById(songid)
            artistida   = songa["artistid"]
            artistidb   = songb["artistid"]
        except Exception as e:
            # If one of the IDs is invalid, then here it will become noticed the first time.
            logging.error("musicdb.GetSongById failed with error \"%s\"!", str(e))
            return False

        # store relation
        try:
            self.trackerdb.AddRelation("song",   self.lastsongid, songid)
            self.trackerdb.AddRelation("artist", artistida, artistidb)
        except Exception as e:
            logging.error("trackerdb.AddRelation failed with error \"%s\"!", str(e))
            return False

        logging.debug("New relation added: \033[0;35m%i → %i", self.lastsongid, songid)

        # Rotate the chain
        self.lastsongid = songid

        return True



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

