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
This module implements the interface between MusicDB and MPD (Music Playing Daemon).
It is not designed as class due to the fact that MusicDB shall only have one single connection to the daemon.

Interface
---------

For clean code, this module shall be imported in its namespace.
Connecting to MPD can looke like the following example:

    .. code-block:: python

        import mdbapi.mpd as mpd

        mpd.StartMPDClient(mdbconfig)

This module maintains a global state!
All functions work on the settings in the :class:`~lib.cfg.musicdb.MusicDBConfig` configuration object and the internal state of this module.

:meth:`~mdbapi.mpd.StartMPDClient` also executes :meth:`~mdbapi.mpd.StartObserver`

Observer Thread
---------------

The observer thread polls MPD to get its current state.
On certain event callback functions get triggered.
Furthermore, in some situation the :doc:`/mdbapi/tracker` gets updated.

The observer consists of the following methods:

    * :meth:`~mdbapi.mpd.StartObserver` - This method should only be called indirect via :meth:`~mdbapi.mpd.StartMPDClient`
    * :meth:`~mdbapi.mpd.StopObserver`
    * :meth:`~mdbapi.mpd.ObserverThread` - This thread should never be called directly.

Callbacks
---------

This module provided a callback interface to react on events triggered by MPD.

    * :meth:`~mdbapi.mpd.RegisterCallback`
    * :meth:`~mdbapi.mpd.RemoveCallback`

Functions that get called must provide two parameters.
The first is a string that provides the name of the event as described below.
The second parameter contains an event specitic information, or ``None``.

The following events exist:

    QueueChanged:
        Gets triggered when the MPD song queue changes

    StatusChanded:
        Gets triggered when MPDs status changes. Not the status of the internal state of this module!

    SongChanged:
        When the current playing song changes.

    TimeChanged:
        The time of the current playing position of a song changed.
        Argument is the current playtime of the song.


Managing MPD
------------

The following functions can be used to get and manage the state of MPD.

    * :meth:`~mdbapi.mpd.Play`
    * :meth:`~mdbapi.mpd.PlayNextSong`
    * :meth:`~mdbapi.mpd.GetConnectionState`
    * :meth:`~mdbapi.mpd.GetPlayingState`
    * :meth:`~mdbapi.mpd.GetStatus`
    * :meth:`~mdbapi.mpd.Update`
        
Queue management
----------------

To manage the queue that gets internally used by MPD, the following functions can be used:

    * :meth:`~mdbapi.mpd.GetQueue`
    * :meth:`~mdbapi.mpd.GetCurrentSong`
    * :meth:`~mdbapi.mpd.AddSong`
    * :meth:`~mdbapi.mpd.RemoveSong`
    * :meth:`~mdbapi.mpd.MoveSong`

