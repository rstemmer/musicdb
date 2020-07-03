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
This module transcodes the users source music into mp3 data that can be streamed via :class:`lib.stream.icecast.IcecastInterface`.
Therefore it uses the :class:`lib.stream.gstreamer.GStreamerInterface` class.
A `GStreamer Pipeline`_ will be created to transcode m4a, mp3 and flac files into a specific mp3 encoding.
The output of the GStreamer Pipeline gets written into a `UNIX Pipe`_.
The data can then be accessed via :mod:`~MP3Transcoder.GetChunk`.

GStreamer Pipeline
------------------

As shown in the graph below, GStreamer is used for the transcoding.
The files get read by the ``filesrc`` element and then be decoded.
The raw audio data gets then be encoded using the ``lamemp3enc`` element.
These mp3 encoded data will then be provided by writing into a `UNIX Pipe`_ for further processing.

    .. graphviz::

        digraph hierarchy {
            size="5,8"

            filesrc       [shape=box, label="filesrc"]
            decodebin     [shape=box, label="decodebin"]
            audioconvert  [shape=box, label="audioconvert"]
            lamemp3enc    [shape=box, label="lamemp3enc"]
            fdsink        [shape=box, label="fdsink"]


            filesrc         -> decodebin
            decodebin       -> audioconvert
            audioconvert    -> lamemp3enc
            lamemp3enc      -> fdsink
        }

The encoding is a MPEG v1 Layer III encoding with 320kb/s and Joint Stereo.

The following example shows the bash representation of the pipeline:

    .. code-block:: bash

        gst-launch-1.0 filesrc location=in.m4a ! decodebin ! audioconvert ! lamemp3enc target=1 bitrate=320 cbr=true ! filesink location=out.mp3

        file out.mp3
        #> out.mp3: MPEG ADTS, layer III, v1, 320 kbps, 44.1 kHz, JntStereo

        ffpribe out.mp3
        #> Duration: 00:03:43.16, start: 0.000000, bitrate: 320 kb/s
        #> Stream #0:0: Audio: mp3, 44100 Hz, stereo, s16p, 320 kb/s

UNIX Pipe
---------

A UNIX Pipe is connected to the ``fdsink`` GStreamer Element.
``fdsink`` writes into the pipe.
Then :meth:`MP3Transcoder.GetChunk` reads some chunks from the mp3 data encoded by the ``lamemp3enc`` Element.

The pipe is accessed non-blocking.

Transcoding
-----------

Transcoding will be done in a separate thread.
To safely work with the :class:`MP3Transcoder` class, you should use the provided context management:


    .. code-block:: python

        with MP3Transcoder("/tmp/test.flac") as transcoder:
            # …
