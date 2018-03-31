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
This module implements the Song Queue.
The song queue consists of a FIFO organized list.

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
import threading    # for Lock

class SongQueue(object):
    """
    This class implements a queue to manage songs to play.

    An entry this queue is a tuple of an entry ID and a song ID as maintained by the :class:`~lib.db.musicdb.MusicDatabase` class.

    Some features of this queue are:

        * The entry ID is a `Version 4 Universally Unique Identifier (UUID)<https://en.wikipedia.org/wiki/Universally_unique_identifier#Version_4_(random)>`_ .
        * The current playing song is at index 0.
        * This class is thread safe. So each method of the same instance can be called from different threads.

    """
    def __init__(self):
        self.queue = []
        self.lock  = theading.Lock()



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
        with self.lock:
            if len(self.queue) > 0:
                entry = self.queue[0]
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
        with self.lock:
            if len(self.queue) > 1:
                self.queue.pop(0)
                entry = self.queue[0]
            elif len(self.queue) == 1:
                self.queue.pop(0)
                entry = (None, None)
            else:
                entry = (None, None)

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
        return list(self.queue)



    def AddSong(self, songid, position="last"):
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
            ValueError: When position is not ``"first"`` or ``"last"``
        """
        if type(songid) != int:
            raise TypeError("Song must be an integer!")

        entryid = self.GenerateID()

        with self.lock:
            if position == "first":
                self.queue.insert(1, (entryid, songid))
            elif position == "last":
                self.queue.append((entryid, songid))
            else:
                raise ValueError("Position must have the value \"first\" or \"last\". Given was \"%s\".", str(position))



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
            IndexError: When the length of the queue is less than 2. So there is no entry that can be removed
            ValueError: When ``entryid`` addresses the first element of the queue.
        """
        if type(entryid) != int:
            raise TypeError("Song must be an integer!")

        with self.lock:

            if len(self.queue) < 2:
                raise IndexError("The queue has only %i element. There must be at least 2 entries to be able to remove one.", len(self.queue))
            if self.queue[0][0] == entryid:
                raise ValueError("The entry ID addresses the current song. This entry cannot be removed!")
            self.queue = [entry for entry in self.queue if entry[0] != entryid]




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
            ValueError: When there is no element with ``entryid`` or ``afterid`` in the queue
            ValueError: When ``entryid`` addresses the current song
        """
        if entryid == afterid:
            return

        # First check, if everything is OK with the arguments
        if type(entryid) != int or type(afterid) != int:
            raise TypeError("Queue entry IDs must be of type int!")

        with self.lock:
            if self.queue[0][0] == entryid:
                raise ValueError("The entry ID addresses the current song. This entry cannot be removed!")

            # Get Positions
            frompos = [pos for pos, entry in enumerate(self.queue) if entry[0] == entryid]
            topos   = [pos for pos, entry in enumerate(self.queue) if entry[0] == afterid]

            if not frompos:
                raise ValueError("Cannot find element with entryid in the queue!")
            if not topos:
                raise ValueError("Cannot find element with afterid in the queue!")

            # When topos is behind frompos, decrement topos because if shifts one entry down due to popping the frompos-element from the list
            if topos > frompos:
                topos -= 1

            # Move element
            entry = self.queue.pop(position)
            self.queue.insert(afterid, entry)



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

