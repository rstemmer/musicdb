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
This module implements the stream that streams the music.
This module provides a thread that takes the songs from a :class:`mdbapi.songqueue.SongQueue` to stream them via Icecast.
It manages the connection to the Icecast server using the :mod:`lib.stream.icecast` module.
Further more this module provides some callback interfaces to inform the rest of MusicDB about the state of the stream.

So this module consist of the following parts:

    * The `Streaming Thread`_ that manages the Song Stream.
    * An `Event Management`_ that provides a callback interface to get updated about what's going on in the Streaming Thread.
    * The :class:`~StreamManager` that does management behind streaming.


Interface
---------

This module maintains a global state!
All functions work on the settings in the :class:`~lib.cfg.musicdb.MusicDBConfig` configuration object and the internal state of this module.

There are two functions and one class that are available to manage the Stream:

    .. code-block:: python

        from mdbapi.stream import StartStreamingThread, StopStreamingThread, StreamManager


    * :meth:`~StartStreamingThread` starts the Streaming Thread that manages the streaming. It also establishes a connection to the Icecast server.
    * :meth:`~StopStreamingThread` disconnects MusicDB from Icecast and stops the Streaming Thread
    * :class:`~StreamManager` is the class to manage the Stream.


Streaming Thread
----------------

The Streaming Thread mainly manages sending mp3-file chunks to the Icecast server.
This thread is the point where the music managed by MusicDB gets handed over to Icecast so the user can listen to it.

The :class:`~StreamManager` communicates with the :meth:`~StreamingThread` with a `Command Queue`_.

More details are in the :meth:`~StreamingThread` description.

The thread maintains a global dictionary that holds the state of the thread - The **Stream State**.
It can be accessed via :meth:`mdbapi.stream.StreamManager.GetStreamState`.
This will only be updated by the StreamingThread.
It contains the following information:

    * ``isconnected`` (bool): ``True`` when connected to Icecast, otherwise ``False``
    * ``isplaying`` (bool): ``True`` when streaming, otherwise ``False``


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

Functions that get called must provide two parameters.
The first is a string that provides the name of the event as described below.
The second parameter contains an event specific argument, or ``None``.

A return value gets not handled.

The following events exist:

    StatusChanged:
        Gets triggered when the connection status to Icecast or the play status changed.

    TimeChanged:
        The time of the current playing position of a song changed.
        Argument is the current playtime of the song in seconds.

Example:

    This example shows how to use the callback interface:

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
from mdbapi.songqueue      import SongQueue
from mdbapi.randy       import Randy


Config          = None
Thread          = None
Callbacks       = []
RunThread       = False
CommandQueue    = []
State           = {}



#####################################################################
# Streaming Thread                                                  #
#####################################################################


