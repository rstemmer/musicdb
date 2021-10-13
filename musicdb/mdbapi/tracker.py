# MusicDB,  a music manager with web-bases UI that focus on music.
# Copyright (C) 2017 - 2021  Ralf Stemmer <ralf.stemmer@gmx.net>
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
This module provides a tracker to track songs and videos that were streamed.
The goal of the tracker is to collect information which songs and videos can be played in series.
So the relation between two songs or videos gets stored in a database - the Tracker Database.
The user can then get the information which song/video were played after (or before) a specific song/video.

The Tracker consists of the following parts:

    * The **Tracker** class (:class:`~musicdb.mdbapi.tracker.Tracker`) tracking music with an internal queue that holds the last played song or and video.
    * The **Tracker Database** (:class:`~musicdb.lib.db.trackerdb.TrackerDatabase`) that stores the tracked music relations.

Example:

    .. code-block:: python

        # Dependencies 
        cfg = MusicDBConfig("./musicdb.ini")

        # Create a new tracker
        tracker = SongTracker(cfg)
        tracker.AddSong("Unicorn/2000 - Honey Horn/13 Rainbow Song.mp3")
        tracker.AddSong("Truther/2013 - Real Album/23 Illuminati.mp3")

"""

import logging
import time
from musicdb.lib.db.trackerdb   import TrackerDatabase
from musicdb.lib.cfg.musicdb    import MusicDBConfig



class Tracker(object):
    """
    This class tracks music (songs and videos) that were played after each other.
    So it gets tracked what songs or videos the user put together into the queue because their style fit to each other.
    
    Only completely played music should considered.
    Skipped music should be ignored.

    .. warning::

        It tracks the played songs and videos using a local state.
        Creating a new instance of this class also creates a further independent tracker.
        This could mess up the database with relations that were counted twice!

    .. note::

        For better readability it is recommended to use the derived classes :class:`~musicdb.mdbapi.tracker.SongTracker` and :class:`~musicdb.mdbapi.tracker.VideoTracker`.

    Args:
        config: :class:`~musicdb.lib.cfg.musicdb.MusicDBConfig` object holding the MusicDB Configuration
        target (str): ``"song"`` or ``"video"`` depending what kind of music will be tracked

    Raises:
        TypeError: When the arguments are not of the correct type.
        ValueError: When ``target`` is not ``"song"`` or ``"video"``
    """
    def __init__(self, config, target):
        if type(config) != MusicDBConfig:
            raise TypeError("config argument not of type MusicDBConfig")
        if type(target) != str:
            raise TypeError("target argument not of type str")

        if not target in ["song", "video"]:
            raise ValueError("target must be \"song\" or \"video\"");

        self.config      = config
        self.disabled    = config.debug.disabletracker
        self.target      = target
        self.lastid      = None
        self.lastaction  = time.time()

        # When tracking is disabled, don't even instantiate the databases.
        # Tracking is disabled for a reason, so protect the databases as good as possible!
        if not self.disabled:
            self.trackerdb = TrackerDatabase(config.files.trackerdatabase)



    def Track(self, targetid):
        """
        This method tracks the relation to the given target with the last added target.
        A target can be a song or a video.
        This new target should be a target that was recently and completely played.

        If the time between this target, and the previous one exceeds *N* minutes, it gets ignored and the internal state gets reset.
        So the chain of targets get cut if the time between playing them is too long.
        The chain of targets gets also cut, if ``targetid`` is ``None`` or invalid.
        The amount of time until this cut takes place can be configured: :doc:`/basics/config`

        If the given target is the same as the last target, then it gets ignored.

        After adding a target, the method checks for a new relation between two targets.
        This is the case when there was previously a target added.

        The relation gets added to the tracker database by calling :meth:`musicdb.lib.db.trackerdb.TrackerDatabase.AddRelation`

        Args:
            targetid: ID of the song or video that gets currently played, ``None`` to cut the chain of consecutive targets.

        Returns:
            ``True`` on success. ``False`` in case an error occurred.
        """
        # Check argument (A situation where ID was None leads to chaos.)
        if type(targetid) != int:
            # Cut chain
            self.lastid = None

            if targetid == None:
                logging.debug(self.target+" ID of new "+self.target+" is None! \033[0;33m(Clearing tracking chain)")
                return True # None is allowed to cut the chain.

            logging.warning(self.target+" ID of new "+self.target+" is not an integer! The type was %s. \033[0;33m(Ignoring the Track-Call and clearing tracking list)", str(type(targetid)))
            return False

        # If there is a *cuttime* Minute gap, do not associate this target with the previous -> clear list
        timestamp = time.time()
        timediff  = int(timestamp - self.lastaction)
        
        if timediff > self.config.tracker.cuttime * 60:
            logging.debug("Resetting tracker history because of a time gap greater than %i minutes.", timediff//60)
            self.queue = []
        
        self.lastaction = timestamp

        if self.lastid == targetid:
            logging.debug("The new "+self.target+" to track (%i) is the same as the previous one - so it gets ignored", targetid)
            return True

        # Adding new target to the history
        logging.debug("Tracking new "+self.target+" with ID %i", targetid)

        # If there was no previous target, initialize the tracker.
        if not self.lastid:
            self.lastid = targetid
            logging.debug("Starting new tracking chain with "+self.target+" ID %i.", targetid)
            return True

        if self.disabled:
            # do not do anything further when tracer is deactivated
            logging.info("Updating tracker disabled. \033[1;33m!! \033[1;30m(Will not process relationship between %i and %i)", self.lastid, targetid)
            self.lastid = targetid    # fake the last step for better debugging
            return True

        # store relation
        try:
            self.trackerdb.AddRelation(self.target, self.lastid, targetid)
        except Exception as e:
            logging.error("trackerdb.AddRelation failed with error \"%s\"!", str(e))
            return False

        logging.debug("New "+self.target+" relation added: \033[0;35m%i → %i", self.lastid, targetid)

        # Rotate the chain
        self.lastid = targetid

        return True



class SongTracker(Tracker):
    """
    See :class:`~musicdb.mdbapi.tracker.Tracker`
    """
    def __init__(self, config):
        Tracker.__init__(self, config, "song")

    def TrackSong(self, songid):
        """
        See :meth:`~musicdb.mdbapi.tracker.Tracker.Track`
        """
        self.Track(songid);

class VideoTracker(Tracker):
    """
    See :class:`~musicdb.mdbapi.tracker.Tracker`
    """
    def __init__(self, config):
        Tracker.__init__(self, config, "video")

    def TrackVideo(self, videoid):
        """
        See :meth:`~musicdb.mdbapi.tracker.Tracker.Track`
        """
        self.Track(videoid);



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

