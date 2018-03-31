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
This module implements the Song Queue management and stream. The soul of MusicDB.
This module provides a thread that takes the songs from a :class:`lib.songqueue.SongQueue` to stream them via Icecast.
It manages the connection to the Icecast server using the :mod:`lib.icecast` module.
Further more this module provides some callback interfaces to inform the rest of MusicDB about the state of the Song Queue.

So this module consist of the following parts:

    * The `Streaming Thread`_ that manages the Song Stream.
    * An `Event Management`_ that provides a callback interface to get updated about what's going on in the Streaming Thread.
    * The :class:`~StreamManager` that provides an interface to the Song Queue, and the management behind streaming the queue.


Interface
---------

This module maintains a global state!
All functions work on the settings in the :class:`~lib.cfg.musicdb.MusicDBConfig` configuration object and the internal state of this module.

There are two functions and one class that are available to manage the Song Queue and Stream:

    .. code-block:: python

        from mdbapi.stream import StartStreamingThread, StopStreamingThread, StreamManager


    * :meth:`~StartStreamingThread` starts the Streaming Thread that manages the streaming. It also establishes a connection to the Icecast server.
    * :meth:`~StopStreamingThread` disconnects MusicDB from Icecast and stops the Streaming Thread
    * :class:`~StreamManager` is the class to manage the Stream and the Song Queue.


Streaming Thread
----------------

The Streaming Thread mainly manages sending mp3-file chunks to the Icecast server.
This thread is the point where the music managed by MusicDB gets handed over to Icecast so the user can listen to it.

Furthermore this thread does some Song Queue management like adding new random songs the queue when it runs empty.

The :class:`~StreamManager` communicates with the :meth:`~StreamingThread` with a `Command Queue`_.

More details are in the :meth:`~StreamingThread` description.


Command Queue
-------------

The Command Queue is a FIFO buffer of tuple.
Each tuple has a command name and an optional argument.
For the whole Module, there is only one global Command Queue.

Each instance of the :class:`~StreamManager` class writes into the same queue following the *First Come First Serve* (FCFS) protocol.
The :meth:`~StreamingThread` reads the command from that queue and processes them.

The following commands are available:

    ``Play`` (:meth:`StreamManager.Play`):
        If state is ``True`` the current song from the Song Queue gets streamed to Icecast.
        If state is ``False`` the audio stream gets paused.

    ``PlayNextSong`` (:meth:`StreamManager.PlayNextSong`):
        Stops streaming the current song, and starts with the next song.
        If streaming is paused, only the next song gets selected as new current song.


Event Management
----------------

This module provided a callback interface to react on events triggered by Streaming Thread or by actions done by the :class:`~StreamManager` class.

The following two functions can be used to register or remove a callback function:

    * :meth:`~StreamManager.RegisterCallback`
    * :meth:`~StreamManager.RemoveCallback`

TODO
Functions that get called must provide two parameters.
The first is a string that provides the name of the event as described below.
The second parameter contains an event specitic information, or ``None``.

A return value gets not handled.

The following events exist:

    QueueChanged:
        Gets triggered when the Song Queue changes

    StatusChanded:
        Gets triggered when the connection status to Icecast or the play status changed.

    SongChanged:
        When the current playing song changes.

    TimeChanged:
        The time of the current playing position of a song changed.
        Argument is the current playtime of the song.
        It is a rough estimation calculated from the position of the data in the file that gets streamed.

Example:

    .. code-block:: python

        def callback(name, arg):
            print("Event \"%s\" occurred with argument \"%s\"." % (name, str(arg)))

        sq = StreamManager(mdbconfig, musicdatabase)
        sq.RegisterCallback(callback)

        # …

        sq.RemoveCallback(callback)