def StartStreamingThread(config, musicdb):
    """
    This function starts the Streaming Thread :mod:`~StreamingThread`.
    You should use this function instead of calling the Streaming Thread function directly.

    By calling this function, the global state of this module gets reset.
    This included removing all commands from the Command Queue.

    Args:
        config: :class:`~lib.cfg.musicdb.MusicDBConfig` object holding the MusicDB Configuration
        database: A :class:`~lib.db.musicdb.MusicDatabase` instance

    Returns:
        ``True`` on Success, otherwise ``False``

    Raises:
        TypeError: When the arguments are not of the correct type.
    """
    global Config
    global Thread
    global RunThread
    global Callbacks
    global CommandQueue
    global State

    if Thread != None:
        logging.warning("Streaming Thread already running")
        return False

    if type(config) != MusicDBConfig:
        raise TypeError("config argument not of type MusicDBConfig")
    if type(musicdb) != MusicDatabase:
        raise TypeError("database argument not of type MusicDatabase")

    logging.debug("Initialize Streaming environment")
    Config       = config
    Callbacks    = []
    CommandQueue = []
    State        = {"isconnected": False, "isplaying": False}

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

    if Thread == None:
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

    The thread tracks the played song using the :doc:`/mdbapi/tracker` module.
    It also tracks randomly added songs assuming the user skips or removes songs that don't fit.
    Only completely played songs will be considered.
    Skipped songs will be ignored.

    The thread triggers the following events:

        * ``StatusChanged``: When the play-state
        * ``TimeChanged``: To update the current streaming progress of a song

    The ``TimeChanged`` event gets triggered approximately every second.
    """
    from lib.stream.icecast import IcecastInterface
    from mdbapi.tracker     import Tracker

    global Config
    global RunThread
    global CommandQueue
    global State

    # Create all interfaces that are needed by this Thread
    musicdb = MusicDatabase(Config.database.path)
    tracker = Tracker(Config, musicdb)
    filesystem = Filesystem(Config.music.path)
    queue   = SongQueue(Config, musicdb)
    randy   = Randy(Config, musicdb)
    icecast = IcecastInterface(
            port      = Config.icecast.port,
            user      = Config.icecast.user,
            password  = Config.icecast.password,
            mountname = Config.icecast.mountname
            )
    icecast.Mute()

    while RunThread:
        # Sleep a bit to reduce the load on the CPU. If disconnected, sleep a bit longer
        if State["isconnected"]:
            time.sleep(0.1)
        else:
            time.sleep(2)

        # Check connection to Icecast, and connect if disconnected.
        isconnected = icecast.IsConnected()
        if State["isconnected"] != isconnected:
            State["isconnected"] = isconnected
            Event_StatusChanged()

        if not isconnected:
            # Try to connect, and check if connection succeeded in the next turn of the main loop
            logging.info("Trying to reconnect to Icecast…")
            icecast.Connect()
            continue


        # Get current song that shall be streamed.
        currententryid, currentsongid = queue.CurrentSong()
        if currententryid == None:
            logging.info("Waiting for 5s to try to get a new song to play.")
            time.sleep(5)
            continue

        mdbsong  = musicdb.GetSongById(currentsongid)
        songpath = filesystem.AbsolutePath(mdbsong["path"])


        # Stream song
        icecast.UpdateTitle(mdbsong["path"])
        logging.debug("Start streaming %s", songpath)
        timeplayed    = 0
        lasttimestamp = time.time()
        for frameinfo in icecast.StreamFile(songpath):
            # Send every second the estimated time position of the song.
            if not frameinfo["muted"]:
                timeplayed += frameinfo["header"]["frametime"]
            timestamp   = time.time()
            timediff    = timestamp - lasttimestamp;
            if timediff >= 1.0:
                Event_TimeChanged(timeplayed/1000)
                lasttimestamp = timestamp

            # Check if the thread shall be exit
            if not RunThread:
                break

            # read and handle queue commands if there is one
            if len(CommandQueue) == 0:
                continue

            command, argument = CommandQueue.pop(0)
            if command == "PlayNextSong":
                logging.debug("Playing next song")
                break   # Stop streaming current song, and start the next one

            elif command == "Play":
                logging.debug("Setting Play-State to %s", str(argument))
                State["isplaying"] = argument
                icecast.Mute(not State["isplaying"])    # Mute stream, when not playing
                Event_StatusChanged()
        else:
            # when the for loop streaming the current song gets not left via break,
            # then the whole song was streamed. So add that song to the trackers list
            # Also update the last time played information.
            # In case the loop ended because Icecast failed, update the Status
            if icecast.IsConnected():
                tracker.AddSong(currentsongid)
                if not Config.debug.disablestats:
                    musicdb.UpdateSongStatistic(currentsongid, "lastplayed", int(time.time()))
            else:
                icecast.Mute()
                State["isplaying"]   = False
                State["isconnected"] = False
                Event_StatusChanged()

        # Current song completely streamed. Get next one.
        # When the song was stopped to shutdown the server, do not skip to the next one
        # In case the loop stopped because of an Icecast error, stay at the last song.
        if RunThread and icecast.IsConnected():
            queue.NextSong()



#####################################################################
# Event Management                                                  #
#####################################################################



def Event_StatusChanged():
    """
    See :meth:`~TriggerEvent` with event name ``"StatusChanged"``
    More details in the module description at the top of this document.
    """
    TriggerEvent("StatusChanged")

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
            logging.exception("A Stream Thread event callback function crashed!")



#####################################################################
# Stream Manager Class                                              #
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

        Never call the :meth:`mdbapi.songqueue.SongQueue.NextSong` method directly from this class!
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

        self.db         = database
        self.cfg        = config
        self.songqueue  = SongQueue(self.cfg, self.db)



    def PushCommand(self, command, argument=None):
        """
        Class internal interface to the `Command Queue`_ used to communicate with the :meth:`StreamingThread`.
        You should not access the queue directly, because the Streaming Thread expects valid data inside the queue.
        This is guaranteed by the methods that use this method.

        Args:
            command (str): A command to the Streaming Thread. Valid commands are listed in the :meth:`StreamingThread` section of the documentation.
            argument: An argument to the command.

        Returns:
            ``True`` on success, ``False`` when the Streaming Thread is not running.
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



    def GetStreamState(self):
        """
        This method returns the current state of the Streaming Thread as a dictionary.

        Returns:
            A copy of the Stream state. See the top of the documentation for details of the Stream State.
        """
        global State
        return dict(State)




    #####################################################################
    # Callback Function Management                                      #
    #####################################################################



    def RegisterCallback(self, function):
        """
        Register a callback function that reacts on Streaming related events.
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
            logging.warning("A Streaming Thread callback function should be removed, but did not exist in the list of callback functions!")
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

        When the command got successful executed, 
        the :meth:`~mdbapi.stream.StreamingThread` will trigger the ``StatusChanged`` event.

        Args:
            play (bool): Playstate the Streaming Thread shall get

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



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

