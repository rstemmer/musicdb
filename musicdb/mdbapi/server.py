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
This is the main module to run the MusicDB Server.

To start and run the server, the following sequence of function calls is necessary:

    .. code-block:: python

        Initialize(mdbconfig, musicdatabase)
        StartWebSocketServer()
        Run()


This module maintain global instances of the following classes.
Those objects can be used inside the thread the server runs. 
Usually the main thread.
Using these objects saves a lot of memory.
If the server is not started, the objects are all ``None``.

    * :class:`musicdb.lib.db.musicdb.MusicDatabase` as ``database``
    * :class:`musicdb.mdbapi.mise.MusicDBMicroSearchEngine` as ``mise``
    * :class:`musicdb.lib.cfg.musicdb.MusicDBConfig` as ``cfg``

"""

import traceback
import random
import time
import signal
from musicdb.lib.cfg.musicdb    import MusicDBConfig
from musicdb.lib.db.musicdb     import MusicDatabase
from musicdb.lib.filesystem     import Filesystem
from musicdb.lib.ws.server      import MusicDBWebSocketServer
from musicdb.mdbapi.mise        import MusicDBMicroSearchEngine
from musicdb.mdbapi.audiostream import StartAudioStreamingThread, StopAudioStreamingThread
from musicdb.mdbapi.videostream import StartVideoStreamingThread, StopVideoStreamingThread
from musicdb.taskmanagement.managementthread    import StartTaskManagementThread, StopTaskManagementThread
import logging

# Global objects
# This is the server environment that needs to be accessed by many objects
# Instances
database    = None  # music.db object
mise        = None  # micro search engine object
cfg         = None  # overall configuration file
# WS Server
tlswsserver = None
shutdown    = False


def SendSignalToServer(signum):
    """
    .. warning::

        This method requires root privileges!

    This method can be used by any MusicDB module to send a signal to the MusicDB server.
    The signals are listen in the `Python Signal Module <https://docs.python.org/3/library/signal.html>`_.

    .. Example:

        .. code-block:: python

            import signal
            from musicdb.mdbapi.server import SendSignal

            SendSignalToServer(signal.SIGTERM)  # Trigger server to shut down

    The bash-equivalent of this call is:

    .. code-block:: bash

        systemctl kill -s $signum --kill-who=main musicdb.service

    Args:
        signum (Signals): A signal as listed in the `Python Signal Module <https://docs.python.org/3/library/signal.html>`_

    Returns:
        *Nothing*
    """
    fs = Filesystem()
    try:
        logging.debug("Sending signal %i to musicdb.service", signum)
        fs.Execute(["systemctl", "kill", "-s", str(signum), "--kill-who=main", "musicdb.service"])
    except ChildProcessError as e:
        logging.error("Sending signal %i to musicdb.service failed with error: %s", signum, str(e))
    return 



def SignalHandler(signum, stack):
    """
    This is the general signal handle for the MusicDB Server.
    This function reacts on system signals and calls the handler of a specific signal.

    Args:
        signum: signal number
        stack: current stack frame
    
    Returns: Nothing
    """
    if signum == signal.SIGTERM:
        logging.debug("Got signal TERM")
        SIGTERM_Handler()
    else:
        logging.warning("Got unexpected signal %s"%str(signum))


def UpdateCaches():
    """
    This function handles the signal to refresh the server cache.
    Its task is to trigger updating the servers cache and to inform the clients to update.

    On server side:
    
        * The MiSE Cache gets updated by calling :meth:`musicdb.mdbapi.mise.MusicDBMicroSearchEngine.UpdateCache`


    To inform the clients a broadcast packet get sent with the following content: ``{method:"broadcast", fncname:"sys:refresh", fncsig:"UpdateCaches", arguments:null, pass:null}``

    Example:

        .. code-block:: javascript

            if(fnc == "sys:refresh" && sig == "UpdateCaches") {
                MusicDB_Request("GetTags", "UpdateTagsCache");                  // Update tag cache
                MusicDB_Request("GetFilteredArtistsWithAlbums", "ShowArtists"); // Update artist view
            }
    """
    global mise
    global tlswsserver

    try:
        mise.UpdateCache()
    except Exception as e:
        logging.warning("Unexpected error updating MiSE cache: %s \033[0;33m(will be ignored)\033[0m", str(e))

    try:
        packet = {}
        packet["method"]      = "broadcast"
        packet["fncname"]     = "sys:refresh"
        packet["fncsig"]      = "UpdateCaches"
        packet["arguments"]   = None
        packet["pass"]        = None
        tlswsserver.factory.BroadcastPacket(packet)
    except Exception as e:
        logging.warning("Unexpected error broadcasting a tags-update: %s \033[0;33m(will be ignored)\033[0m", str(e))


def SIGTERM_Handler():
    """
    This function is the handler for the system signal TERM.
    It signals the server to shut down.
    """
    logging.info("\033[1;36mSIGTERM:\033[1;34m Initiate Shutdown …\033[0m")
    global shutdown
    shutdown = True



def Initialize(configobj, databaseobj):
    """
    This function initializes the whole server.
    It initializes lots of global objects that get shared between multiple connections.

    The following things happen when this method gets called:

        #. Assign the *configobj* and *databaseobj* to global variables ``cfg`` and ``database`` to share them between multiple connections
        #. Seed Python's random number generator
        #. Instantiate a global :meth:`musicdb.mdbapi.mise.MusicDBMicroSearchEngine` object
        #. Starting the upload, integration and import management via :meth:`musicdb.taskmanagement.managementthread.StartTaskManagementThread`
        #. Start the Audio Streaming Thread via :meth:`musicdb.mdbapi.audiostream.StartAudioStreamingThread` (see :doc:`/mdbapi/audiostream` for details)
        #. Start the Video Streaming Thread via :meth:`musicdb.mdbapi.videostream.StartVideoStreamingThread` (see :doc:`/mdbapi/audiostream` for details)
        #. Update MiSE cache via :meth:`musicdb.mdbapi.mise.MusicDBMicroSearchEngine.UpdateCache`

    Args:
        configobj: :class:`~musicdb.lib.cfg.musicdb.MusicDBConfig` that gets shared between connections
        databaseobj: :class:`~musicdb.lib.db.musicdb.MusicDatabase` that gets shared between connections

    Returns:
        ``None``

    Raises:
        TypeError: When *configobj* is not of type :class:`~musicdb.lib.cfg.musicdb.MusicDBConfig`
        TypeError: When *databaseobj* is not of type :class:`~musicdb.lib.cfg.musicdb.MusicDatabase`
    """

    global cfg
    global database
    if type(configobj) != MusicDBConfig:
        logging.critical("Config-class of unknown type!")
        raise TypeError("configobj must be a valid MusicDBConfig object!")
    if type(databaseobj) != MusicDatabase:
        logging.critical("Database-class of unknown type!")
        raise TypeError("databaseobj must be a valid MusicDatabase object")

    cfg      = configobj
    database = databaseobj

    random.seed()

    # Initialize all interfaces
    logging.debug("Initializing MicroSearchEngine…")
    global mise
    mise   = MusicDBMicroSearchEngine(cfg)

    logging.debug("Starting Task Management…")
    StartTaskManagementThread(cfg, database)

    # Start/Connect all interfaces
    logging.debug("Starting Streaming Thread…")
    StartAudioStreamingThread(cfg, database)
    StartVideoStreamingThread(cfg, database)
    
    logging.debug("Updating MiSE Cache…")
    mise.UpdateCache()
    
    # Signal Handler
    signal.signal(signal.SIGTERM, SignalHandler)
    signal.signal(signal.SIGUSR1, SignalHandler)

    return None



def StartWebSocketServer():
    """
    This function creates and starts the actual MusicDB Websocket Server.

    Returns:
        ``True`` on success, otherwise ``False``
    """
    global tlswsserver
    tlswsserver = MusicDBWebSocketServer()
    
    retval = tlswsserver.Setup(
            cfg.websocket.bind,
            cfg.websocket.port,
            cfg.websocket.cert,
            cfg.websocket.key)
    if retval == False:
        logging.critical("Setup for websocket server failed!")
        return False

    retval = tlswsserver.Start()
    if retval == False:
        logging.critical("Starting websocket server failed!")
        return False

    return True



def Shutdown():
    """
    This function stops the server and all its dependent threads.

    The following things happen when this function gets called:

        #. Stopping task management via :meth:`musicdb.taskmanagement.managementthread.StopTaskManagementThread`
        #. Stop the Audio Streaming Thread via :meth:`musicdb.mdbapi.audiostream.StopAudioStreamingThread`
        #. Stop the Video Streaming Thread via :meth:`musicdb.mdbapi.videostream.StopVideoStreamingThread`
        #. Stop the websocket server

    At the end, the program gets terminated. So, this function gets never left.
    
    The exit code will be ``0`` if this was a regular shutdown.
    If the shutdown got forced, for example due to a critical error, the exit code is ``1``.

    This function should also be called when :meth:`~musicdb.mdbapi.server.Initialize` fails or when it raises an exception.
    """
    logging.info("Shutting down MusicDB-Server")
    global tlswsserver

    if tlswsserver:
        logging.debug("Disconnect from clients…")
        tlswsserver.factory.CloseConnections()
    
    logging.debug("Stopping Task Management Thread…")
    StopTaskManagementThread()

    logging.debug("Stopping Streaming Threads…")
    StopAudioStreamingThread()
    StopVideoStreamingThread()
    
    if tlswsserver:
        logging.debug("Stopping TLS WS Server…")
        tlswsserver.Stop()

    # dead end
    global shutdown
    if shutdown:
        exit(0)
    else:
        exit(1)



def Run():
    """
    This is the servers main loop.

    Inside the loop all MusicDB Websocket Server events get handled by calling :meth:`musicdb.lib.ws.server.MusicDBWebSocketServer.HandleEvents`.
    When a shutdown gets triggered the :meth:`~mdbapi.server.Shutdown` function gets called and the server stops.

    The :meth:`~musicdb.mdbapi.server.Shutdown` gets also called the user presses *Ctrl-C* This leads to a regular shutdown.

    In as an exception occurs the :meth:`~musicdb.mdbapi.server.Shutdown` gets called, too. In this case the exit-code will be ``1``.
    """
    logging.info("Setup complete. \033[1;37mExecuting server.\033[1;34m")
    # enter event loop
    global tlswsserver
    if not tlswsserver:
        logging.critical("TLS Websocket Server was not started!")
        return

    try:

        global shutdown
        while True:
            tlswsserver.HandleEvents()
            
            if shutdown:
                Shutdown()

            time.sleep(.1)  # Avoid high CPU load

    except KeyboardInterrupt:
        logging.warning("user initiated server shutdown");
        shutdown = True     # signal that this is a correct shutdown and no crash
        Shutdown()

    except Exception as e:
        logging.critical("FATAL ERROR (shutting down server!!):");
        logging.critical(e)
        traceback.print_exc()
        Shutdown()

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

