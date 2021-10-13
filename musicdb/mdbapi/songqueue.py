# MusicDB,  a music manager with web-bases UI that focus on music.
# Copyright (C) 2018 - 2021  Ralf Stemmer <ralf.stemmer@gmx.net>
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

Queue Management
----------------

An entry in this queue is a dictionary having the following keys:

    entryid:
        An entry ID that is unique for all entries at any time.
        This UUID is a 128 bit integer.
    
    songid:
        A song ID as maintained by the :class:`~musicdb.lib.db.musicdb.MusicDatabase` class.

    israndom:
        A boolean value that is set to ``True`` when the song was added by :doc:`/mdbapi/randy`.


Some features of this queue are:

    * The entry ID is a `Version 4 Universally Unique Identifier (UUID) <https://en.wikipedia.org/wiki/Universally_unique_identifier#Version_4_(random)>`_ .
    * The current playing song is at index 0.
    * The songs remain in the queue until they got completely streamed.
    * This class is thread safe. So each method of the same instance can be called from different threads.
    * The queue is persistent. After restarting MusicDB, the queue is not lost.

Furthermore this module cooperates the Randy module (see: :doc:`/mdbapi/randy`)
When the queue runs empty, a new random song gets append to the queue.


Event Management
----------------

This module provided a callback interface to react on events triggered on changes in the Song Queue.

The following two functions can be used to register or remove a callback function:

    * :meth:`~SongQueue.RegisterCallback`
    * :meth:`~SongQueue.RemoveCallback`

Functions that get called must provide two parameters.
The first is a string that provides the name of the event as described below.
The second parameter contains an event specific argument, or ``None``.

A return value gets not handled.

The following events exist:

    SongQueueChanged:
        Gets triggered when the Song Queue changes

    SongChanged:
        When the current playing song changes.

Examples
--------

    The following example shows how the :meth:`~SongQueue.NextSong` method works:

    .. code-block:: python

        queue = SongQueue(mdbconfig, musicdatabase)
        queue.AddSong(7357)         # 7357 is a song ID
        queue.AddSong(1337)
        queue.AddSong(2342)

        print(queue.CurrentSong()["songid"])  # 7357
        print(queue.CurrentSong()["songid"])  # 7357
        print(queue.NextSong()["songid"])     # 1337
        print(queue.CurrentSong()["songid"])  # 1337

        queueentry = queue.CurrentSong()
        if queueentry["israndom"]:
            print("Entry %d is a randomly added song."%(queueentry["entryid"]))