"""

from threading import Thread
import time
import logging
import sys
import os
from lib.stream.gstreamer import GStreamerInterface

class MP3Transcoder(object):
    """
    Args:
        path (str): The absolute path of the audio file that shall be transcoded

    Raises:
        TypeError: When path is not of type string

    Example:
        
        .. code-block:: python

            with MP3Transcoder("/tmp/test.flac") as transcoder:
                while True:
                    chunk = transcoder.GetChunk(4096)
                    if len(chunk) == 0:
                        break
    """

    def __init__(self, path):
        if type(path) != str:
            raise TypeError("Path must be of type string!")

        self.path            = path
        self.gstreamer       = GStreamerInterface("transcoder")
        self.gstreamerthread = None

        self.source    = self.gstreamer.CreateElement("filesrc",      "source")
        self.decoder   = self.gstreamer.CreateElement("decodebin",    "decoder")
        self.converter = self.gstreamer.CreateElement("audioconvert", "converter")
        self.encoder   = self.gstreamer.CreateElement("lamemp3enc",   "encoder")
        self.sink      = self.gstreamer.CreateElement("fdsink",       "sink")

        self.unixpipesource, self.unixpipesink = os.pipe2(os.O_NONBLOCK)

        self.source.set_property("location", self.path)
        self.encoder.set_property("target", 1)
        self.encoder.set_property("bitrate", 320)
        self.encoder.set_property("cbr", True)
        self.sink.set_property("fd", self.unixpipesink)
        
        self.source.link(self.decoder)
        self.converter.link(self.encoder)
        self.encoder.link(self.sink)
        self.decoder.connect("pad-added", self.onDecoderPadAdded)


    def __enter__(self):
        self.Transcode()    # start transcoding
        return self



    def __exit__(self, exc_type, exc_value, traceback):
        # Stop transcoding
        self.Cancel()

        # Close Unix pipes to GStreamer
        os.close(self.unixpipesource)
        os.close(self.unixpipesink)

        # Close GStreamer pipeline
        self.gstreamer = None   # Force Garbage Collection
        # HACK:
        # I observed the following behavior.
        # There were some file handler that get not closed.
        # GStreamer did not close the file handler for the file to transcode.
        # 
        # Closing them explicitly in python using the deref() method lead to the following issue:
        # Exiting the server lead to lots of "GLib-GObject-CRITICAL"-Errors.
        # These errors where produced in the PyFinalizex-function.
        # After some tries I figured out that all unref-falls needed by GStreamer
        # are done by Pythons garbage collector.
        # This is what I originally assumed and why I never called unref.
        #
        # Strange is, that the GStreamer object got garbage collected when the whole software exits
        # and not, before. For example when an instance of this class get destroyed.
        #
        # Setting the reference explicitly to None solved the problem for now.



    def onDecoderPadAdded(self, dbin, pad):
        """
        Args:

        Returns:

        Example:

            .. code-block:: python
        """
        decoder   = pad.get_parent()
        pipeline  = decoder.get_parent()
        converter = pipeline.get_by_name('converter')
        decoder.link(converter)



    def Cancel(self):
        """
        This method cancels a currently running transcoding process.
        If there is no transcoding going on, nothing happens.

        The GStreamer object gets set into CANCEL state.
        The connection to GStreamer stays established!
        """
        # Cancel when there is still a transcoding process
        self.gstreamer.Cancel()
        while True:
            gstate = self.gstreamer.GetState()
            if gstate == "IDLE":
                break
            elif gstate == "ERROR":
                logging.error("GStreamerInterface is in ERROR state!")
                break
            time.sleep(0.1)

        # Wait until Execute thread is finished
        if self.gstreamerthread:
            logging.debug("Waiting for previous transcoding process to stop")
            self.gstreamerthread.join()
            self.gstreamerthread = None



    def Transcode(self):
        """
        This method starts the transcoding process of a file as thread.
        After setting the ``path`` as source for the audio data,
        a thread gets started that runs the GStreamer Pipeline.
        Before leaving, the method ensures that the GStreamer Pipeline is running.
        If an error occurs ``False`` gets returned, otherwise ``True``.

        When calling this method, a previous started transcoding process gets canceled.

        Returns:
            If an error occurs ``False`` gets returned, otherwise ``True``.

        Example:

            .. code-block:: python

                transcoder = MP3Transcoder("/tmp/test.flac")

                retval   = transcoder.Transcode()
                if retval == False:
                    print("\033[1;31mStarting Transcoder failed!")
        """
        # Cancel when there is still a transcoding process
        self.Cancel()

        # Setup new streaming thread
        self.gstreamerthread = Thread(target=self.gstreamer.Execute)
        self.gstreamerthread.start()

        # Make sure the pipeline gets started
        while True:
            gstate = self.gstreamer.GetState()
            if gstate == "RUNNING":
                return True
            elif gstate != "IDLE":
                logging.error("Unexpected GStreamerInterface state: %s", gstate)
                return False
            time.sleep(0.1)



    def GetChunk(self, size):
        r"""
        This method reads a chunk of data that gets provided by the GStreamer ``fdsink`` element from the GStreamer Pipeline.
        This element writes into a UNIX Pipe.
        It tries to read ``size`` bytes of data.
        
        When reading from the UNIX Pipe fails with an ``BlockingIOError``, than the state of the current transcoding gets checked.
        If it is ``RUNNING``, than the method tries to read from the pipe again after 100ms.
        Otherwise it is assumed that the process of transcoding is complete.

        When 0 bytes were read and the state of the transcoding process is not ``RUNNING``, than it is also assumed that the process is competed.

        In all cases, all collected bytes were returned by this method.
        It may only be less that ``size``.
        When there were less than ``size`` bytes returned, or even ``0``, than the process of transcoding can be considered complete.

        The following diagram shows how this method gets the data from the GStreamer Pipeline via UNIX Pipes:

        .. graphviz::

            digraph hierarchy {
                size="5,8"
                start           [label="Start"];

                read            [shape=box,     label="Read data from pipe"]
                isrunningstate  [shape=diamond, label="Is GStreamer Pipeline\nprocess still running?"]
                isempty         [shape=diamond, label="No further bytes\nto expect from pipe?"]
                calcrest        [shape=box,     label="Calculate remaining bytes"]
                appendbytes     [shape=box,     label="Collect already read bytes"]
                bytesremaining  [shape=diamond, label="Remaining\nbytes?"]
                sleep           [shape=box,     label="Sleep for 0.1s"]

                end             [label="Return chunk"];

                start           -> read
                read            -> isrunningstate   [style="dashed", label="Blocking IO Exception"]
                isrunningstate  -> sleep            [label="yes"]
                isrunningstate  -> end              [label="no"]
                sleep           -> read
                read            -> isempty
                isempty         -> end              [label="yes"]
                isempty         -> calcrest         [label="no"]
                calcrest        -> appendbytes
                appendbytes     -> bytesremaining
                bytesremaining  -> sleep            [label="yes"]
                bytesremaining  -> end              [label="no"]

            }

        Args:
            size (int): Number of bytes to read

        Returns:
            A chunk of data as type ``bytes``

        Example:

            .. code-block:: python

                print("\033[1;36mTranscoding %s"%(path))
                sinkpath = path + ".mp3"
                sinkfile = open(sinkpath, "wb")

                retval   = transcoder.Transcode(path)
                if retval == False:
                    print("\033[1;31mStarting Transcoder failed")
                    return 1

                while True:
                    chunk = transcoder.GetChunk(4096)
                    if len(chunk) == 0:
                        break

                    sinkfile.write(chunk)
                sinkfile.close()

        """
        retval = bytes()
        while size > 0:
            try:
                chunk = os.read(self.unixpipesource, size)
            except BlockingIOError:
                if self.gstreamer.GetState() == "RUNNING":
                    # Buffer empty - just wait a bit for GStreamer, then continue
                    time.sleep(0.1)
                    continue

                self.gstreamerthread.join()
                self.gstreamerthread = None
                break

            if len(chunk) == 0 and self.gstreamer.GetState() != "RUNNING":
                self.gstreamerthread.join()
                self.gstreamerthread = None
                break

            size -= len(chunk)
            retval += chunk
            if size > 0:
                time.sleep(0.01)

        return retval



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

