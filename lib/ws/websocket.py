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
This module provides low level classes for the WebSocket communication to the WebUI.

Most interesting are the following methods:

    * :meth:`lib.ws.websocket.WebSocket.SendPacket`
    * :meth:`lib.ws.websocket.WebSocket.BroadcastPacket`
    * :meth:`lib.ws.websocket.WebSocket.onMessage`
"""

from autobahn.asyncio.websocket import WebSocketServerProtocol, WebSocketServerFactory
import json
import time
import traceback
import logging


class MusicDBWebSocketFactory(WebSocketServerFactory):
    """
    Derived from ``WebSocketServerFactory``.
    Implements some basic configuration and a broadcasting infrastructure to send packets to all connected clients.
    """
    def __init__(self):
        WebSocketServerFactory.__init__(self)
        logging.debug("Using WebSocket module " + str(self.server))
        from mdbapi.server import cfg

        self.openHandshakeTimeout   = cfg.websocket.opentimeout
        self.closeHandshakeTimeout  = cfg.websocket.closetimeout
        #logging.debug("openHandshakeTimeout = " + str(self.openHandshakeTimeout))
        #logging.debug("closeHandshakeTimeout= " + str(self.closeHandshakeTimeout))
        #logging.debug("autoPingTimeout      = " + str(self.autoPingTimeout))
        #logging.debug("autoPingInterval     = " + str(self.autoPingInterval))
        #logging.debug("server               = " + str(self.server))
        #logging.debug("isSecure             = " + str(self.isSecure))

        self.clients    = []    # for broadcast



    def AddToBroadcast(self, client):
        """
        This method registers a new client.
        The client must be of the low level class :class:`lib.ws.websocket.WebSocket` or a derived class.

        Args:
            client: WebSocket connection handler

        Returns:
            *Nothing*
        """
        if client not in self.clients:
            self.clients.append(client)


    def RemoveFromBroadcast(self, client):
        """
        Removes a client connection handler from the broadcast-list.

        Args:
            client: WebSocket connection handler

        Returns:
            *Nothing*
        """
        if client in self.clients:
            self.clients.remove(client)


    def BroadcastPacket(self, packet):
        """
        This method broadcasts a packet to all connected clients.

        The ``method`` value in the packet gets forced to ``"broadcast"``.

        Args:
            packet: A packet dictionary that shall be send to all clients

        Returns:
            *Nothing*
        """
        packet["method"] = "broadcast"
        logging.debug("Sending Broadcast Message. \033[1;30m(fncname = %s, fncsig = %s)", packet["fncname"], packet["fncsig"])

        for client in self.clients:
            try:
                client.SendPacket(packet)
            except Exception as e:
                logging.warning("Sending broadcast packet failed for one client with error: %s\033[1;30m (Ignoring that client)", str(e))


    def CloseConnections(self):
        """
        This method initiates a closing handshake to all connections with error code ``1000`` and reason ``"Server shutdown"``

        Returns:
            *Nothing*
        """
        for client in self.clients:
            try:
                client.sendClose(1000, "Server shutdown")
            except Exception as e:
                logging.warning("Closing connection to clientpacket for one client with error: %s\033[1;30m (Ignoring that client)", str(e))



class WebSocket(WebSocketServerProtocol):
    """
    Derived from ``WebSocketServerProtocol``.
    This class provides the low level WebSocket interface for MusicDBs WebSocket Interface.
    It manages the packet handling and handles callback routines.
    """
    def __init__(self):
        WebSocketServerProtocol.__init__(self)
        self.connected = False



    def SendPacket(self, packet):
        """
        This method sends a packet via to the connected client.
        The format of the packet is described in the :doc:`/basics/webapi` documentation.

        The abstract process of sending the packet is shown in the following code:

            .. code-block:: python

                rawdata = json.dumps(packet)        # Python Dict to JSON string
                rawdata = rawdata.encode("utf-8")   # Encode as UTF-8
                self.sendMessage(rawdata, False)    # isBinary = False
        
        There is a race condition allowing calling ``SendPacket`` before the connection process is complete.
        To prevent problems, this method returns ``False`` if the connection is not established yet.
        Further more the state of the connection gets checked.
        If the connection state is not *OPEN*, ``False`` gets returned, too.

        Args:
            packet: A packet dictionary that will be send to the client

        Returns:
            ``True`` on success, otherwise ``False``

        Raises:
            TypeError: If packet is not of type ``dict``
            RuntimeError: If *Autobahns* ``WebSocketServerProtocol`` class did not set an internal state. Should never happen, but happed once :)

        Example:

            Response to an album request by a client.

            .. code-block:: python

                response    = {}
                response["method"]      = "response"
                response["fncname"]     = "GetAlbums"
                response["fncsig"]      = request["fncsig"]
                response["arguments"]   = albums
                response["pass"]        = request["pass"]
                self.SendPacket(response)
        """
        if type(packet) != dict:
            raise TypeError("Expecting a dictionary")

        if self.connected == False:
            logging.warning("Socket not conneced! \033[1;30m(message will be discard) %s", str(self))
            return False

        rawdata = json.dumps(packet)
        rawdata = rawdata.encode("utf-8")
        
        if not hasattr(self, "state"):
            # This can hatten in some strange situation where Autobahn seems to be in a half-connected state.
            # Usually this should never happen, but happend at least once.
            logging.error("Websocket connetion has no stater!")
            raise RuntimeError("Autobahn totaly fucked it up")

        if self.state != WebSocketServerProtocol.STATE_OPEN:
            logging.warning("State of websocket is not STATE_OPEN! \033[0;33mState is %d. \033[1;30m(message will be discard)", self.state)
            # Possible states:
            # https://github.com/crossbario/autobahn-python/blob/2ea1c735f7a116a8b2cd64b3d38a91aba9ca35f8/autobahn/websocket/protocol.py#L422
            # STATE_CLOSED = 0
            # STATE_CONNECTING = 1
            # STATE_CLOSING = 2
            # STATE_OPEN = 3
            return False

        try:
            self.sendMessage(rawdata, False)
        except Exception as e:
            logging.warning("Unexpected error while trying to send a message: %s! \033[0;33m(message will be discard)", str(e))
            return False
        return True


    def BroadcastPacket(self, packet):
        """
        This method works line :meth:`~lib.ws.websocket.WebSocket.SendPacket` only that the packet gets send to all clients.
        It uses the broadcasting method from :meth:`lib.ws.websocket.MusicDBWebSocketFactory.BroadcastPacket`
        This method should be used with care because it can cause high traffic.

        Args:
            packet: A packet dictionary that will be send to all clients

        Returns:
            *Nothing*
        """
        self.factory.BroadcastPacket(packet)



    def onOpen(self):
        """
        This method gets called by ``WebSocketServerProtocol`` implementation.
        It registers this connection to the broadcasting infrastructure of :class:`lib.ws.websocket.MusicDBWebSocketFactory`.

        This method calls an ``onWSConnect()`` Method that must be implemented by the programmer who uses this class.
        """
        logging.info("Websocket connection established.")
        self.connected = True
        self.factory.AddToBroadcast(self)
        self.onWSConnect()


    def onClose(self, wasClean, code, reason):
        """
        This method gets called by ``WebSocketServerProtocol`` implementation.
        It removes this connection to the broadcasting infrastructure of :class:`lib.ws.websocket.MusicDBWebSocketFactory`.

        This method calls an ``onWSDisconnect(wasClean:bool, closecode:int, closereason:str)`` Method that must be implemented by the programmer who uses this class.
        """
        self.connected = False
        self.factory.RemoveFromBroadcast(self)

        if code == WebSocketServerProtocol.CLOSE_STATUS_CODE_NORMAL:
            logging.info("Websocket connection closed with \"Normal\" code.")
        elif code == WebSocketServerProtocol.CLOSE_STATUS_CODE_GOING_AWAY:
            logging.info("Websocket connection closed with \"Going Away\" code. \033[1;30m(Client just went away)")
        elif code == None and wasClean == True:
            logging.info("Websocket connection closed without an exit-code. \033[1;30m(Exitcode == None ; wasClean-Flag == True)")
        else:
            logging.warning("Websocket connection closed abnormaly!")
            logging.debug  ("\033[0;33mwasClean = %s" % wasClean)
            logging.debug  ("\033[0;33mcode     = \033[1;33m%s" % code)
            logging.warning("\033[0;33mreason   = \033[1;33m%s" % reason)
            logging.debug  ("\033[0;33mclosedByMe  = %s" % self.closedByMe)
            logging.debug  ("\033[0;33mfailedByMe  = %s" % self.failedByMe)
            logging.debug  ("\033[0;33mdroppedByMe = %s" % self.droppedByMe)
            logging.debug  ("\033[0;33mwasClean          = %s" % self.wasClean)
            logging.debug  ("\033[0;33mwasNotCleanReason = \033[1;33m%s" % self.wasNotCleanReason)
            logging.debug  ("\033[1;33mlocalCloseCode    = %s" % self.localCloseCode)
            logging.debug  ("\033[1;33mlocalCloseReason  = %s" % self.localCloseReason)
            logging.debug  ("\033[1;33mremoteCloseCode   = %s" % self.remoteCloseCode)
            logging.debug  ("\033[1;33mremoteCloseReason = %s" % self.remoteCloseReason)

        self.onWSDisconnect(wasClean, code, reason)

        #CLOSE_CODE_NORMAL              = 1000 #Normal close of connection.
        #CLOSE_CODE_GOING_AWAY          = 1001 #Going away.
        #CLOSE_CODE_PROTOCOL_ERROR      = 1002 #Protocol error.
        #CLOSE_CODE_UNSUPPORTED_DATA    = 1003 #Unsupported data.
        #CLOSE_CODE_RESERVED1           = 1004 #RESERVED
        #CLOSE_CODE_NULL                = 1005 #No status received.
        #CLOSE_CODE_ABNORMAL_CLOSE      = 1006 #Abnormal close of connection.
        #CLOSE_CODE_INVALID_PAYLOAD     = 1007 #Invalid frame payload data.
        #CLOSE_CODE_POLICY_VIOLATION    = 1008 #Policy violation.
        #CLOSE_CODE_MESSAGE_TOO_BIG     = 1009 #Message too big.
        #CLOSE_CODE_MANDATORY_EXTENSION = 1010 #Mandatory extension.
        #CLOSE_CODE_INTERNAL_ERROR      = 1011 #The peer encountered an unexpected condition or internal error.
        #CLOSE_CODE_TLS_HANDSHAKE_FAILED= 1015 #TLS handshake failed, i.e. server certificate could not be verified.


    def onOpenHandshakeTimeout(self):
        logging.error("Open-Handshake Timeout!")
        WebSocketServerProtocol.onOpenHandshakeTimeout(self)

    def onCloseHandshakeTimeout(self):
        logging.warning("Close-Handshake Timeout!")
        WebSocketServerProtocol.onCloseHandshakeTimeout(self)


    def onMessage(self, payload, isBinary):
        """
        This method gets called by ``WebSocketServerProtocol`` implementation.
        It handles the decoding of a received packet and provides the packet format as described in the :doc:`/basics/webapi` documentation.

        The decoding process can be abstracted as listed in the following code:

            .. code-block:: python

                # Check if payload is text
                if isBinary == True:
                    return None

                # Create packet
                rawdata = payload.decode("utf-8")
                packet  = json.loads(rawdata)

                # Provide packet to high level interface
                self.onCall(packet)

        Args:
            payload: The payload of a WebSocket message received from a client
            isBinary: ``True`` if binary data got received, False`` when text. This implementation allows only text.

        Return:
            ``None``
        """

        # I do not expect binary data
        if isBinary == True:
            logging.warning("Got a binary encoded message. \033[0;33m(Message will be ignored)")
            return None

        try:
            rawdata = payload.decode("utf-8")
        except:
            # hm… better do nothing :D
            logging.warning("Got a none utf-8 encoded message. \033[0;33m(Message will be ignored)")
            return None

        packet = json.loads(rawdata)

        # Handle packet
        try:
            self.onCall(packet)
        except Exception as e:
            logging.error("Unhandled exception in packet handler!")
            logging.exception("Trace: %s", e)

        return None


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