"""


import time
import logging
import threading
from lib.filesystem     import Filesystem
from lib.cfg.musicdb    import MusicDBConfig
from lib.db.musicdb     import MusicDatabase
from lib.songqueue      import SongQueue
from mdbapi.musiccache  import MusicCache


Config          = None
Thread          = None
Callbacks       = []
Songs           = None
RunThread       = False
CommandQueue    = []



#####################################################################
# Song Queue Management                                             #
#####################################################################


# TODO: store queue in mdbstate or in a special file
def StartStreamingThread(config):
    """
    This function starts the Streaming Thread :mod:`~StreamingThread`.
    You should use this function instead of calling the Streaming Thread function directly.

    By calling this function, the global state of this module gets reset.
    This included removing all commands from the Command Queue and creating a new Song Queue.

    Args:
        config: :class:`~lib.cfg.musicdb.MusicDBConfig` object holding the MusicDB Configuration

    Returns:
        ``True`` on Success, otherwise ``False``
    """
    global Config
    global Thread
    global RunThread
    global Songs
    global Callbacks
    global CommandQueue

    if Thread != None:
        logging.warning("Streaming Thread already running")
        return False

    logging.debug("Initialize Streaming environment")
    Config       = config
    Songs        = SongQueue()
    Callbacks    = []
    CommandQueue = []

    logging.debug("Starting Streaming Thread")
    RunThread = True
    Thread    = threading.Thread(target=StreamingThread)
    Thread.start()

    return True



def StopStreamingThread():
    """
    This function stops the Streaming Thread.
    The function is blocking and waits until the thread is closed.

    Returns:
        ``True`` on success, otherwise ``False``
    """
    global RunThread
    global Thread

    if Thread != None:
        logging.warning("There is no Streaming Thread running!")
        return False

    logging.debug("Waiting for Streaming Thread to stop…")

    RunThread = False
    Thread.join()
    Thread = None

    logging.debug("Streaming Thread shut down.")
    return True



def StreamingThread():
    """
    This thread manages the streaming of the songs from the Song Queue to the Icecast server.


    """
    # TODO: add details like what happens with the Tracker, are there any conditions or side effects?
    # TODO: This is a better place to set song stats!
    from lib.icecast        import IcecastInterface
    from mdbapi.server      import mdbstate
    from mdbapi.randy       import RandyInterface
    from mdbapi.tracker     import TrackerInterface

    global Config
    global RunThread
    global CommandQueue
    global Songs

    # Create all interfaces that are needed by this Thread
    randy   = RandyInterface()
    tracker = TrackerInterface()
    musicdb = MusicDatabase(Config.database.path)
    cache   = MusicCache(Config, musicdb)
    icecast = IcecastInterface(
            port      = Config.icecast.port,
            user      = Config.icecast.user,
            password  = Config.icecast.password,
            mountname = Config.icecast.mountname
            )

    while RunThread:
        # Check connection to Icecast, and connect if disconnected.
        if not icecast.IsConencted():
            icecast.Connect()

        # Get current song
        entryid, songid = Songs.CurrentSong()
        if not songid:
            logging.error("Song Queue run empty!")
            # TODO: Warten und wiederholen???
            continue

        mdbsong  = musicdb.GetSongById(songid)
        songpath = cache.GetSongPath(mdbsong, absolute=True)

        # Stream song
        for size, offset in icecast.StreamFile(songpath):

            # Send estimated time position of the song.
            # It's just how much of the file got read multiplied by total play time
            timeplayed = (offset / size) * mdbsong["playtime"]
            #Event_TimeChanged(timeplayed)   # TODO: This spams! - Only call every n times.

            # read and handle queue commands if there is one
            if len(CommandQueue) == 0:
                continue

            command, argument = CommandQueue.pop(0)
            if command == "PlayNextSong":
                # Stop streaming current song, and start the next one
                break
            elif comman == "Play":
                logging.error("Not Implemented Yet!")   # TODO

        # Current song completely streamed.
        # Get next song
        Songs.NextSong()





#####################################################################
# Event Management                                                  #
#####################################################################



def Event_QueueChanged():
    """
    See :meth:`~TriggerEvent` with event name ``"QueueChanged"``.
    More details in the module description at the top of this document.
    """
    TriggerEvent("QueueChanged")

def Event_StatusChanged():
    """
    See :meth:`~TriggerEvent` with event name ``"StatusChanged"``
    More details in the module description at the top of this document.
    """
    TriggerEvent("StatusChanged")

def Event_SongChanged():
    """
    See :meth:`~TriggerEvent` with event name ``"SongChanged"``
    More details in the module description at the top of this document.
    """
    TriggerEvent("SongChanged")

def Event_TimeChanged(playtime):
    """
    See :meth:`~TriggerEvent` with event name ``"TimeChanged"`` and playtime of the song as argument
    More details in the module description at the top of this document.
    """
    TriggerEvent("TimeChanged", playtime)

def TriggerEvent(name, arg=None):
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



#####################################################################
# Song Queue Interface Class                                        #
#####################################################################



class StreamManager(object):
    """
    This class provides an interface to the Streaming Thread (:meth:`~StreamingThread`) and the Song Queue that will be streamed.

    The communication is implemented with a command queue.
    More details about those commands can be found in the :meth:`StreamingThread` description.
    Anyway, the details of the command queue are not important to know.
    They get hide by this class.
    Only important thing to know is, that when multiple instances of this class are used, the actions follow the *First Come First Server* protocol.

    .. note::

        **Important for developer:**

        Never call the :meth:`lib.songqueue.SongQueue.NextSong` method directly from this class!
        Send the ``"PlayNextSong"`` command to the :meth:`StreamingThread` instead.
        The thread handles the skip to the next song and starts streaming the new file.

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

        self.db  = database
        self.cfg = config



    def PushCommand(self, command, argument=None):
        """
        Class internal interface to the `Command Queue`_ used to communicate with the :meth:`StreamingThread`.
        You should not access the queue directly, because the Song Queue Thread expects valid data inside the queue.
        This is guaranteed by the methods that use this method.

        Args:
            command (str): A command to the Song Queue Thread. Valid commands are listed in the :meth:`StreamingThread` section of the documentation.
            argument: An argument to the command.

        Returns:
            ``True`` on success, ``False`` when the Song Queue Thread is not running.
        """
        global RunThread
        global CommandQueue
        
        if not RunThread:
            logging.warning("Streaming Thread is not running! Command will be ignored.")
            return False

        if len(CommandQueue) > 25:
            logging.warning("The Streaming Thread Command Queue has an unusual length of %i entries. Did the thread hung up? \033[1;30m(This is only an information, nothing changes in the behavior of this method)", len(CommandQueue))

        CommandQueue.append((command, argument))
        return True



    #####################################################################
    # Callback Function Management                                      #
    #####################################################################



    def RegisterCallback(function):
        """
        Register a callback function that reacts on Song Queue or Streaming related events.
        For more details see the module description at the top of this document.

        Args:
            function: A function that shall be called on an event.

        Returns:
            *Nothing*
        """
        global Callbacks
        Callbacks.append(function)



    def RemoveCallback(function):
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



    #####################################################################
    # Queue Commands                                                    #
    #####################################################################



    def Play(self, play=True):
        """
        Set the play-state.

            * If ``play`` is ``True`` (default value), the Streaming Thread streams audio file data to Icecast.
            * If ``play`` is ``False``, the stream gets paused.

        This function is forcing the state. It does not care about the current playing state.

        Args:
            play (bool): Playstate MPD shall be set to

        Returns:
            ``True`` on success. When ``play`` is not a Boolean, ``False`` gets returned.
        """
        if type(play) != bool:
            logging.warning("Unexpected datatype %s of play-argument (expecting bool)! \033[1;30m(Command will be ignored)", str(type(play)))
            return False

        return self.PushCommand("Play", play)



    def PlayNextSong(self):
        """
        This function triggers the Streaming Thread to play the next song in the queue.

        Returns:
            ``True`` on success, otherwise ``False``
        """
        return self.PushCommand("PlayNextSong")



    def GetQueue(self):
        """
        This method returns the song queue.

        The queue is a list of tuple.
        The tuple holds the entry ID of the queue element, and song ID
        The entry ID is a `Version 4 Universally Unique Identifier (UUID)<https://en.wikipedia.org/wiki/Universally_unique_identifier#Version_4_(random)>`_ .

        Returns:
            The current song queue. ``None`` if there is no queue yet.

        Example:

            .. code-block::

                queue = manager.GetQueue()

                if not queue:
                    print("There are no songs in the queue")
                else:
                    for element in queue:
                        print("Element with ID %i holds the song with ID %i" % (element[0], element[1]))

        """
        global Songs
        if not Songs:
            logging.warning("There is no song queue loaded! \033[1;30m(Doing nothing)")
            return None

        queue = Songs.GetQueue()
        return queue



    def GetCurrentSongId(self):
        """
        Returns the Song ID of the current playing song.

        Returns:
            The Song ID of the current playing song. ``None`` if there is no manage queue yet.
        """
        global Songs
        if not Songs:
            logging.warning("There is no song queue loaded! \033[1;30m(Doing nothing)")
            return None

        songid = Songs.CurrentSong()[1]
        return songid



    def AddSong(self, song, position="last"):
        """
        With this method, a new song can be insert into the queue.

        The position in the queue, where the song gets insert can be changed by setting the ``position`` argument:

            * ``"last"`` (default): Appends the song at the end of the queue
            * ``"next"``: Inserts the song right after the current playing song.

        The ``song`` argument can be a song entry from the music database, or just the song ID (as integer)

        Args:
            song (int/dict): The song that shall be inserted into the queue
            position (str): Position where the song will be inserted

        Returns:
            ``True`` on success, ``False`` otherwise.

        """
        global Songs
        if not Songs:
            logging.warning("There is no song queue loaded! \033[1;30m(Doing nothing)")
            return False

        if not position in ["next", "last"]:
            logging.warning("Position must be \"next\" or \"last\". Given was the invalid value \"%s\". \033[1;30(Doing nothing)", str(position))
            return False

        if type(song) == dict:
            songid = mdbsong["id"]
        elif type(song) == int:
            songid = song
        else:
            logging.error("Type of song (%s) is invalid. An ID of type int or a database entry of type dict was expected. \033[1;30m(Song won\'t be added)", str(type(song)))

        Songs.AddSong(song, position)
        return True



    def RemoveSong(self, entryid):
        """
        Removes the entry with the ID ``entryid`` from the queue.
        Removing the current song is not allowed!
        Call :meth:`PlayNextSong` instead.

        Args:
            entryid (int): ID of the entry that shall be removed.

        Returns:
            ``True`` on success, ``False`` otherwise.
        """
        global Songs
        if not Songs:
            logging.warning("There is no song queue loaded! \033[1;30m(Doing nothing)")
            return False

        try:
            Songs.RemoveSong(entryid)
        except Exception as e:
            logging.warning("Removing song from the queue failed with error: %s", str(e))
            return False

        return True



    def MoveSong(self, entryid, afterid):
        """
        This method allows to move an entry to another position in the queue.
        The entry with the ID ``entryid`` gets moved behind an entry with the ID ``afterid``.

        Moving the first song is not allowed!

        Args:
            entryid (int): ID of the element to move
            afterid (int): The ID of the element, the moved element gets placed behind.

        Returns:
            ``True`` on success, ``False`` otherwise.
        """
        global Songs
        if not Songs:
            logging.warning("There is no song queue loaded! \033[1;30m(Doing nothing)")
            return False

        try:
            Songs.MoveSong(entryid, afterid)
        except Exception as e:
            logging.warning("Removing song from the queue failed with error: %s", str(e))
            return False

        return True



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

