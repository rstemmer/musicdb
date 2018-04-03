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
This is the main module to run the MusicDB Server.

To start and run the server, the following sequence of function calls is necessary:

    .. code-block:: python

        Initialize(mdbconfig, musicdatabase)
        StartWebSocketServer()
        Run()

When starting the server, a named pipe gets created at the path set in the configuration file.
MusicDB Server handles the following commands when written into its named pipe:

    * refresh:  :meth:`~mdbapi.server.UpdateCaches` - Update server caches and inform clients to update their caches
    * shutdown: :meth:`~mdbapi.server.Shutdown` - Shut down the server

Further more does this module maintain global instances of the following classes.
Those objects can be used inside the thread the server runs. 
Usually the main thread.
Using these objects saves a lot of memory.
If the server is not started, the objects are all ``None``.

    * :class:`lib.db.musicdb.MusicDatabase` as ``database``
    * :class:`mdbapi.mise.MusicDBMicroSearchEngine` as ``mise``
    * :class:`lib.cfg.musicdb.MusicDBConfig` as ``cfg``

The following example shows how to use the pipe interface:

    .. code-block:: bash

        # Update caches
        echo "refresh" > /data/musicdb/musicdb.fifo

        # Terminate server
        echo "shutdown" > /data/musicdb/musicdb.fifo

"""

import traceback
import random
import time
import signal
from threading          import Thread
from lib.cfg.musicdb    import MusicDBConfig
from lib.db.musicdb     import MusicDatabase
from lib.pidfile        import *
from lib.namedpipe      import NamedPipe
from lib.ws.server      import MusicDBWebSocketServer
from mdbapi.mise        import MusicDBMicroSearchEngine
from mdbapi.tracker     import StartTracker, StopTracker
from mdbapi.stream      import StartStreamingThread, StopStreamingThread
import logging

# Global objects
# This is the server environment that needs to be accessed by many objects
# Instances
database    = None  # music.db object
mise        = None  # micro search engine object
cfg         = None  # overall configuration file
pipe        = None  # Named pipe for server commands
# WS Server
tlswsserver = None
shutdown    = False

def SignalHandler(signum, stack):
    """
    This is the general signal handle for the MusicDB Server.
    This function reacts on system signals and calls the handler of a specific signal.

    Args:
        signum: signal number
        stack: current stack frame
    
    Returns: Nothing
    """
    if signum == signal.SIGUSR1:
        logging.debug("Got signal USR1")
        SIGUSR1_Handler()
    elif signum == signal.SIGTERM:
        logging.debug("Got signal TERM")
        SIGTERM_Handler()
    else:
        logging.warning("Got unexpected signal %s"%str(signum))


# Update Caches
def SIGUSR1_Handler():
    logging.info("\033[1;33m(DEPRECATED: Signals will be removed in 2019) \033[1;36mSIGUSR1:\033[1;34m Updating caches …\033[0m") # DEPRECATED 2019
    UpdateCaches()


def UpdateCaches():
    """
    This function handles the *refresh* command from the named pipe.
    Its task is to trigger updating the servers cache and to inform the clients to update.

    On server side:
    
        * The MiSE Cache gets updated by calling :meth:`mdbapi.mise.MusicDBMicroSearchEngine.UpdateCache`


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


# Initiate Shutdown
def SIGTERM_Handler():
    """
    This function is the handler for the system signal TERM.
    It signals the server to shut down.
    """
    logging.info("\033[1;33m(DEPRECATED: Signals will be removed in 2019) \033[1;36mSIGTERM:\033[1;34m Initiate Shutdown …\033[0m") # DEPRECATED 2019
    global shutdown
    shutdown = True



