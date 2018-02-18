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

import kivy
kivy.require('1.10.0')

try:
    import logging
except:
    from kivy.logger import Logger as logging

import ssl
import websocket
import json


class WebSocket(object):
    """
    This class handles the WebSocket connection to a WebSocket Server.
    The URL includes the protocol and port.
    For example: ``"wss://localhost:9000"``

    All methods are blocking.
    This class is designed for burst communication, not for being all the time connected to the server!

    Args:
        url (str): URL to the WebSocket server
    """
    def __init__(self, url):
        self.wsurl = url
        self.wsconnection = None



    def Connect(self, url=None):
        """
        This method opens a connection to the WebSocket server addressed by the ``url`` given to the constructor of this class or as argument to this method.

        Args:
            url (str): URL (including protocol and port) to the WebSocket server. If ``None``, the URL given to the constructor will be used.

        Returns:
            ``True`` on success. In case an error occurs, ``False`` gets returned.
        """
        # Redefine URL if given
        if url != None:
            self.wsurl = url

        # Open Connection
        try:
            self.wsconnection = websocket.create_connection(self.wsurl, 
                    sslopt={"check_hostname": False, "cert_reqs": ssl.CERT_NONE})
        except Exception as e:
            logging.error("Connecting to %s failed with error \"%s\"!"%(str(self.wsurl), str(e)))
            return False

        # Check if succeeded
        if not self.wsconnection:
            return False
        
        return True



    def Disconnect(self):
        """
        A previous opened connection gets closed.

        Returns:
            ``True`` on success. If there was no connection open, ``False`` gets returned.
        """
        if not self.wsconnection:
            return False

        self.wsconnection.close()
        self.wsconnection = None

        return True



    def Send(self, message):
        """
        Sends a message to the WebSocket server.

        Args:
            message (str): The message to send as a string.

        Returns:
            ``True`` on success. If there was no connection open, ``False`` gets returned.
        """
        if not self.wsconnection:
            return False

        self.wsconnection.send(message)

        return True



    def Receive(self):
        """
        This method waits for a message and returns it.

        Returns:
            A message as string, or ``None`` if an error occures
        """
        if not self.wsconnection:
            return None

        result = self.wsconnection.recv()
        return result



class WebSocketClient(WebSocket):
    """
    This class handles the WebSocket connection to the MusicDB WebSocket Server.
    It implements the packet handling for MusicDB's WebSocket Interface.

    The URL includes the protocol and port.
    For example: ``"wss://localhost:9000"``

    All methods are blocking.
    This class is designed for burst communication, not for being all the time connected to the server!

    Args:
        url (str): URL to the WebSocket server
    """
    def __init__(self, url):
        WebSocket.__init__(self, url)


    def SendPacket(self, method, fncname, fncsig, args, passthrough):
        """
        This method implements the MusicDB packet format for WebSocket communication.
        """
        packet = {}
        packet["method"]    = method
        packet["fncname"]   = fncname
        packet["fncsig"]    = fncsig
        packet["arguments"] = args
        packet["pass"]      = passthrough

        rawdata = json.dumps(packet)
        rawdata = rawdata.encode("utf-8")
        
        try:
            retval = self.Send(rawdata)
        except Exception as e:
            logging.warning("Unexpected error while trying to send a message: %s! \033[0;33m(message will be discard)", str(e))
            return False

        if retval == False:
            logging.warning("Socket not connected! \033[1;30m(message will be discard) %s", str(self))
            return False

        return True


    def Call(self, fncname, args=None):
        return self.SendPacket("call", fncname, None, args, None)

    def Request(self, fncname, fncsig, args=None, passthrough=None):
        return self.SendPacket("request", fncname, fncsig, args, passthrough)

    def Broadcast(self, fncname, fncsig, args=None, passthrough=None):
        return self.SendPacket("broadcast", fncname, fncsig, args, passthrough)


    def WaitForResponse(self, fncsig, limit=10):
        """
        This method tries to receive a specific packet.
        The packet gets identified by its function signature (``fncsig``).
        To prevent a deadlock in case of an error, the method returns ``None`` after it dropped a certain number of packets.
        This limit can be defined by the ``limit`` parameter.

        The following pseudo code shows how the algorithm works:

        .. code-block:: python

            for pkgcnt in range(limit):
                packet = GetPacket()
                if packet == None:
                    return None

                if packet["fncsig"] == fncsig:
                    return packet

            return None

        Args:
            fncsig (str): Signature of the packet that shall be received
            limit (int): Optional limit of tries to get the packet.

        Returns:
            The received packet on success, or ``None`` on error.
        """

        for pkgcnt in range(limit):

            payload = self.Receive()
            if payload == None:
                return None

            try:
                rawdata = payload.decode("utf-8")
            except Exception as e:
                # hm… better do nothing :D
                logging.warning("Got a none utf-8 encoded message. \033[0;31m[%s] \033[0;33m(Message will be ignored)"%str(e))
                return None

            packet = json.loads(rawdata)

            try:
                signature = packet["fncsig"]
            except KeyError as e:
                logging.error("Malformed packet received! \033[1;30m(Make sure the following key are included: method, fncname, fncsig, arguments, pass)")
                return None

            if signature == fncsig:
                return packet

        return None

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