"""

import uuid
import logging
import threading    # for RLock
from musicdb.lib.cfg.musicdb    import MusicDBConfig
from musicdb.lib.cfg.mdbstate   import MDBState
from musicdb.lib.db.musicdb     import MusicDatabase
from musicdb.mdbapi.randy       import Randy
from musicdb.mdbapi.blacklist   import BlacklistInterface

Queue     = None
QueueLock = threading.RLock()   # RLock allows nested calls. It locks only different threads.
Callbacks = []                  # For events like QueueChanged or SongChanged



class SongQueue(object):
    """
    This class implements a queue to manage songs to play.
    Whenever the queue changes, its data gets stored in the MusicDB State Directory

    When the constructor detects that there is no queue yet (not even an empty one),
    it tries to load the stored queue.
    If this fails, a new empty queue gets created.

    Args:
        config: :class:`~musicdb.lib.cfg.musicdb.MusicDBConfig` object holding the MusicDB Configuration
        database: A :class:`~musicdb.lib.db.musicdb.MusicDatabase` instance

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
        self.mdbstate   = MDBState(self.cfg.directories.state, self.db)
        self.blacklist  = BlacklistInterface(self.cfg, self.db)
        self.randy      = Randy(self.cfg, self.db)

        global Queue
        global QueueLock

        with QueueLock:
            if Queue == None:
                logging.debug("Loading Song Queue…")
                try:
                    self.Load()
                except Exception as e:
                    logging.warning("Loading song queue failed with error: %s. \033[1;30m(Creating an empty one)", str(e))
                    Queue = []



    #####################################################################
    # Event Management                                                  #
    #####################################################################



    def RegisterCallback(self, function):
        """
        Register a callback function that reacts on Song Queue related events.
        For more details see the module description at the top of this document.

        Args:
            function: A function that shall be called on an event.

        Returns:
            *Nothing*
        """
        global Callbacks
        Callbacks.append(function)



    def RemoveCallback(self, function):
        """
        Removes a function from the list of callback functions.

        Args:
            function: A function that shall be called removed.

        Returns:
            *Nothing*
        """
        global Callbacks

        # Not registered? Then do nothing.
        if not function in Callbacks:
            logging.warning("A Song Queue callback function should be removed, but did not exist in the list of callback functions!")
            return

        Callbacks.remove(function)



    def TriggerEvent(self, name, arg=None):
        """
        This function triggers an event.
        It iterates through all registered callback functions and calls them.

        The arguments to the functions are the name of the even (``name``) and addition arguments (``arg``).
        That argument will be ``None`` if there is no argument.

        More details about events can be found in the module description at the top of this document.

        Args:
            name (str): Name of the event
            arg: Additional arguments to the event, or ``None``

        Returns:
            *Nothing*
        """
        global Callbacks
        for callback in Callbacks:
            try:
                callback(name, arg)
            except Exception as e:
                logging.exception("A Song Queue event callback function crashed!")

    def Event_SongQueueChanged(self):
        """
        See :meth:`~TriggerEvent` with event name ``"SongQueueChanged"``.
        More details in the module description at the top of this document.

        This method also tries to save the queue into the MusicDB State Directory.
        """
        try:
            self.Save()
        except Exception as e:
            logging.warning("Saving the current song queue failed with error: %s. \033[1;30m(Continuing without saving)", str(e))
        self.TriggerEvent("SongQueueChanged")

    def Event_SongChanged(self):
        """
        See :meth:`~TriggerEvent` with event name ``"SongChanged"``
        More details in the module description at the top of this document.
        """
        self.TriggerEvent("SongChanged")



    #####################################################################
    # Queue Management                                                  #
    #####################################################################



    def Save(self):
        """
        Save the current queue into a csv file in the MusicDB State Directory.
        Therefor the :meth:`musicdb.lib.cfg.mdbstate.MDBState.SaveSongQueue` gets used.

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
        via :meth:`musicdb.lib.cfg.mdbstate.MDBState.LoadSongQueue`.

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
        In detail, it is a `Version 4 Universally Unique Identifier (UUID) <https://en.wikipedia.org/wiki/Universally_unique_identifier#Version_4_(random)>`_ .
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

        The method returns element 0 from the queue which is the current song that can be streamed or gets already streamed.
        The song shall remain in the queue until it got completely streamed.
        Then it can be removed by calling :meth:`~musicdb.mdbapi.songqueue.SongQueue.NextSong`.

        When the queue is empty, a new random song gets added.
        This is the exact same song that then will be returned by this method.
        If adding a new song fails, ``None`` gets returned.
        This method triggers the ``SongQueueChanged`` event when the queue was empty and a new random song got added.

        Returns:
            A dictionary as described in the module description

        Example:

            .. code-block:: python

                queue = SongQueue()

                # Queue will be empty after creating a SongQueue object
                entry = queue.CurrentSong()
                if entry:
                    print("Random SongID: %s" % (str(entry["songid"])))
                else
                    print("Queue is empty! - Adding random song failed!")

                # Adds two new song with ID 7357 and 1337. 
                # Then the current song is the first song added.
                queue.AddSong(7357)
                queue.AddSong(1337)
                entry = queue.CurrentSong()
                if entry:
                    print("SongID: %s" % (str(entry["songid"]))) # 7357
                else
                    # will not be reached because we explicitly added songs.
                    print("Queue is empty! - Adding random song failed!")

        """
        global Queue
        global QueueLock

        with QueueLock:
            # Empty Queue? Add a random song!
            if len(Queue) == 0:
                self.AddRandomSong()
                self.Event_SongQueueChanged()

            # Still empty (no random song found)? Then return None. Nothing to do…
            if len(Queue) == 0:
                logging.critical("Queue run empty! \033[1;30m(Check constraints for random song selection and check if there are songs at all)")
                return None

            # Select first song from queue
            entry = Queue[0]

        return entry



    def NextSong(self):
        """
        This method returns the next song in the queue.
        This entry will be the next current song.

        The method pops the last current element from the queue.
        Then the new element at position 0, the new current element, will be returned.

        If the queue is empty, ``None`` gets returned.

        .. warning::

            In context of streaming, this method may not be the one you want to call.
            This Method drops the current song and sets the next song on top of the queue.

            The stream will not notice this, so that it continues streaming the previous song. (See :doc:`/mdbapi/audiostream`).
            If you want to stream the next song, call :meth:`musicdb.mdbapi.audiostream.AudioStreamManager.PlayNextSong`.

            The :meth:`musicdb.mdbapi.audiostream.AudioStreamManager.PlayNextSong` then makes the Streaming Thread calling this method.

        This method triggers the ``SongChanged`` and ``SongQueueChanged`` event when the queue was not empty.
        The ``SongChanged`` event gets also triggered when there was no next song.

        When there is only one entry left in the queue - the current song - then a new one gets add via :meth:`AddRandomSong`

        Returns:
            The new current song entry in the queue as dictionary described in the module description

        Example:

            .. code-block:: python

                queue = SongQueue()

                # Adds two new song with ID 7357 and 1337. 
                queue.AddSong(7357)
                queue.AddSong(1337)
            
                entry = queue.CurrentSong()
                print("SongID: %s" % (str(entry["songid"]))) # 7357

                entry = queue.NextSong()
                print("SongID: %s" % (str(entry["songid"]))) # 1337
                entry = queue.CurrentSong()
                print("SongID: %s" % (str(entry["songid"]))) # 1337

        """
        global Queue
        global QueueLock

        with QueueLock:
            if len(Queue) == 0:
                return None

            # Get next song
            if len(Queue) == 1:
                Queue.pop(0)
                entry = None
            else:   # > 1
                Queue.pop(0)
                entry = Queue[0]

            # Make sure the queue never runs empty
            if len(Queue) < 2:
                self.AddRandomSong()

        self.Event_SongChanged()
        self.Event_SongQueueChanged()
        return entry



    def GetQueue(self):
        """
        This method returns a copy of the song queue.

        The queue is a list of dictionaries.
        The content of the dictionary is described in the description of this module.

        Returns:
            The current song queue. ``[None]`` if there is no queue yet.

        Example:

            .. code-block:: python

                queue = songqueue.GetQueue()

                if not queue:
                    print("There are no songs in the queue")
                else:
                    for entry in queue:
                        print("Element with ID %i holds the song with ID %i" 
                                % (entry["entryid"], entry["songid"]))

        """
        global Queue
        return list(Queue)



    def AddSong(self, songid, position="last", israndom=False):
        """
        With this method, a new song can be insert into the queue.

        The position in the queue, where the song gets insert can be changed by setting the ``position`` argument:

            * ``"last"`` (default): Appends the song at the end of the queue
            * ``"next"``: Inserts the song right after the current playing song.
            * *Integer*: Entry-ID after that the song shall be inserted.

        On success, this method triggers the ``SongQueueChanged`` event.

        When the song shall be put at the beginning of the queue, then it gets set to index 1 not index 0.
        So the current playing song (index 0) remains!

        The new song gets added to the :mod:`~musicdb.musicdb.mdbapi.blacklist` via :meth:`musicdb.mdbapi.blacklist.BlacklistInterface.AddSong`
        The method also triggers the ``SongQueueChanged`` event.

        Args:
            songid (int): The ID of the song that shall be added to the queue
            position (str/int): Defines the position where the song gets inserted
            israndom (bool): Defines whether the song is randomly selected or not

        Returns:
            The new Queue Entry ID as integer

        Raises:
            TypeError: When ``songid`` is not of type ``int``
        """
        if type(songid) != int:
            raise TypeError("Song ID must be an integer!")

        entryid = self.GenerateID()

        newentry = {}
        newentry["entryid"]  = entryid
        newentry["songid"]   = songid
        newentry["israndom"] = israndom

        global Queue
        global QueueLock

        with QueueLock:
            if position == "next":
                Queue.insert(1, newentry)

            elif position == "last":
                Queue.append(newentry)

            elif type(position) == int:
                for index, entry in enumerate(Queue):
                    if entry["entryid"] == position:
                        Queue.insert(index+1, newentry)
                        break;
                else:
                    logging.warning("Queue Entry ID %s does not exist. \033[1;30m(Doing nothing)", str(position))

            else:
                logging.warning("Position must have the value \"next\", \"last\" or an Queue Entry ID. Given was \"%s\". \033[1;30m(Doing nothing)", str(position))
                return

        # add to blacklist
        self.blacklist.AddSong(songid)

        self.Event_SongQueueChanged()
        return entryid



    def AddRandomSong(self, position="last", albumid=None):
        """
        This method adds a random song into the queue.

        The position in the queue, where the song gets insert can be changed by setting the ``position`` argument:

            * ``"last"`` (default): Appends the song at the end of the queue
            * ``"next"``: Inserts the song right after the current playing song.

        When there is an album ID, the randoms song gets selected from that album using :meth:`musicdb.mdbapi.randy.Randy.GetSongFromAlbum`.
        If the album ID is ``None``, the method :meth:`musicdb.mdbapi.randy.Randy.GetSong` will be used to get a random song from the activated genres.

        After selecting the random song, the :meth:`~AddSong` method gets used to insert the new song into the queue.
        If there is no song found by Randy, then nothing gets added to the queue and ``False`` will be returned.

        Args:
            position (str): Defines the position where the song gets inserted.
            albumid (int/NoneType): ID of the album from that the song will be selected, or ``None`` for selecting a song from the activated genres.

        Returns:
            ``True`` when a random song got added to the queue. Otherwise ``False``.

        Raises:
            TypeError: When one of the types of the arguments are not correct
        """
        if type(position) != str:
            raise TypeError("Position must be a string!")
        if albumid != None and type(albumid) != int:
            raise TypeError("Album ID must be an integer!")

        if albumid:
            mdbsong = self.randy.GetSongFromAlbum(albumid)
        else:
            mdbsong = self.randy.GetSong()

        if not mdbsong:
            return False

        self.AddSong(mdbsong["id"], position, israndom=True)
        return True



    def GetSong(self, entryid):
        """
        Returns the song ID of the entry addressed by the entry ID

        Args:
            entryid (int): ID of the entry that song ID shall be returned

        Returns:
            The song ID of the entry, or ``None`` if the entry does not exists

        Raises:
            TypeError: When ``entryid`` is not of type ``int``
        """
        if type(entryid) != int:
            raise TypeError("Entry ID must be an integer!")

        global Queue
        global QueueLock

        with QueueLock:
            for entry in Queue:
                if entry["entryid"] == entryid:
                    return entry["songid"]

        logging.debug("Cannot find the requested entry %s! \033[1;30m(Returning None)", str(entryid))
        return None



    def RemoveSong(self, entryid):
        """
        Removes the entry with the ID ``entryid`` from the queue.
        Removing the current song is not allowed!
        Call :meth:`~NextSong` instead.

        When there is only one entry left in the queue - the current song - then a new one gets add via :meth:`~AddRandomSong`

        On success, this method triggers the ``SongQueueChanged`` event.

        Args:
            entryid (int): Entry to remove

        Returns:
            ``True`` on success, otherwise ``False``

        Raises:
            TypeError: When ``entryid`` is not of type ``int``
        """
        if type(entryid) != int:
            raise TypeError("Entry ID must be an integer!")

        global Queue
        global QueueLock

        with QueueLock:
            if len(Queue) < 2:
                logging.warning("The queue has only %i element. There must be at least 2 entries to be able to remove one.", len(Queue))
                return False

            if Queue[0]["entryid"] == entryid:
                logging.warning("The entry ID addresses the current song. This entry cannot be removed!")
                return False

            Queue = [entry for entry in Queue if entry["entryid"] != entryid]

            # Make sure the queue never runs empty
            if len(Queue) < 2:
                self.AddRandomSong()

        self.Event_SongQueueChanged()
        return True



    def MoveSong(self, entryid, afterid):
        """
        This method moves an entry, addressed by ``entryid`` behind another entry addressed by ``afterid``.
        If both IDs are the same, the method returns immediately without doing anything.
        When ``entryid`` addresses the current song, the method returns with value ``False``

        On success, the method triggers the ``SongQueueChanged`` event.

        Args:
            entryid (int):
            afterid (int):

        Returns:
            ``True`` when the entry was moved, otherwise ``False``

        Raises:
            TypeError: When ``entryid`` or ``afterid`` is not of type int
        """
        if entryid == afterid:
            return False

        # First check, if everything is OK with the arguments
        if type(entryid) != int or type(afterid) != int:
            raise TypeError("Queue entry IDs must be of type int!")

        global Queue
        global QueueLock

        with QueueLock:
            if Queue[0]["entryid"] == entryid:
                logging.warning("The entry ID addresses the current song. This entry cannot be moved!")
                return False

            # Get Positions
            frompos = [pos for pos, entry in enumerate(Queue) if entry["entryid"] == entryid]
            topos   = [pos for pos, entry in enumerate(Queue) if entry["entryid"] == afterid]

            if not frompos:
                logging.warning("Cannot find element with entryid %i in the queue!\033[1;30m (Doing nothing)", entryid)
                return False
            if not topos:
                logging.warning("Cannot find element with afterid %i in the queue!\033[1;30m (Doing nothing)", afterid)
                return False

            frompos = frompos[0]
            topos   = topos[0]

            # When topos is behind frompos, decrement topos because if shifts one entry down due to popping the frompos-element from the list
            if topos < frompos:
                topos += 1

            # Move element
            entry = Queue.pop(frompos)
            Queue.insert(topos, entry)

        self.Event_SongQueueChanged()
        return True



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

