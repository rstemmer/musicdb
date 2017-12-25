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
This module starts the MusicDB Websocket Server.

The start is done in the following steps:

    #. Create PID file (this will be deleted at exit)
    #. Initialize the server by calling :meth:`mdbapi.Initialize`
    #. Start the websocket server by calling :meth:`mdbapi.StartWebSocketServer`
    #. Enter the event loop by running :meth:`mdbapi.Run`

Example:

    This example shows the easiest way to start musicdb.
    The following commands must be called as root. 
    There will appear warnings and errors if ``mpd`` is not running.

    .. code-block:: bash

        musicdb server

    A typical call to start the server as user *musicdb* and to run ``mpd`` is shown in the following example:

    .. code-block:: bash

        mpd /data/musicdb/mpd/mpd.conf
        su -l -c "musicdb --config /data/musicdb/musicdb.ini server" musicdb

    To stop the server, use the TERM-System signal:

    .. code-block:: bash

        kill -TERM $( cat /data/musicdb/musicdb.pid )
"""

import traceback
import argparse
import atexit
from lib.modapi         import MDBModule
from lib.pidfile        import *    # CreatePIDFile
import logging
import mdbapi.server as srv

class server(MDBModule):
    def __init__(self, config, database):
        MDBModule.__init__(self)

        self.config   = config
        self.database = database


    @staticmethod
    def MDBM_CreateArgumentParser(parserset, modulename):
        parser = parserset.add_parser(modulename, help="websocket server")
        parser.set_defaults(module=modulename)


    # return exit-code
    def MDBM_Main(self, args):

        # Show the user that debugging options are enabled
        if self.config.debug.disablestats > 0:
            logging.warning("Collecting statistics disabled!")
        if self.config.debug.disabletracker > 0:
            logging.warning("Tracker disabled!")
        if self.config.debug.disableai > 0:
            logging.warning("AI disabled!")
        if self.config.debug.disabletagging > 0:
            logging.warning("Tagging disabled!")
            
        # Create a PID-File
        CreatePIDFile(self.config.server.pidfile)                  # needed to work with signals
        atexit.register(DeletePIDFile, self.config.server.pidfile) # Delete PID file on exit

        # Initialize Server
        try:
            srv.Initialize(self.config, self.database)
        except Exception as e:
            logging.critical("Fatal error while initializing the server:");
            logging.critical(e)
            traceback.print_exc()
            srv.Shutdown()
            return 1

        # server setup
        retval = srv.StartWebSocketServer()
        if retval == False:
            srv.Shutdown()
            return 1

        # enter event loop
        srv.Run()
        return 1 # Run should never be left but via exit call


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

