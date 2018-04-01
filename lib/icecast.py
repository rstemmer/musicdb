# MusicDB,  a music manager with web-bases UI that focus on music.
# Copyright (C) 2018  Ralf Stemmer <ralf.stemmer@gmx.net>
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
This module implements the interface to `Icecast <https://icecast.org/>`_.

The stream uses the python interface `Shouty <https://github.com/edne/shouty>`_ 
to `libshout <https://github.com/xiph/Icecast-libshout>`_ 
from the `Icecast <https://icecast.org/>`_.

.. code-block:: bash

    pip install shouty


Introduction to Icecast
-----------------------

A setup using Icecast consist of three components. Using Icecast's terms, the are the following:

    Source Client:
        This the software that provides the music. In this setup, it is *MusicDB*.
        It is called client, because it connects to Icecast that can manage multiple source clients.

    Icecast Server:
        This is *Icecast* itself. It servers the audio stream to the world.

    Listener:
        The listener is the receiver of the stream. For example VLC.

Icecast can handle multiple sources.
Each source is used for the input of a *Mountpoint*.
All *Listeners* that want to access the audio stream receives the data from this Mountpoint's output.

For more details see the `Icecast Documentation <https://icecast.org/docs/icecast-trunk/basic_setup/>`_.


Icecast Configuration
^^^^^^^^^^^^^^^^^^^^^

The Icecast configuration defines the *Source Client* and how the data from the Source Clients gets served to the listeners.

In this section, I only point out the more important settings of the whole Icecast configuration.
There is a good example configuration provided by MusicDB.
The following list addresses the settings in the XML file for the Icecast configration.

    icecast/authentication/source-password:
        This is the password *MusicDB* needs to know to connect to Icecast.
        So this password must be the same as in MusicDB Configuration ``[icecast]->password``.

There are two ports needed for the MusicDB/Icecast setup.
One port to connect MusicDB to Icecast, and one to provide the stream to Listeners.
The MusicDB connection (Port 6666) is bound to localhost and not encrypted.
The other port (666) can be open to the world because it will be encrypted and protected against unwanted access.

The ports will be configured in the ``icecast`` section of the configuration file by adding ``listen-socket`` sections:

    .. code-block:: xml

        <!-- Extern -->
        <listen-socket>
            <port>666</port>
            <ssl>1</ssl>
        </listen-socket>

        <!-- Intern -->
        <listen-socket>
            <port>6666</port>
            <ssl>0</ssl>
            <shoutcast-mount>/stream</shoutcast-mount>
        </listen-socket>


    icecast/listen-socket/shoutcast-mount:
        This setting defines the *Mountpoint* name (starting with "/").
        It must be the same like the one set in MusicDB's configuration: ``[icecast]->mountname``
        Further more it must be equal to the name definded in the detailed mount specification: ``icecast/mount/mount-name``.


User Management
^^^^^^^^^^^^^^^

TODO:

How to remove access validation.

How to create a new user