def Initialize(configobj, databaseobj):
    """
    This function initializes the whole server.
    It initializes lots of global objects that get shared between multiple connections.

    The following things happen when this method gets called:

        #. Assign the *configobj* and *databaseobj* to global variables ``cfg`` and ``database`` to share them between multiple connections
        #. Seed Python's random number generator
        #. Instantiate a global :meth:`mdbapi.mise.MusicDBMicroSearchEngine` object
        #. Start the song Tracker via :meth:`mdbapi.Tracker.StartTracker`
        #. Start the Streaming Thread via :meth:`mdbapi.stream.StartStreamingThread` (see :doc:`/mdbapi/stream` for details)
        #. Update MiSE cache via :meth:`mdbapi.mise.MusicDBMicroSearchEngine.UpdateCache`
        #. Create FIFO file for named pipe

    Args:
        configobj: :class:`~lib.cfg.musicdb.MusicDBConfig` that gets shared between connections
        databaseobj: :class:`~lib.db.musicdb.MusicDatabase` that gets shared between connections

    Returns:
        ``None``

    Raises:
        TypeError: When *configobj* is not of type :class:`~lib.cfg.musicdb.MusicDBConfig`
        TypeError: When *databaseobj* is not of type :class:`~lib.cfg.musicdb.MusicDatabase`
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
    mise   = MusicDBMicroSearchEngine(database)

    # Start/Connect all interfaces
    logging.debug("Starting Tracker…")
    StartTracker(cfg)
    
    logging.debug("Starting Streaming Thread…")
    StartStreamingThread(cfg, database)
    
    logging.debug("Updateing MiSE Cache…")
    mise.UpdateCache()
    
    # Signal Handler
    # Don't mention the signals - they are deprecated!
    #logging.info("Register signals \033[0;36m(" + cfg.server.pidfile + ")\033[0m")
    #logging.info("\t\033[1;36mUSR1:\033[1;34m Update Caches\033[0m")
    signal.signal(signal.SIGUSR1, SignalHandler)
    #logging.info("\t\033[1;36mTERM:\033[1;34m Shutdown Server\033[0m")
    signal.signal(signal.SIGTERM, SignalHandler)

    # Named Pipe
    global pipe
    logging.info("Open pipe \033[0;36m(" + cfg.server.fifofile + ")\033[0m")
    logging.info("\t\033[1;36mrefresh\033[1;34m: Update Caches\033[0m")
    logging.info("\t\033[1;36mshutdown\033[1;34m: Shutdown Server\033[0m")
    pipe = NamedPipe(cfg.server.fifofile)
    pipe.Create()

    return None



def StartWebSocketServer():
    """
    This function creates and starts a the actual MusicDB Websocket Server.

    Returns:
        ``True`` on success, otherwise ``False``
    """
    global tlswsserver
    tlswsserver = MusicDBWebSocketServer()
    
    retval = tlswsserver.Setup(cfg.websocket.address, cfg.websocket.port
            , cfg.tls.cert, cfg.tls.key)
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

        #. Stop the song Tracker via :meth:`mdbapi.tracker.StopTracker`
        #. Stop the Streaming Thread via :meth:`mdbapi.stream.StopStreamingThread`
        #. Removing FIFO file for named pipe
        #. Stop the websocket server

    At the end, the program gets terminated. So, this function gets never left.
    
    The exit code will be ``0`` if this was a regular shutdown.
    If the shutdown got forced, for example due to a critical error, the exit code is ``1``.

    This function should also be called when :meth:`~mdpapi.server.Initialize` fails or when it raises an exception.
    """
    logging.info("Shutting down MusicDB-Server")
    global tlswsserver

    if tlswsserver:
        logging.debug("Disconnect from clients…")
        tlswsserver.factory.CloseConnections()
    
    logging.debug("Stopping Tracker…")
    StopTracker()

    logging.debug("Stopping Streaming Thread…")
    StopStreamingThread()
    
    if tlswsserver:
        logging.debug("Stopping TLS WS Server…")
        tlswsserver.Stop()

    global pipe
    logging.debug("Removing named pipe…")
    pipe.Delete()

    # dead end
    global shutdown
    if shutdown:
        exit(0)
    else:
        exit(1)



def Run():
    """
    This is the servers main loop.

    Inside the loop all MusicDB Websocket Server events get handled by calling :meth:`lib.ws.server.MusicDBWebSocketServer.HandleEvents`.
    When a shutdown gets triggered the :meth:`~mdbapi.server.Shutdown` function gets called and the server stops.

    The :meth:`~mdbapi.server.Shutdown` gets also called the user presses *Ctrl-C* This leads to a regular shutdown.

    In as an exception occurs the :meth:`~mdbapi.server.Shutdown` gets called, too. In this case the exit-code will be ``1``.
    """
    global pipe

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
            
            line = pipe.ReadLine()
            if line == "shutdown":
                shutdown = True
            elif line == "refresh":
                UpdateCaches()

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

