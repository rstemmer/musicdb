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
from lib.mp3file import MP3File


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
    
    The Icecast Interface class can stream any data to the Icecast Server via :meth:`~StreamChunk`.
    In general this should be not necessary!
    Instead only use the :meth:`~StreamFile` method that streams a mp3 file addressed by its path.
    Advantage of the :meth:`~StreamFile` is, beside a clean frame wise transfer of the data to the server,
    that the stream can be muted via :meth:`~Mute`.

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
        self.mutestate       = False
        self.silentframe     = b"\xff\xfb\xe0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00Info\x00\x00\x00\x0f\x00\x00\x00(\x00\x00\xa7X\x00\x0c\x0c\x12\x12\x18\x18\x18\x1f\x1f%%%++11188>>>DDJJJQQWWW]]cccjjpppvv|||\x83\x83\x89\x89\x89\x8f\x8f\x95\x95\x95\x9c\x9c\xa2\xa2\xa2\xa8\xa8\xae\xae\xae\xb5\xb5\xbb\xbb\xbb\xc1\xc1\xc7\xc7\xc7\xce\xce\xd4\xd4\xd4\xda\xda\xe0\xe0\xe0\xe7\xe7\xed\xed\xed\xf3\xf3\xf9\xf9\xf9\xff\xff\x00\x00\x00\x00Lavc57.10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00$\x05|\x00\x00\x00\x00\x00\x00\xa7X\xa4\xd9\xdf&\x00\x00" + b"\x00"*850



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
        logging.debug("Trying to connect to Icecast server.")
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

        When sending a chunk of data to Icecast fails,
        the method disconnects from the Server.
        
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
            logging.error("Sending chunk to Icecast failed with error %s! - Disconnecting from Icecast", str(e))
            self.Disconnect()
            return False
        return True



    def StreamFile(self, path):
        """
        This is a generator that sends a mp3 file to the Icecast server.
        The mp3 file gets split into its frames, and sent frame wise.

        After sending one chunk, the generator returns a dictionary with exact the keys and values
        that gets returned by :meth:`lib.mp3file.MP3File.Frames` and  :meth:`lib.mp3file.MP3File.AnalyzeHeader`

        This frame dictionary gets extended by one further key: ``muted``.
        When this value is ``True``, then a silent frame got sent.
        In this case, all information in the dictionary relate to the next frame from the mp3 file that will be send when the stream continues.
        When ``Fale`` then the information are related to the actual sent frame.

        Streaming of the file using this method allows to pause the audio stream by calling the :meth:`~Mute` method.
        Then instead of the frames from the file, a hard coded frame of pure silence gets streamed as long as the mute-state persists.
        Instead of one silent frame, 10 frames will be streamed at once.
        This is about 261ms of silence.

        The control flow is visualized in the following image:

        .. graphviz::

            digraph hierarchy {
                size="5,8"
                start           [label="Start"];
                loadmp3         [shape=box,     label="Load mp3 file"]
                getframe        [shape=box,     label="Get next frame"]
                ismuted         [shape=diamond, label="state == muted"]
                streamsilence   [shape=box,     label="Stream silence"]
                yieldnextframe  [shape=box,     label="Yield next frame"]
                streamframe     [shape=box,     label="Stream frame"]
                yieldframe      [shape=box,     label="Yield frame"]
                end             [label="End"];

                hasalbumid      [shape=diamond, label="albumid == None"];
                getallalbums    [shape=box,     label="Get all Album IDs"]
                getalltags      [shape=box,     label="Get list of Tag IDs\nfrom filterlist"]
                hasfilterlist   [shape=diamond, label="Is there a filter list"];
                removealbums    [shape=box,     label="Remove albums without\ntags of filter"]
                getallsongs     [shape=box,     label="Get all songs of selected albums"]
                selectsong      [shape=box,     label="Select random song"]


                start           -> loadmp3
                loadmp3         -> getframe
                getframe        -> ismuted          [label="Frame available"]
                ismuted         -> streamsilence    [label="Yes"]
                ismuted         -> streamframe      [label="No"]
                streamsilence   -> yieldnextframe
                streamframe     -> yieldframe
                yieldnextframe  -> ismuted
                yieldframe      -> getframe
                getframe        -> end              [label="No further frames"]

            }

        The silent frame is optimized to be injected in the mp3-files generated by MusicDB for the MP3 Cache.
        The mp3 file was generated as shown in the script example below.
        Then the first frame was captured via the :meth:`lib.mp3file.MP3File.Frames` method.

            .. code-block:: bash
                ffmpeg -filter_complex aevalsrc=0 -acodec libmp3lame -ab 320k -t 1 monosilence.mp3
                ffmpeg -i monosilence.mp3 -ab 320k -ac 2 stereosilence.mp3

        Args:
            path (str): Absolute path to the mp3 file to stream. The encoding must be the same for all files!

        Returns:
            Returns a generator that returns the currently streamed frame.

        Example:

            .. code-block:: python

                for frameinfo in icecast.StreamFile(path):
                    if frameinfo["muted"] == True:
                        print("Stream is muted.")
                        continue

                    print("%i. frame of %i frames sent. Length: %s ms"%(
                            frameinfo["count"], 
                            frameinfo["total"],
                            frameinfo["header"]["frametime"]
                            ))
        """

        try:
            mp3 = MP3File(path)
        except Exception as e:
            logging.error("Loading \"%s\" failed with error: %s", str(path), str(e))
            return

        for frame in mp3.Frames():
            # Muted -> stream silence
            while self.mutestate == True:
                retval = self.StreamChunk(self.silentframe*10) # ~ 261ms silence
                if retval == False:
                    break

                frame["muted"] = True
                yield frame

            # stream mp3 frame
            retval = self.StreamChunk(frame["frame"])   # Stream whole mp3 frame
            if retval == False:
                break

            frame["muted"] = False
            yield frame




    def Mute(self, state=True):
        """
        This method sets the Icecast Interface into a mute state (when ``state == True``).
        Then, the method :meth:`~StreamFile` streams silence instead of the file content.
        After leaving the mute state, the file streaming continues at the position it got muted (=paused)

        Args:
            state (bool): Mute stream when ``True``, otherwise continue streaming audio

        Returns:
            *Nothing*
        """
        self.mutestate = state


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

