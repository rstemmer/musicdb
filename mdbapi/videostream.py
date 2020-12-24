# MusicDB,  a music manager with web-bases UI that focus on music.
# Copyright (C) 2020  Ralf Stemmer <ralf.stemmer@gmx.net>
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
This module implements the video stream that streams the music videos.
This module provides a thread that takes the videos from a :class:`mdbapi.videoqueue.VideoQueue` to stream them.


So this module consist of the following parts:

    * The `Streaming Thread`_ that manages the Video Stream.
    * An `Event Management`_ that provides a callback interface to get updated about what's going on in the Streaming Thread.
    * The :class:`~VideoStreamManager` that does management behind streaming.


Interface
---------

This module maintains a global state!
All functions work on the settings in the :class:`~lib.cfg.musicdb.MusicDBConfig` configuration object and the internal state of this module.

There are two functions and one class that are available to manage the Stream:

    .. code-block:: python

        from mdbapi.videostream import StartVideoStreamingThread, StopVideoStreamingThread, VideoStreamManager


    * :meth:`~StartVideoStreamingThread` starts the Streaming Thread that manages the streaming.
    * :meth:`~StopVideoStreamingThread` stops the Streaming Thread
    * :class:`~VideoStreamManager` is the class to manage the Stream.


Streaming Thread
----------------

The Streaming Thread mainly manages updating the queue based on played videos by the stream player (WebUI).
This thread is the point where the music managed by MusicDB gets handed over to the users web browser
so that the user can watch the video stream.

The :class:`~VideoStreamManager` communicates with the :meth:`~VideoStreamingThread` with a `Command Queue`_.

The thread maintains a global dictionary that holds the state of the thread - The **Stream State**.
It can be accessed via :meth:`mdbapi.videostream.VideoStreamManager.GetStreamState`.
This will only be updated by the VideoStreamingThread.
It contains the following information:

More details are in the :meth:`~VideoStreamingThread` description.


Command Queue
-------------

The Command Queue is a FIFO buffer of tuple.
Each tuple has a command name and an optional argument.
For the whole Module, there is only one global Command Queue.

Each instance of the :class:`~VideoStreamManager` class writes into the same queue following the *First Come First Serve* (FCFS) protocol.
The :meth:`~VideoStreamingThread` reads the command from that queue and processes them.

More details are in the :meth:`~VideoStreamingThread` description.


Event Management
----------------

This module provided a callback interface to react on events triggered by Streaming Thread or by actions done by the :class:`~VideoStreamManager` class.

The following two functions can be used to register or remove a callback function:

    * :meth:`~VideoStreamManager.RegisterCallback`
    * :meth:`~VideoStreamManager.RemoveCallback`

Functions that get called must provide two parameters.
The first is a string that provides the name of the event as described below.
The second parameter contains an event specific argument, or ``None``.

A return value gets not handled.

The following events exist:

    StatusChanged:
        Gets triggered when the status of the streaming thread changes.
        Internal states are excluded.

    StreamNextVideo:
        Informs the stream player to play the next video in the queue.
        The video to play is provided by the event as well.

More details are in the :meth:`~VideoStreamingThread` description.


Example:

    This example shows how to use the callback interface:

    .. code-block:: python

        def callback(name, arg):
            print("Event \"%s\" occurred with argument \"%s\"." % (name, str(arg)))

        videostream = VideoStreamManager(mdbconfig, musicdatabase)
        videostream.RegisterCallback(callback)

        # …

        videostream.RemoveCallback(callback)

"""


import time
import logging
import threading
from lib.cfg.musicdb    import MusicDBConfig
from lib.db.musicdb     import MusicDatabase
from mdbapi.videoqueue  import VideoQueue


Config          = None
Thread          = None
Callbacks       = []
RunThread       = False
CommandQueue    = []
State           = {}



#####################################################################
# Streaming Thread                                                  #
#####################################################################


def StartVideoStreamingThread(config, musicdb):
    """
    This function starts the Streaming Thread :mod:`~VideoStreamingThread`.
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
        logging.warning("Video Streaming Thread already running")
        return False

    if type(config) is not MusicDBConfig:
        raise TypeError("config argument not of type MusicDBConfig")
    if type(musicdb) is not MusicDatabase:
        raise TypeError("database argument not of type MusicDatabase")

    logging.debug("Initialize Video Streaming environment")
    Config       = config
    Callbacks    = []
    CommandQueue = []
    State        = {"isstreaming": False, "isplaying": False, "currententry": 0}

    logging.debug("Starting Video Streaming Thread")
    RunThread = True
    Thread    = threading.Thread(target=VideoStreamingThread)
    Thread.start()

    return True



