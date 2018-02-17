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
This module provides a tracker to track songs that were played by MusicDBs backend MPD (Music Playing Daemon).
The goal of the tracker is to collect information which songs can be played in series.
So the relation between two songs gets stored in a database.
The user can than get the information which song were played after (or before) a specific song.

The Tracker consists of three parts:

    * The **Tracker Thread** (:meth:`~mdbapi.tracker.TrackerThread`) and its environment :meth:`~mdbapi.tracker.StartTracker` and  :meth:`~mdbapi.tracker.StopTracker`.
    * The **Tracker Interface** class (:class:`~mdbapi.tracker.TrackerInterface`) providing an interface to interact with the Tracker thread. The interaction with the thread can happen in several threads simultaneously.
    * The **Tracker Database** (:class:`~lib.db.trackerdb.TrackerDatabase`) that stores the tracked song relations.

To use the tracker, start the Tracker Thread by calling :meth:`~mdbapi.tracker.StartTracker` once. 
Now it is possible to access the randomizer using the :class:`~mdbapi.tracker.TrackerInterface` class. 
This can be done from multiple different threads.
When the tracker is not needed anymore, it can be stopped by calling :meth:`~mdbapi.tracker.StopTracker`.

Example:

    .. code-block:: python

        # Dependencies 
        cfg = MusicDBConfig("./musicdb.ini")

        # Start the Tracker
        StartTracker(cfg)

        # Use Tracker (Can be anywhere in the code)
        tracker = TrackerInterface()
        tracker.NewSong("Unicorn/2000 - Honey Horn/13 Rainbow Song.mp3")
        tracker.NewSong("Truther/2013 - Real Album/23 Illuminati.mp3")
        tracker.SongSkipped()

        # Stop Tracker
        StopTracker()