"""

# TODO: scan for "TODO" and check if the configuration hints are still valid

import os
import logging
import shouty


class IcecastInterface(object):
    """
    This Icecast interface manages the connection to the Icecast server 
    and provides the server with the mp3 files cached in the MusicDB mp3 Cache (:mod:`mod.cache`, :mod:`mdbapi:musiccache`).
    
    The following values for setting up the connection via libshout are hard coded.
    They can easily be changed in the Icecast configuration in the ``icecast/mount`` section.

        +-------------+-------------------------+------------------------------------------------------------------------+
        | Parameter   | Value                   | Comment                                                                |
        +=============+=========================+========================================================================+
        | protocol    | ``SHOUT_PROTOCOL_HTTP`` | The native and recommended format for Icecast 2                        |
        +-------------+-------------------------+------------------------------------------------------------------------+
        | format      | ``SHOUT_FORMAT_MP3``    | Obvious. MusicDB streams mp3 files                                     |
        +-------------+-------------------------+------------------------------------------------------------------------+
        | public      | ``0``                   | For security and privacy reasons                                       |
        +-------------+-------------------------+------------------------------------------------------------------------+
        | host        | ``"localhost"``         | For security reasons MusicDB and Icecast must run on the same computer |
        +-------------+-------------------------+------------------------------------------------------------------------+
        | name        | ``"MusicDB Stream"``    |                                                                        |
        +-------------+-------------------------+------------------------------------------------------------------------+
        | dumpfile    | ``None``                | Storing the stream does not make sense for non-moderated streams       | 
        +-------------+-------------------------+------------------------------------------------------------------------+
        | url         | ``None``                | There is no website for the stream, because it is a private stream     |
        +-------------+-------------------------+------------------------------------------------------------------------+
        | genre       | ``None``                | Not relevant for private streams                                       |
        +-------------+-------------------------+------------------------------------------------------------------------+
        | description | ``None``                | Not relevant for private streams                                       |
        +-------------+-------------------------+------------------------------------------------------------------------+
        | agent       | ``None``                | Not relevant                                                           |
        +-------------+-------------------------+------------------------------------------------------------------------+
        | audio_info  | ``None``                | Not relevant                                                           |
        +-------------+-------------------------+------------------------------------------------------------------------+

    Args:
        port (int): port number for the *Source Client* connection
        user (str): Name of the source user
        password (str): The password of the source user
        mountname (str): Name of the mountpoint to use.

    Example:

        .. code-block:: python

            # Create IcecastInterface object
            icecast = IcecastInterface(666, "source", "hackme", "/stream")

            # Connect to the Icecast server
            icecast.Connect()

            # Stream one file
            for size, offset in icecast.StreamFile("/tmp/test.mp3"):
                print("%i of %i bytes sent"%(offset, size))

            # Disconnect from the Icecast server
            icecast.Disconnect()
    """

    def __init__(self, port, user, password, mountname):

        self.icecast = shouty.connection.Connection()
        self.icecast.set_params(
                host     = "localhost",
                port     = port,
                user     = user,
                password = password,
                protocol = shouty.Protocol.HTTP,
                format   = shouty.Format.MP3,
                mount    = mountname,
                dumpfile = None,
                agent    = None,
                public   = 0,
                name     = "MusicDB Stream",
                url      = None,
                genre    = None,
                description = None,
                audio_info  = None
                )

        self.connectionstate = False



    def IsConnected(self):
        """
        Returns:
            ``True`` if connected to Icecase. ``False`` of not connected.
        """
        return self.connectionstate



    def Connect(self):
        """
        Tries to connect to Icecast.

        If already connected, only ``True`` gets returned with out opening again.

        Returns:
            ``True`` on success, otherwise ``False``
        """
        logging.debug("Connecting to Icecast server.")
        if self.connectionstate == True:
            logging.warning("Connection to Icecast already open! \033[1;30m(Will not be opened again)")
            return True

        try:
            self.icecast.open()
        except Exception as e:
            logging.error("Connecting to Icecast failed with the following exception: %s", str(e))
            self.connectionstate = False
            return False

        self.connectionstate = True
        return True



    def Disconnect(self):
        """
        Tries to close the Icecast connection.

        If already disconnected, only ``True`` gets returned with out disconnecting again.

        Returns:
            ``True`` on success, otherwise ``False``
        """
        if self.connectionstate == False:
            logging.warning("Not connected to Icecast! \033[1;30m(So closing is not needed)")
            return True

        logging.debug("Disconnecting from Icecast server.")
        self.connectionstate = False    # whatever happens, we are disconnected.

        try:
            self.icecast.close()
            #self.icecast.free()    # Do not free, to be able to reconnect.
        except Exception as e:
            logging.error("Disconnecting from Icecast failed with the following exception: %s", str(e))
            return False

        return True



    def StreamChunk(self, chunk):
        """
        This method send a chunk of a file to the Icecast server.
        The method synchronizes with Icecast before sending the data.
        This is a blocking process!
        
        Args:
            chunk (bytes): A chunk of a file to stream to Icecast

        Returns:
            ``True`` on success, ``False`` otherwise

        Raises:
            TypeError: When ``chunk`` is not of type bytes

        Example:

            .. code-block:: python

                with open(path) as mp3:
                    while True:
                        chunk = mp3.read(4096)
                        if not chunk:
                            print("File sent.")
                            break

                        retval = icecast.StreamChunk(chunk)
                        if retval == False:
                            print("ERROR")
                            break
        """
        if type(chunk) != bytes:
            raise TypeError("Chunks must be of type bytes!")

        if self.connectionstate == False:
            logging.warning("Not connected to Icecast! \033[1;30m(No data sent)")
            return False

        try:
            self.icecast.sync()         # libshout doc recommends to call sync before send.
            self.icecast.send(chunk)
        except Exception as e:
            logging.error("Sending chunk to Icecast failed with error %s", str(e))
            return False
        return True



    def StreamFile(self, path):
        """
        This is a generator that sends a file to the Icecast server.
        The file gets split into 4096 byte chunks.

        After sending one chunk, the generator returns a tuple ``(size, offset)`` 
        with ``size`` as the file size, 
        and ``chunk`` as the offset of the next chunk in the file.

        Args:
            path (str): Absolute path to the mp3 file to stream. The encoding must be the same for all files!

        Returns:
            Returns a generator that generates tuple ``(size, offset)`` of the streaming progress

        Example:

            .. code-block:: python

                for size, offset in icecast.StreamFile(path):
                    print("%i bytes of %i bytes sent."%(offset, size))
        """

        offset = 0
        try:
            filesize = os.path.getsize(path)
        except FileNotFoundError as e:
            logging.error("File \"%s\" does not exist!", str(path))
            return

        with open(path, "rb") as mp3:

            # Process file chunk-wise
            while True:
                chunk = mp3.read(4096)
                if not chunk:
                    break

                retval = self.StreamChunk(chunk)
                if retval == False:
                    break

                offset += len(chunk)
                yield filesize, offset



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

