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


class WebSocketClient(object):
    """
    This class handles the WebSocket connection to the MusicDB WebSocket Server.
    The URL includes the protocol and port.
    For example: ``"wss://localhost:9000"``

    All methods are blocking.
    This class is designed for burst communication, not for being all the time connected to the server!
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



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