"""

import logging
import time
from threading          import Thread
from lib.db.musicdb     import MusicDatabase
from lib.db.trackerdb   import TrackerDatabase

RUN      = False
THREAD   = None
CMDQUEUE = []
CMD_NEWSONG     = 1
CMD_SONGSKIPPED = 2
CMD_CLEAR       = 3

# Tracks the time between two songs added
LastTimeStamp = time.time()


def StartTracker(config):
    """
    Start the Tracker thread.
    You should use this function instead of calling the TrackerThread directly.

    Args:
        config: a MusicDB config object

    Returns:
        ``None`` if something went wrong, otherwise the thread-handler will be returned
    """
    global THREAD
    if THREAD != None:
        logging.warning("Tracker already running")
        return None

    global RUN
    RUN    = True
    THREAD = Thread(target=TrackerThread, args=(config,))
    THREAD.start()

    return THREAD


def StopTracker():
    """
    Stops the Tracker thread.
    This function is blocking and waits until the thread is closed.

    Returns:
        ``None``
    """
    global RUN
    global THREAD
    RUN = False

    if THREAD:
        THREAD.join()
    else:
        logging.debug("There is no Thread to stop!")

    THREAD = None
    return None


def TrackerThread(config):
    """
    .. warning::

        This function should not be called directly. Use :meth:`~mdbapi.tracker.StartTracker` to execute the Thread!

    This thread tracks songs that were played after each other.
    So it gets tracked what songs the user put together into the queue because their style fit to each other.
    It will also track randomly added songs assuming the user skips songs that don't fit.
    Only completely played songs were considered.
    Skipped songs get ignored.

    The thread runs in three stages until :meth:`~mdbapi.tracker.StopTracker` gets called.

    **Check for new command**

    First a new command gets popped from the command queue.
    An entry in the command queue is a tuple of the command itself and one argument.
    If there is no new command, the thread sleeps for a configured time and checks again.

    **Check for a relationship**

    If there was a command in the queue it gets executed.
    The command influences the state of the tracker internal playlist.

    The intern playlist holds up to three entries. Each is a relative path to a played or playing song.
    So the first and second (index 0 and index 1) have a connection that will be tracked.
    As list:

        #. The song that was fully played before the last song
        #. The last song that was played completely
        #. The current playing song
    
    The following commands exist:

    CMD_NEWSONG:
        Set by the method :meth:`~mdbapi.tracker.TrackerInterface.NewSong`.
        This signals that MPD (Music Playing Daemon) started playing a new file.
        The path to the file is the argument to this command.
        If the last song added to the playlist already exist, it gets ignored.

    CMD_SONGSKIPPED:
        Set by the method :meth:`~mdbapi.tracker.TrackerInterface.SongSkipped`.
        This command signals that the current song was skipped and so the first entry (index 0)
        gets removed from the internal playlist.

    CMD_CLEAR:
        Set by the method :meth:`~mdbapi.tracker.TrackerInterface.NewSong`.
        If the time between two songs more than 30 minutes, the relation gets rejected.
        The internal playlist gets emptied and a new "session" can start.


    **Store relationship into database**

    The third step is to check for a new relation between two songs.
    This is the case if there are three entries in the internal playlist.
    If there are less, or if the tracker was disabled by the configuration, 
    nothing will be done and the control flow goes back to the first step - reading a new command.

    If there are three entries in the queue, the song IDs get determined.
    Then the relation gets added to the tracker database by calling :meth:`lib.db.tracker.TrackerDatabase.AddEdge`

    Args:
        config: MusicDB Configuration
    """
    # Read some settings
    disabled      = config.debug.disabletracker
    musicdbpath   = config.database.path
    trackerdbpath = config.tracker.dbpath
    pollinterval  = config.tracker.interval

    global RUN
    global CMDQUEUE

    # Open databases
    if not disabled:
        musicdb   = MusicDatabase(musicdbpath)
        trackerdb = TrackerDatabase(trackerdbpath)

    # Enter main loop
    playlist = []
    while RUN:
            # check if there is a new command, otherwise sleep
            if len(CMDQUEUE) == 0:
                time.sleep(pollinterval)
                continue

            # Get command and argument
            (cmd, arg) = CMDQUEUE.pop(0)

            # Process command
            if cmd == CMD_NEWSONG:
                # check if the previous song is the same one
                if len(playlist) > 0:
                    if playlist[-1] != arg:
                        playlist.append(arg)
                    else:
                        logging.debug("The new song to track \"%s\" is the same as the previous one - so it gets ignored", arg)
                else:
                    playlist.append(arg)

            elif cmd == CMD_SONGSKIPPED:
                if len(playlist) > 0:
                    playlist.pop()

            elif cmd == CMD_CLEAR:
                playlist = []

            # check if we got a new relation (two songs played completely - implies that a 3rd one is currently running)
            if len(playlist) < 3:
                continue

            song0Path = playlist.pop(0)
            song1Path = playlist[0]     # do not remove this song, now its just the successor

            if disabled:
                # do not do anything further when database accesses are permitted
                continue

            # Translate songpath to songid
            try:
                songa       = musicdb.GetSongByPath(song0Path)
                songb       = musicdb.GetSongByPath(song1Path)
                songida     = songa["id"]
                songidb     = songb["id"]
                artistida   = songa["artistid"]
                artistidb   = songb["artistid"]
            except Exception as e:
                logging.error("musicdb.GetSongByPath failed with error \"%s\"!", str(e))
                continue

            # store relation
            try:
                trackerdb.AddRelation("song",   songida,   songidb)
                trackerdb.AddRelation("artist", artistida, artistidb)
            except Exception as e:
                logging.error("trackerdb.AddEdge failed with error \"%s\"!", str(e))
                continue



class TrackerInterface(object):
    """
    Interface to the :meth:`~mdbapi.tracker.TrackerThread`.
    This class is made to access the thread form all over the code simultaneously.
    """
    def __init__(self):
        pass



    # A command is a tuple of the command ID and ONE argument
    def PushCMD(self, command, argument=None):
        """
        This method pushes a new command into the command queue that gets processed by the Tracker thread.
        This method is supposed to be only called from a method inside the Tracker class.
        You should not call this method directly.

        If the Tracker is not running, nothing happens and ``False`` gets returned

        Args:
            command: One of the commands that can be processed by the Tracker
            argument: Optional argument for a command

        Returns:
            ``None``
        """
        global CMDQUEUE
        global RUN
        
        if not RUN:
            logging.warning("Tracker is not running. Command will be ignored.")
            return False

        CMDQUEUE.append((command, argument))
        return True



    def NewSong(self, songpath):
        """
        This method adds a new song to the list of song tracked.

        If the time between this song, and the previous one exceeds 30 minutes, it gets ignored and the internal state gets reset.
        So the chain of songs get cut if the time between playing them is too long.
        The chain of songs gets also cut, if *songpath* is ``None`` or ``""``.

        Args:
            songpath: relative song path of the song that gets currently played.

        Returns:
            ``True`` on success. ``False`` in case an error occurred.
        """
        # Check argument (A situation where songpath was None leads to chaos.)
        if not songpath:
            self.PushCMD(CMD_CLEAR)    # avoid tracking wrong relations
            logging.warning("Songpath of new song is of type None! \033[0;33m(Ignoring the NewSong-Call)")
            return False

        # Get timestamp
        global LastTimeStamp
        timestamp = time.time()

        # If there is a 30 Minute gap, do not associate this song with the previous -> clear list
        if int(timestamp - LastTimeStamp) > 30*60:
            logging.debug("Clear tracker history because of a 30 minute gap.")
            self.PushCMD(CMD_CLEAR)

        LastTimeStamp = timestamp
        logging.debug("Track new song: %s", songpath)
        self.PushCMD(CMD_NEWSONG, songpath)
        return True



    # The playing song was skipped (undo NewSong-Call - ONCE)
    def SongSkipped(self):
        """
        This method signals the tracker that the last added song (via :meth:`~.mdbapi.tracker.TrackerInterface.NewSong`) was skipped.

        Returns:
            ``None``
        """
        self.PushCMD(CMD_SONGSKIPPED)
        logging.debug("Last tracked song was skipped")
        return None


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