def StopVideoStreamingThread():
    """
    This function stops the Streaming Thread.
    The function is blocking and waits until the thread is closed.

    Returns:
        ``True`` on success, otherwise ``False``
    """
    global RunThread
    global Thread

    if Thread == None:
        logging.warning("There is no Video Streaming Thread running!")
        return False

    logging.debug("Waiting for Video Streaming Thread to stop…")

    RunThread = False
    Thread.join()
    Thread = None

    logging.debug("Video Streaming Thread shut down.")
    return True



def VideoStreamingThread():
    """
    This thread manages the streaming of the videos from the Video Queue.

    The thread tracks the played video using the :doc:`/mdbapi/tracker` module.
    It does not track randomly added videos.
    Only completely played videos will be considered.
    Skipped videos will be ignored.
    It also maintains the ``lastplayed`` statistic.

    The thread triggers the following events:

        * ``StatusChanged``: When the stream state changed
        * ``StreamNextVideo``: When the player shall stream the next video. MDBVideo, streamstate and queue entry is included as rawdata argument.

    States

        * ``isstreaming``: This thread manages the queue and provides new videos when a video is considered being watched.
        * ``isplaying``: Stream is in a state where clients could play the current video. This is an assumption of the clients possible state. This does not represent the true clients state, and it is not meant to be used by the clients in any way.
        * ``currententry``: The queue entry ID of the current playing video.

    Commands:

        * ``VideoEnded``: When a client send the VideoEnded information to the server (:meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.VideoEnded` this thread manages the call. In case the provided entry ID is the same as the ``currententy`` ID the next video gets popped from the video queue. Otherwise the command gets ignored.
        * ``PlayNextVideo``: Skip the current video and start playing the next.
        * ``SetStreamState``: Sets the stream state to streaming or not streaming.

    When streaming gets deactivated, or activated, it also generates an event (``StatusChanged``).
    It is expected that all clients stop playing the current video if ``isstreaming`` is set to ``Flase``.
    In case it is set to ``True``, all clients that were used to play the videos continue playing the current video.
    """
    from mdbapi.tracker import VideoTracker

    global Config
    global RunThread
    global CommandQueue
    global State

    # Create all interfaces that are needed by this Thread
    musicdb = MusicDatabase(Config.database.path)
    tracker = VideoTracker(Config)
    queue   = VideoQueue(Config, musicdb)

    State["isplaying"]    = False
    State["isstreaming"]  = True
    queueentry = queue.CurrentVideo()
    if queueentry == None or queueentry["entryid"] == None:
        logging.info("Video Queue is empty, waiting for new video.")
    else:
        State["currententry"] = queueentry["entryid"]


    # Do nothing if video streaming is disabled
    if Config.debug.disablevideos:
        logging.warning("Video streaming disabled!")

        State["isplaying"]   = False
        State["isstreaming"] = False
        Event_StatusChanged()

        while RunThread:
            time.sleep(1)

        return


    while RunThread:
        # Sleep a bit to reduce the load on the CPU. If not in streaming , sleep a bit longer
        if State["isstreaming"]:
            time.sleep(0.1)
        else:
            time.sleep(2)

        # Check command
        if len(CommandQueue) == 0:
            continue
        command, argument = CommandQueue.pop(0)

        if command == "PlayNextVideo":      # Player pressed "Next" Button
            logging.debug("User forced next video")
            queue.NextVideo()
            State["isplaying"] = False

        elif command == "VideoEnded":    # Video was played to the end
            # If the currently streaming entry is different from the finished video
            # a different client may have already finished streaming the video and
            # requested the next video.
            # So nothing to do here anymore
            if State["currententry"] != argument:
                logging.debug("Ignoring VideoEnded command for %s. Current video is %s.", str(argument), str(State["currententry"]))
                continue

            logging.debug("Finished streaming video with queue entry id %i", argument)

            # Track video
            if not queueentry["israndom"]:  # do not track random videos
                try:
                    tracker.TrackVideo(queueentry["videoid"]);
                except Exception as e:
                    logging.exception("Trying to track video with ID %i failed with error \"%s\".",
                            queueentry["videoid"],
                                str(e))
            else:
                logging.debug("The played video was added by Randy. So it will not be tracked.")

            # Play next video
            queue.NextVideo()
            State["isplaying"] = False
            if not Config.debug.disablestats:
                musicdb.UpdateVideoStatistic(queueentry["videoid"], "lastplayed", int(time.time()))

        elif command == "SetStreamState":
            logging.debug("Setting Video Stream-State to %s", str(argument))
            State["isstreaming"] = argument
            Event_StatusChanged()


        # Stream next video, if clients finished streaming a video
        if State["isstreaming"] and not State["isplaying"]:
            # Get current video that shall be streamed.
            queueentry = queue.CurrentVideo()
            if queueentry == None or queueentry["entryid"] == None:
                logging.info("Video Queue is empty, waiting for new video.")
                continue

            State["isplaying"]    = True
            State["currententry"] = queueentry["entryid"]

            mdbvideo  = musicdb.GetVideoById(queueentry["videoid"])
            videoinfo = {}
            videoinfo["video"]       = mdbvideo
            videoinfo["queue"]       = dict(queueentry) # will be manipulated, so better make a copy
            videoinfo["queue"]["entryid"] = str(videoinfo["queue"]["entryid"]) # JavaScript cannot handle big integers
            videoinfo["streamstate"] = dict(State)
            videoinfo["streamstate"]["currententry"] = str(videoinfo["streamstate"]["currententry"])
            Event_StreamNextVideo(videoinfo)

    return