"""

import time
import logging
import threading
from mpd            import MPDClient, MPDError, CommandError, ConnectionError
from mdbapi.tracker import TrackerInterface

Config      = None
Thread      = None
Tracker     = None
Interface   = None
Callbacks   = []

# State
IsConnected     = False
IsPlaying       = False
IsReconnecting  = False


def StartMPDClient(config):
    """
    This function initializes the MPD environment.
    At the end, it tries to connect to MPD.

    If there is already a connection to MPD, nothing will be done.

    Args:
        config: :class:`~lib.cfg.musicdb.MusicDBConfig` object

    Returns:
        ``True`` on Success, otherwise ``False``
    """
    global IsConnected
    global IsReconnecting

    if IsConnected or IsReconnecting:
        logging.warning("There is already a connection to the MPD!")
        return False

    global Config
    global Tracker
    global Interface

    logging.debug("Initialize MPD Client environment")
    Config      = config
    Tracker     = TrackerInterface()
    Interface   = MPDClient()

    logging.debug("Connect to MPD")
    retval = Connect()
    if retval == False:
        return False

    logging.debug("Update MPDs database")
    Update()

    logging.debug("Start MPD observer thread")
    StartObserver(config)
    return True



#####################################################################
# Observer Management                                               #
#####################################################################



def StartObserver(config):
    """
    Start the MPD Observer thread.
    You should use this function instead of calling the ObserverThread directly.

    Args:
        config: a MusicDB config object

    Returns:
        ``None`` if something went wrong, otherwise the thread-handler will be returned
    """
    global Thread
    if Thread != None:
        logging.warning("MPD Observer already running")
        return None

    Thread = threading.Thread(target=ObserverThread)
    Thread.start()

    return Thread



def StopObserver():
    """
    Stops the MPD Observer thread.
    This function is blocking and waits until the thread is closed.
    If there is a connection to MPD, this function also disconnects.

    Returns:
        ``None``
    """
    global IsConnected
    global IsReconnecting

    if IsReconnecting:
        logging.debug("Currently reconnecting to MPD. Waiting until reconnection is done.")
        while IsReconnecting:
            pass

    if IsConnected:
        logging.debug("There is a connection to the MPD! - Disconnect.")
        Disconnect()

    logging.debug("Waiting for Observer Thread to stop…")
    global Thread
    if Thread:
        Thread.join()
    else:
        logging.debug("There is no Thread to stop!")
    Thread = None
    logging.debug("MPD Interface shut down.")
    return None



def ObserverThread():
    """
    This thread observes the state of MPD.
    On special events it triggers the callback functions registered via :meth:`~mdbapi.mpd.RegisterCallback``.

    The threads main loop does the following things:

        #. Get current state from MPD
        #. Check if the current playing song changed
        #. Check if the queue changed
        #. Call callbacks. At least the ``"TimeChanged"`` event occurred

    In case the queue reaches its end, and the *End of Queue* event set in the MusicDB State is ``"add"``, a new random song gets added to the queue.

    This thread ends if the connection state to MPD is ``False`` and the reconnecting-state is ``False``.
    """
    from mdbapi.server      import mdbstate
    from mdbapi.randy       import RandyInterface

    global IsReconnecting
    global IsConnected
    global IsPlaying
    global Tracker
    global Config

    interval = Config.mpd.interval
    randy    = RandyInterface()
    lastsong = GetCurrentSong()
    if "file" not in lastsong:
        logging.warning("There was no \"file\"-entry in the initial song state! \033[1;30m(Setting to None)")
        # create a dummy entry to avoid problems
        lastsong["file"] = None

    lasttimestamp = time.time()
    while IsConnected or IsReconnecting:

        # Check if we got timing issues
        timestamp = time.time()
        timediff  = timestamp - lasttimestamp;
        if timediff > interval * 2.5:
            logging.warning("Pollingintervall exceeded time of %ss. Last iteration was %s ago!",
                    str(interval * 2.5),
                    str(timediff))
        lasttimestamp = timestamp

        # while reconnecting just wait and try again later
        if IsReconnecting:
            logging.debug("A reconnection is performed currently. Pollthread paused for %ds.", interval * 2)
            time.sleep(interval * 2)
            continue

        # Get the current state of MPD
        songchanged  = False
        queuechanged = False
        currentsong  = GetCurrentSong()
        status       = GetStatus()

        # Any data available?
        if currentsong == None or status == None:
            # on error just wait and try again later
            logging.warning("No new data from MPD! \033[1;30m(trying again in %ds)", interval * 2)
            time.sleep(interval * 2)
            continue

        # is the queue empty?
        if "file" not in currentsong:
            logging.warning("There was no \"file\"-entry in the current song dict.! \033[1;30m(Assuming MPDs Queue run empty)")
            IsPlaying           = False     # mpd goes into Pause mode if the queue is empty
            currentsong["file"] = None
            songchanged         = True      # mpd changed its state (to pause, queue is empty)
            queuechanged        = True      # Queue is empty now

        # If this song is different from the past one, notify the clients and track the change
        if currentsong["file"] != lastsong["file"]:
            lastsong     = currentsong
            songchanged  = True     # New song
            queuechanged = True     # First entry removed from queue
            if Tracker:
                Tracker.NewSong(currentsong["file"])

        # Check queue - add a random song if just one entry left
        queuelength = int(status["playlistlength"])
        if queuelength < 2 and mdbstate.queue.eoqevent == "add":
            randy.AddSong("last")
            queuechanged = False    # AddSong already trigger a queue-update-event!

        # Update if there are updates :)
        if songchanged:
            Event_SongChanged()
        if queuechanged:
            Event_QueueChanged()

        # Get time the current song was played to update a clients timers
        # This event became mandatory so send every interfall a TimeChanged event.
        # Even if no time passed
        if "elapsed" in status:
            playtime = int(float(status["elapsed"]))
        else:
            logging.warning("There was no \"elapsed\"-entry in MPD-Status dict.! \033[1;30m(Setting to 0)")
            playtime = 0
        Event_TimeChanged(playtime)

        # Sleep to reduce load
        time.sleep(interval)

    logging.info("MPD polling stopped as intended.")
    return None



#####################################################################
# Connection Management                                             #
#####################################################################



def Connect():
    """
    This function connects to MPD.
    If it is already connected nothing happens.
    After connecting, the current status of MPD gets requested to initialize the playing-state.

    Returns:
        ``True`` on success, otherwise ``False``
    """
    global IsConnected
    global IsPlaying
    global Interface
    global Config

    # do nothing if still connected
    if IsConnected == True:
        logging.debug("Already connected to MPD")
        return True

    # Check if the config shall be changed
    host = Config.mpd.address
    port = Config.mpd.port

    # Try to connect
    logging.debug("Connecting to MPD at %s:%s", host, port)
    try:
        Interface.connect(host, port)
    except (ConnectionError, IOError) as e:
        logging.error("Connecting to MPD (%s:%s) failed with error: %s", host, port, str(e))
        return False

    IsConnected = True
    logging.debug("Connecting to MPD succeeded.")

    # Check if the Daemon is in playing mode
    mpdstatus = GetStatus()
    if mpdstatus["state"] == "play":
        IsPlaying = True

    return True



def Disconnect():
    """
    This function disconnects from MPD.
    After disconnecting, the global state gets updated.

    Returns:
        ``True`` on success, otherwise ``False``
    """
    global IsConnected
    global IsPlaying
    global Interface

    # if not connected, do not disconnect
    if IsConnected == False:
        logging.debug("Already disconnected to MPD")
        return True

    # first close
    logging.debug("Closing MPD connection…")
    try:
        Interface.close()
    except (MPDError, IOError) as e:
        logging.debug("Closing failed with error: %s (Can be ignored at this point)", str(e))

    # then disconnect
    logging.debug("Disconnecting form MPD…")
    try:
        Interface.disconnect()
    except (MPDError, IOError) as e:
        logging.debug("Disconnecting failed with error: %s (Can be ignored at this point)", str(e))
        Interface = MPDClient() # Lib-Documentation recommends to create a new object if disconnect fails

    # Update state
    #IsPlaying   = False    # TODO: Check if this is a good idea
    IsConnected = False
    logging.debug("Disconnecting from MPD complete.")
    return True



def Reconnect():
    """
    This function forces a reconnect to MPD.

    Returns:
        The connection state after reconnect. So if this value is ``False`` the process failed.
    """
    global IsReconnecting
    global IsConnected

    logging.debug("Initiating a reconnection to MPD")
    IsReconnecting = True
    Disconnect()
    if not Connect():
        logging.error("Reconnecting to MPD failed. Staying disconnected.")
    else:
        logging.debug("Reconnecting to MPD succeeded.")
    IsReconnecting = False
    return IsConnected



#####################################################################
# Callback Management                                               #
#####################################################################



def RegisterCallback(function):
    """
    Register a callback function that reacts on MPD related events.
    First parameter of the function is used for the event name, the second one for additional information.
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
        return

    try:
        Callbacks.remove(function)
    except Exception as e:
        logging.warning("Removing a MPD-callback function failed with error: %s!", str(e))



def Event_QueueChanged():
    """
    See :meth:`~mdbapi.mpd.TriggerEvent` with event name ``"QueueChanged"``
    """
    TriggerEvent("QueueChanged")

def Event_StatusChanged():
    """
    See :meth:`~mdbapi.mpd.TriggerEvent` with event name ``"StatusChanged"``
    """
    TriggerEvent("StatusChanged")

def Event_SongChanged():
    """
    See :meth:`~mdbapi.mpd.TriggerEvent` with event name ``"SongChanged"``
    """
    TriggerEvent("SongChanged")
def Event_TimeChanged(playtime):
    """
    See :meth:`~mdbapi.mpd.TriggerEvent` with event name ``"TimeChanged"`` and playtime of the song as argument
    """
    TriggerEvent("TimeChanged", playtime)

def TriggerEvent(name, arg=None):
    """
    This function triggers an event.
    It iterates through all registered callback functions and calls them.

    The arguments to the functions are the name of the even (*name*) and addition arguments (*arg*).
    That argument can also be ``None``.

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
            logging.exception("A MPD Event-Callback function crashed.")



#####################################################################
# MPD State Management                                              #
#####################################################################



def Play(play=True):
    """
    Set the play-state of MPD

    If *play* is ``True``, MPD gets set into *Play*-State.
    If *play* is ``False``, MPD gets set into *Pause*-State.

    This function is forcing the state. It does not care about the current playing state.

    After changing the state, the ``"StatusChanged"`` event gets triggered.

    Args:
        play (bool): Playstate MPD shall be set to

    Returns:
        ``True`` on success. ``False`` if an error occurres
    """
    global IsConnected
    global IsPlaying
    global Interface

    if IsConnected == False:
        logging.debug("Play(%s) called but there is no connection to MPD", str(play))
        return False

    try:
        if play:
            Interface.play()
            IsPlaying = True
        else:
            Interface.pause()
            IsPlaying = False
    except:
        logging.exception("Setting MPDs play/pause state failed! - Reconnecting…")
        Reconnect()
        return False

    Event_StatusChanged()
    return True



def PlayNextSong():
    """
    This function triggers MPD to play the next song in the queue.
    This only works if MPD is in playing state.

    When using this function, the Tracker gets informed that the current song got skipped.
    The rest (Queue changed, Song changed) gets handled by the observer.

    Returns:
        ``True`` on success, otherwise ``False``
    """
    global IsConnected
    global IsPlaying
    global Interface
    global Tracker

    if IsConnected == False:
        logging.warning("Cannot paly next song because there is no connection to mpd!")
        return False
    if IsPlaying == False:
        logging.warning("Cannot paly next song because mpd is paused.")
        return False

    try:
        Interface.next()
    except Exception as e:
        logging.error("Playing next song failed with error \"%s\"!", str(e))
        Reconnect()
        return False

    if Tracker:
        Tracker.SongSkipped()

    # The Observer-Thread will recognize that a new song gets played
    return True



def GetConnectionState():
    """
    This function returns the current connection state to MPD.

    In case of a reconnection, the state is ``False`` but may soon change to ``True``.

    Returns:
        ``True`` if connected, ``False`` if disconnected.
    """
    global IsConnected
    return IsConnected

def GetPlayingState():
    """
    Get the playing-state as stored by this client. (It may, but should not, differ from the MPDs play state)

    Returns:
        ``True`` when playing a song. When paused ``False`` gets returned.
    """
    global IsPlaying
    return IsPlaying



def GetStatus():
    """
    This function returns the current status of MPD as dictionary.

    The status dictionary has the following keys. Each value behind a key is a string.

        .. code-block:: python

            {
            'nextsongid':       '2', 
            'bitrate':          '0', 
            'elapsed':          '293.418', 
            'playlist':         '2', 
            'single':           '0', 
            'repeat':           '1', 
            'songid':           '1', 
            'mixrampdb':        '0.000000', 
            'volume':           '-1', 
            'audio':            '44100:f:2', 
            'song':             '0', 
            'state':            'pause', 
            'time':             '293:339', 
            'random':           '0', 
            'playlistlength':   '5', 
            'nextsong':         '1', 
            'consume':          '1'
            }

    Returns:
        The current status of MPD, or ``None`` if not connected
    """
    global IsConnected
    global Interface

    if IsConnected == False:
        logging.debug("There is no connection to MPD!")
        return None
    
    try:
        status = Interface.status()
    except Exception as e:
        logging.error("Getting MPD status failed with error \"%s\"!", str(e))
        Reconnect()
        return None

    return status



def Update():
    """
    This function forces MPD to update its database.
    Whenever there were songs added to the music database, the MPDs database should be updated, too.

    Returns:
       ``True`` on success, otherwise ``False``
    """
    global IsConnected
    global Interface

    if IsConnected == False:
        logging.warning("Cannot update MPD database because there is no connection to mpd!")
        return False

    try:
        Interface.update()
    except CommandError as e:
        logging.warning("MPDs database update failed with error \"%s\"!", str(e))
        return False
    except ConnectionError as e:
        logging.warning("MPDs database update failed with error \"%s\"!", str(e))
        logging.warning("  Start mpd and run update manually!")
        return False

    return True



#####################################################################
# Queue and Song Management                                         #
#####################################################################



def GetQueue():
    """
    This function returns the current queue MPD holds as list of songs.
    If an error occurres or there is no connection to MPD, ``None`` gets returned

    The paths are relative to the music root directory. 

    .. warning::

        The returned paths depends on the MPD Configuration.
        Make sure ``music_directory`` is the same path that MusicDB uses as music root directory.

    Returns:
        A list of relative song paths representing MPDs queue.
        ``None`` in case of an error.
    """

    global IsConnected
    global Interface

    if IsConnected == False:
        logging.debug("There is no connection to MPD!")
        return None
    
    try:
        playlist = Interface.playlist()
    except Exception as e:
        logging.error("Getting playlist from MPD failed with error \"%s\"! (Reconnecting …)", str(e))
        Reconnect()
        return None

    paths = []
    for entry in playlist:
        if entry[:6] == "file: ":
            entry = entry[6:]
        paths.append(entry)

    return paths



def GetCurrentSong():
    """
    This function returns the current song MPD is playing (or paused at) as dictionary.

    This song dictionary has nothing in common with a MDBSong dictionary as read from the music database.
    The song dictionary has the following keys. Each value behind a key is a string.

        .. code-block:: python

            {
           'track':         '18/20', 
           'genre':         'Rock', 
           'title':         'Mein Blut (Carlos Perón Neumischung)', 
           'time':          '339', 
           'last-modified': '2015-11-29T12:50:08Z', 
           'date':          '2004-06-22T00:00:00Z', 
           'album':         'Eisbrecher - Deluxe Edition', 
           'file':          'Eisbrecher/2004 - Eisbrecher - Deluxe Edition/18 Mein Blut (Carlos Perón Neumischung).m4a', 
           'composer':      'Pix, Noel / Wesselsky, A.', 
           'pos':           '0', 
           'artist':        'Eisbrecher', 
           'disc':          '1/1', 
           'id':            '1'
            }

    Returns:
        The song currently playing by MPD, or ``None`` if something gets wrong.
    """
    global IsConnected
    global Interface

    if IsConnected == False:
        logging.debug("There is no connection to MPD!")
        return None

    try:
        song = Interface.currentsong()
    except Exception as e:
        logging.error("Get current song from MPD failed with error \"%s\"! (Reconnecting …)", str(e))
        Reconnect()
        return None

    return song



def AddSong(path, position="last"):
    """
    This function adds a new song to MPDs queue.
    The path must be relative to the music root directory as stored in the music database.

    .. warning::

        The path to the song is relative to the music root director.
        Make sure ``music_directory`` in the MPD configuration file is the same path MusicDB uses as music root directory.

    After adding the song, the Queue Changed event gets triggered

    Args:
        path (str): relative path to the song.
        position (str): Position in the queue. ``"next"`` to add next to the current song, ``"last"`` to add the song at the end of the queue.

    Returns:
        ``True`` on success, otherwise ``False``
    """
    global IsConnected
    global Interface

    if IsConnected == False:
        logging.warning("Cannot add song into the mpd-queue because there is no connection to mpd!")
        return False
    if type(path) != str:
        logging.error("Invalid type of the path-variable that shall be added to the mpd-queue! \033[0;33m(Ignoring this AddSong-Command)")
        return False

    logging.debug("Adding song \"%s\" (\"%s\") into the mpd-queue", path, position)

    try:
        if position == "last":
            Interface.add(path)
        elif position == "next":
            Interface.addid(path, 1)
        else:
            logging.warning("Song cannot be added to an unknown position. %s not in {\"next\", \"last\"}.", position)
    except CommandError as e:
        logging.warning("Adding song \033[1;35m%s\033[1;33m (\"%s\") failed with error \"\033[1;31m%s\033[1;33m\"", path, position, str(e))
        return False

    Event_QueueChanged()
    return True



# position is the song-number in the playlist.
def RemoveSong(position):
    """
    This function removes a song from the queue.

    On success, the Queue Changed event gets triggered.

    Args:
        position (int): Position of the song in the Queue. Must be ``1`` or greater.

    Returns:
        ``True`` on success, otherwise ``False``
    """
    global IsConnected
    global Interface

    if IsConnected == False:
        logging.warning("Cannot remove song because there is no connection to mpd!")
        return False

    try:
        position = int(position)
    except:
        logging.error("Position must be an integer!")
        return False

    if position < 1:
        logging.warning("Position must be greater than 0!")
        return False

    try:
        Interface.delete((position, position+1))
    except CommandError as e:
        logging.warning("Removing MPDs queue entries (from %i, to %i) failed with error \"%s\"!", position, position+1, str(e))
        return False

    Event_QueueChanged()
    return True



def MoveSong(posfrom, posto):
    """
    This function moves a song from one position in the queue to another.

    On success, the Queue Changed event gets triggered.

    Args:
        posfrom (int): The position of the song that shall be moved (must be greater than ``0``)
        posto (int): The new position of the song (must be greater than ``0``)

    Returns:
        ``True`` on success, otherwise ``False``
    """
    global IsConnected
    global Interface

    if IsConnected == False:
        logging.warning("Cannot move songs because there is no connection to mpd!")
        return False

    try:
        posfrom = int(posfrom)
        posto   = int(posto)
    except:
        logging.error("Position must be an integer!")
        return False

    if posfrom < 1 or posto < 1:
        logging.warning("Position must be greater than 0!")
        return False

    if posfrom == posto:
        return True

    try:
        Interface.move(posfrom, posto)
    except CommandError as e:
        # ignore failed moves… ok, give a warning :)
        logging.warning("Moving MPD queue entry (from %i, to %i) failed with error \"%s\"!", posfrom, posto, str(e))
        return False

    Event_QueueChanged()
    return True



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

