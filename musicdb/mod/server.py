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
This module starts the MusicDB Websocket Server.

The start is done in the following steps:

    #. Initialize the GObject and GStreamer libraries
    #. Initialize the server by calling :meth:`mdbapi.Initialize`
    #. Start the websocket server by calling :meth:`mdbapi.StartWebSocketServer`
    #. Set SystemD status to ``READY=1``
    #. Enter the event loop by running :meth:`mdbapi.Run`

Read :doc:`/mdbapi/server` for details

Example:

    The recommended way to start and stop MusicDB is using SystemD:

    .. code-block:: bash

        systemctl start musicdb
        systemctl stop musicdb

"""

import traceback
import argparse
import atexit
import logging
import systemd.daemon

import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst

from musicdb.lib.modapi  import MDBModule
import musicdb.mdbapi.server as srv

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
        if self.config.debug.disablestats:
            logging.warning("Collecting statistics disabled!")
        if self.config.debug.disabletracker:
            logging.warning("Tracker disabled!")
        if self.config.debug.disableai:
            logging.warning("AI disabled!")
        if self.config.debug.disabletagging:
            logging.warning("Tagging disabled!")
        if self.config.debug.disableicecast:
            logging.warning("Icecast disabled!")
        if self.config.debug.disablevideos:
            logging.warning("Videos disabled!")

        # Prepare GStreamer
        GObject.threads_init()
        Gst.init(None)

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

        # Tell SystemD that MusicDB is ready now
        systemd.daemon.notify("READY=1")

        # enter event loop
        srv.Run()
        return 1 # Run should never be left but via exit call


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