#####################################################################
# Event Management                                                  #
#####################################################################



def Event_StatusChanged():
    """
    See :meth:`~TriggerEvent` with event name ``"StatusChanged"``
    More details in the module description at the top of this document.
    """
    global State
    streamstate = dict(State)
    streamstate["currententry"] = str(streamstate["currententry"]) # JavaScript cannot handle big integers

    TriggerEvent("StatusChanged", streamstate)

def Event_StreamNextVideo(videoinfo):
    """
    See :meth:`~TriggerEvent` with event name ``"StreamNextVideo"`` and a path to the video as argument
    More details in the module description at the top of this document.
    """
    TriggerEvent("StreamNextVideo", videoinfo)

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



class VideoStreamManager(object):
    """
    This class provides an interface to the Streaming Thread (:meth:`~VideoStreamingThread`) and the Video Queue that will be streamed.

    The communication is implemented with a command queue.
    More details about those commands can be found in the :meth:`VideoStreamingThread` description.
    Anyway, the details of the command queue are not important to know.
    They get hide by this class.
    Only important thing to know is, that when multiple instances of this class are used, the actions follow the *First Come First Server* protocol.

    .. note::

        **Important for developer:**

        Never call the :meth:`mdbapi.videoqueue.VideoQueue.NextVideo` method directly from this class!
        Send the ``"PlayNextVideo"`` command to the :meth:`VideoStreamingThread` instead.
        The thread handles the skip to the next video and starts streaming the new file.

    Args:
        config: :class:`~lib.cfg.musicdb.MusicDBConfig` object holding the MusicDB Configuration
        database: A :class:`~lib.db.musicdb.MusicDatabase` instance

    Raises:
        TypeError: When the arguments are not of the correct type.
    """

    def __init__(self, config, database):
        if type(config) is not MusicDBConfig:
            raise TypeError("config argument not of type MusicDBConfig")
        if type(database) is not MusicDatabase:
            raise TypeError("database argument not of type MusicDatabase")

        self.db  = database
        self.cfg = config



    def PushCommand(self, command, argument=None):
        """
        Class internal interface to the `Command Queue`_ used to communicate with the :meth:`VideoStreamingThread`.
        You should not access the queue directly, because the Streaming Thread expects valid data inside the queue.
        This is guaranteed by the methods that use this method.

        Args:
            command (str): A command to the Streaming Thread. Valid commands are listed in the :meth:`VideoStreamingThread` section of the documentation.
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

            * If ``play`` is ``True`` (default value), the Streaming Thread streams data.
            * If ``play`` is ``False``, the audio stream gets paused.

        This function is forcing the state. It does not care about the current playing state.

        When the command got successful executed, 
        the :meth:`~mdbapi.videostream.VideoStreamingThread` will trigger the ``StatusChanged`` event.

        Args:
            play (bool): Playstate the Streaming Thread shall get

        Returns:
            ``True`` on success. When ``play`` is not a Boolean, ``False`` gets returned.
        """
        if type(play) is not bool:
            logging.warning("Unexpected datatype %s of play-argument (expecting bool)! \033[1;30m(Command will be ignored)", str(type(play)))
            return False

        return self.PushCommand("SetStreamState", play)



    def PlayNextVideo(self):
        """
        This function triggers the Streaming Thread to play the next video in the queue.

        Returns:
            ``True`` on success, otherwise ``False``
        """
        return self.PushCommand("PlayNextVideo")



    def VideoEnded(self, queueentryid):
        """
        This method informs the Streaming Thread the video was completely streams.
        It sets the ``lastplayed`` statistics of the video and
        triggers the Streaming Thread to play the next video in the queue.

        This method can be called multiple times for the same queue entry.

        Args:
            queueentryid (int): The ID of the queue entry that got finished streaming

        Returns:
            ``True`` on success, otherwise ``False``
        """
        return self.PushCommand("VideoEnded", queueentryid)



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

