# MusicDB,  a music manager with web-bases UI that focus on music.
# Copyright (C) 2018  Ralf Stemmer <ralf.stemmer@gmx.net>
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
This module implements the Song Queue.
The song queue consists of a global FIFO organized list.

    .. warning::

        When calling this method, the :meth:`mdbapi.stream.StreamingThread` will never know that the current song changed!
        In context of the stream, always use the :class:`mdbapi.stream.StreamManager` methods!

Example:

    .. code-block:: python

        queue = SongQueue()
        queue.AddSong(7357)         # 7357 is a song ID
        queue.AddSong(1337)
        queue.AddSong(2342)

        print(queue.CurrentSong())  # (*UUID*, 7357)
        print(queue.CurrentSong())  # (*UUID*, 7357)
        print(queue.NextSong())     # (*UUID*, 1337)
        print(queue.CurrentSong())  # (*UUID*, 1337)
"""

import uuid
import logging
import threading    # for RLock
from lib.cfg.musicdb    import MusicDBConfig
from lib.cfg.mdbstate   import MDBState
from lib.db.musicdb     import MusicDatabase

Queue     = []
QueueLock = threading.RLock() # RLock allows nested calls. It locks only different threads.

class SongQueue(object):
    """
    This class implements a queue to manage songs to play.

    An entry this queue is a tuple of an entry ID and a song ID as maintained by the :class:`~lib.db.musicdb.MusicDatabase` class.

    Some features of this queue are:

        * The entry ID is a `Version 4 Universally Unique Identifier (UUID)<https://en.wikipedia.org/wiki/Universally_unique_identifier#Version_4_(random)>`_ .
        * The current playing song is at index 0.
        * This class is thread safe. So each method of the same instance can be called from different threads.

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
        self.lock       = threading.Lock()



    def Save(self):
        """
        Save the current queue into a csv file in the MusicDB State Directory.
        Therefor the :meth:`lib.cfg.mdbstate.MDBState.SaveSongQueue` gets used.

        Returns:
            *Nothing*
        """
        global Queue
        global QueueLock

        with QueueLock:
            self.mdbstate.SaveSongQueue(Queue)

    def Load(self):
        """
        This method loads the last stored song queue for the MusicDB State Directory
        via :meth:`lib.cfg.mdbstate.MDBState.LoadSongQueue`.

        Returns:
            *Nothing*
        """
        global Queue
        global QueueLock

        with QueueLock:
            Queue = self.mdbstate.LoadSongQueue()



    def GenerateID(self):
        """
        This method generate a unique ID.
        In detail, it is a `Version 4 Universally Unique Identifier (UUID)<https://en.wikipedia.org/wiki/Universally_unique_identifier#Version_4_(random)>`_ .
        It will be returned as an integer.

        This method is build for the internal use in this class.

        Returns:
            A UUID to be used as entry ID

        Example:

            .. code-block:: python

                queue = SongQueue()
                uuid  = GenerateID()
                print(type(uuid))   # int
        """
        return uuid.uuid4().int



    def CurrentSong(self):
        """
        This method returns the current song in the queue.

        The method returns element 0 from the queue.

        If the queue is empty, ``(None, None)`` gets returned.

        Returns:
            A tuple (entryid, mdbsong).

        Example:

            .. code-block:: python

                queue = SongQueue()

                # Queue will be empty after creating a SongQueue object
                entryid, songid = queue.CurrentSong()
                print("SongID: %s" % (str(songid))) # None

                # Adds two new song with ID 7357 and 1337. 
                # Then the current song is the first song added.
                queue.AddSong(7357)
                queue.AddSong(1337)
                entryid, songid = queue.CurrentSong()
                print("SongID: %s" % (str(songid))) # 7357

        """
        global Queue
        global QueueLock

        with QueueLock:
            if len(Queue) > 0:
                entry = Queue[0]
            else:
                entry = (None, None)

        return entry



    def NextSong(self):
        """
        This method returns the next song in the queue.
        This entry will be the next current song.

        The method pops the last current element from the queue.
        Then the new element at position 0, the new current element, will be returned.

        If the queue is empty, ``(None, None)`` gets returned.

        Returns:
            A tuple (entryid, mdbsong).

        Example:

            .. code-block:: python
                queue = SongQueue()

                # Adds two new song with ID 7357 and 1337. 
                queue.AddSong(7357)
                queue.AddSong(1337)
            
                entryid, songid = queue.CurrentSong()
                print("SongID: %s" % (str(songid))) # 7357

                entryid, songid = queue.NextSong()
                print("SongID: %s" % (str(songid))) # 1337
                entryid, songid = queue.CurrentSong()
                print("SongID: %s" % (str(songid))) # 1337

        """
        global Queue
        global QueueLock

        with QueueLock:
            if len(Queue) == 0:
                return (None, None)

            # Get next song
            if len(Queue) == 1:
                Queue.pop(0)
                entry = (None, None)
            else:   # > 1
                Queue.pop(0)
                entry = Queue[0]

        return entry



    def GetQueue(self):
        """
        This method returns a copy of the queue.
        Each entry is a tuple of the entry ID and a song ID.

        Returns:
            A copy of the current queue

        Example:

            .. code-block:: python

                songs = queue.GetQueue()
                for entryid, songid in songs:
                    print("%i: %i" % (entryid, songid))

        """
        global Queue
        return list(Queue)



    def AddSong(self, songid, position="last", randomsong=False):
        """
        Adds a song at the end of the queue (``position="last"``) or to the beginning of the queue (``position="next"``).

        When the song shall be put at the beginning of the queue, then it gets set to index 1 not index 0.
        So the current playing song (index 0) remains!

        Args:
            mdbsong (int): The song that shall be added to the queue
            position (str): Defines the position where the song gets inserted.

        Returns:
            *Nothing*

        Raises:
            TypeError: When ``songid`` is not of type ``int``
        """
        if type(songid) != int:
            raise TypeError("Song ID must be an integer!")

        entryid = self.GenerateID()

        global Queue
        global QueueLock

        with QueueLock:
            if position == "next":
                Queue.insert(1, (entryid, songid))
            elif position == "last":
                Queue.append((entryid, songid))
            else:
                logging.warning("Position must have the value \"next\" or \"last\". Given was \"%s\". \033[1;30m(Doing nothing)", str(position))
                return



    def GetSong(self, entryid):
        """
        Returns the song ID of the entry addressed by the entry ID

        Args:
            entryid (int): ID of the entry that song ID shall be returnd

        Returns:
            The song ID of the entry, or ``None`` if the entry does not exists

        Raises:
            TypeError: When ``entryid`` is not of type ``int``
        """
        if type(entryid) != int:
            raise TypeError("Song must be an integer!")

        global Queue
        global QueueLock

        with QueueLock:
            for eid, songid in Queue:
                if eid == entryid:
                    return songid

        logging.debug("Cannot find the requested entry %s! \033[1;30m(Returning None)", str(entryid))
        return None



    def RemoveSong(self, entryid):
        """
        Removes an entry from the queue.
        The entry gets identified by its entry ID.

        You cannot remove the entry at index 0.
        If the entry ID addresses the current song, a value error exception gets raised.
        To remove the current song, call :meth:`~NextSong`.

        Args:
            entryid (int): Entry to remove

        Returns:
            *Nothing*

        Raises:
            TypeError: When ``entryid`` is not of type ``int``
        """
        if type(entryid) != int:
            raise TypeError("Song must be an integer!")

        global Queue
        global QueueLock

        with QueueLock:
            if len(Queue) < 2:
                logging.warning("The queue has only %i element. There must be at least 2 entries to be able to remove one.", len(Queue))
                return

            if Queue[0][0] == entryid:
                logging.warning("The entry ID addresses the current song. This entry cannot be removed!")
                return

            Queue = [entry for entry in Queue if entry[0] != entryid]



    def MoveSong(self, entryid, afterid):
        """
        This method moves an entry, addressed by ``entryid`` behind another entry addressed by ``afterid``.
        If both IDs are the same, the method returns immediately without doing anything.
        When ``entryid`` addresses the current song, then a value error exception gets raised.

        Args:
            entryid (int):
            afterid (int):

        Returns:
            *Nothing*

        Raises:
            TypeError: When ``entryid`` or ``afterid`` is not of type int
        """
        if entryid == afterid:
            return

        # First check, if everything is OK with the arguments
        if type(entryid) != int or type(afterid) != int:
            raise TypeError("Queue entry IDs must be of type int!")

        global Queue
        global QueueLock

        with QueueLock:
            if Queue[0][0] == entryid:
                logging.warning("The entry ID addresses the current song. This entry cannot be moved!")
                return

            # Get Positions
            frompos = [pos for pos, entry in enumerate(Queue) if entry[0] == entryid]
            topos   = [pos for pos, entry in enumerate(Queue) if entry[0] == afterid]

            if not frompos:
                logging.warning("Cannot find element with entryid %i in the queue!\033[1;30m (Doning nothing)", entryid)
                return
            if not topos:
                logging.warning("Cannot find element with afterid %i in the queue!\033[1;30m (Doning nothing)", afterid)
                return

            frompos = frompos[0]
            topos   = topos[0]

            # When topos is behind frompos, decrement topos because if shifts one entry down due to popping the frompos-element from the list
            if topos < frompos:
                topos += 1

            # Move element
            entry = Queue.pop(frompos)
            Queue.insert(topos, entry)



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

