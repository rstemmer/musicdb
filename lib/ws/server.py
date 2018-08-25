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
This module provides the server infrastructure of the server.
"""

from autobahn.asyncio.websocket import WebSocketServerProtocol, WebSocketServerFactory
from lib.ws.websocket           import WebSocket, MusicDBWebSocketFactory
from lib.ws.mdbwsi              import MusicDBWebSocketInterface
import json
import ssl
import asyncio
import logging

class MusicDBWebSocketProtocol(WebSocket, MusicDBWebSocketInterface):
    """
    Derived from :class:`lib.ws.websocket.WebSocket` and :class:`lib.ws.mdbwsi.MusicDBWebSocketInterface`.
    Connecting low level implementation with the high level implementation of MusicDBs WebSocket Interface.

    This object gets always instatiated when a new client connects to the server.
    **It does not matter if this is a websocket client or not!**.
    To initialize code that needs a working websocket connection, use the ``onWSConnect`` callback interface.

    You can and should check changes in :class:`lib.ws.mdbwsi.MusicDBWebSocketInterface`
    by starting the server and accessing it via ``nmap -p $MDBServerPort localhost`` or by accessing the server via https from your browser.
    Both are not valid websocket connections.
    The server should create a new connection but will not call the ``onWSConnect`` method.
    """
    def __init__(self):
        WebSocket.__init__(self)
        MusicDBWebSocketInterface.__init__(self)
        logging.info("New protocolobject created for connection.")


class MusicDBWebSocketServer(object):
    """
    This class implements the whole server infrastructure.
    Outside of the MusicDB WebSocket Interface abstraction this is the only class to use.
    """
    def __init__(self):
        self.factory    = MusicDBWebSocketFactory()
        self.factory.protocol = MusicDBWebSocketProtocol
        self.eventloop  = asyncio.get_event_loop()
        self.coro       = None
        self.server     = None
        self.tlscontext = None


    def Setup(self, address, port, cert, key):
        """
        This method does the server setup.

        It configures the TLS encryption (TLSv1.2) and creates the event loop.

        Args:
            address (str): address to bind to
            port (int): port to bind to
            cert (str): Path to an SSL certificate
            key (str): Path to the key for the certificate

        Returns:
            ``True`` on success, otherwise ``False``
        """
        logging.info("MusicDB WebSocket Server (\033[0;32mTLSv1.2 secured\033[1;34m) listening to port \033[1;36m%s", port)
        self.tlscontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2) # deprecated sinze 3.6 # FIXME
        # New would be the following, but websockets crash if using this
        # tlscontext = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        # tlscontext.options |= ssl.OP_NO_SSLv2
        # tlscontext.options |= ssl.OP_NO_SSLv3
        # tlscontext.options |= ssl.OP_NO_TLSv1
        # tlscontext.options |= ssl.OP_NO_TLSv1_1
        self.tlscontext.set_ciphers("HIGH:MEDIUM:!aNULL:!MD5")
        self.tlscontext.verify_mode = ssl.CERT_NONE # no client side cert needed... # FIXME

        try:
            self.tlscontext.load_cert_chain(cert, key)
        except FileNotFoundError:
            logging.critical("At least one of the following files are missing:")
            logging.critical(cert)
            logging.critical(key)
            logging.critical("Secure websockets (TLS) not possible!")
            return False
        except PermissionError:
            logging.critical("At least one of the following files are not accessable (Permission Error):")
            logging.critical(cert)
            logging.critical(key)
            logging.critical("Secure websockets (TLS) not possible!")
            return False

        try:
            self.coro = self.eventloop.create_server(self.factory, address, port, ssl=self.tlscontext, )
            self.task = self.eventloop.create_task(self.coro)   # necessary for run_until_complete
        except Exception as e:
            logging.exception("Creating server task failed with exception: %s", str(e))
            return False
        return True


    def Start(self):
        """
        This method starts the server.

        Returns:
            ``True`` on success, otherwise ``False``

        Example:

            .. code-block:: python

                server = MusicDBWebSocketServer()

                retval = tlswsserver.Setup("127.0.0.1", 9000, "/etc/ssl/test/test.cert", "/etc/ssl/test/test.key")
                if retval == False:
                    print("Setup for TLS-Server failed!")
                    exit(1)

                retval = tlswsserver.Start()
                if retval == False:
                    print("Starting TLS-Server failed!")
                    exit(1)
        """
        if self.server:
            logging.warning("Double-Start. Server already running.")
            return False

        if not self.tlscontext:
            logging.warning("You need to setup the server before starting!")
            return False

        try:
            self.server = self.eventloop.run_until_complete(self.task)
        except Exception as e:
            logging.exception("Starting server eventloop failed with exception: %s", str(e))
            return False
        return True


    def HandleEvents(self):
        """
        This method handles the events inside the *Autobahn* internal event loop.
        It should be called in a loop as long as the server shall work.

        Returns:
            *Nothing*

        Example:

            .. code-block:: python

                    while True:
                        server.HandleEvents()
                        
                        if shutdown:
                            server.Stop()
                            break

                        time.sleep(.1)  # Avoid high CPU load
        """
        self.eventloop.run_until_complete(self.task)


    def Stop(self):
        """
        This methos halts the server.
        It closes the connection and the event loop.

        Returns:
            ``True``
        """
        if self.server:
            self.server.close() # Close the websocket server
        else:
            logging.warning("No server running to stop!")

        logging.debug("Stopping event loop")
        self.eventloop.run_until_complete(self.eventloop.shutdown_asyncgens()) # TODO: Check if I need this
        self.eventloop.close()  # Close the asyncio event loop

        self.server    = None
        self.eventloop = None
        return True



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

