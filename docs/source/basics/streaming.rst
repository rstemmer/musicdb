
MusicDB Stream
==============

This is the overall documentation of the streaming process in MusicDB

For streaming, two major open source projects are involved.
Reading and transcoding the audio files is done by the `GStreamer Framework <https://gstreamer.freedesktop.org>`_.
Streaming the done using `Icecast <https://icecast.org/>`_.

After describing the general data flow from the file to the users client,
a more detailed explanation of how the stream is implemented in MusicDB follows.

General Data Flow
-----------------

The following graph shows the data flow from the audio file to the listener:

   .. graphviz::

      digraph hierarchy {
         size="5,8"

         files       [shape=box, penwidth=3, style=filled, color="#69015a", fillcolor="#dfcce4", label="Audio files\n(mp3, m4a, flac)"]
         gstreamer   [shape=box, penwidth=3, style=filled, color="#016c3c", fillcolor="#8ccfb7", label="GStreamer"]
         mp3stream   [shape=box, penwidth=3, style=filled, color="#016c3c", fillcolor="#8ccfb7", label="MP3 stream\n(mp3)"]
         icecast     [shape=box, penwidth=3, style=filled, color="#121212", fillcolor="#cccccc", label="Icecast"]
         listener    [shape=box, penwidth=3, style=filled, color="#683705", fillcolor="#fedcc6", label="Listener"]

         files     -> gstreamer [color="#69015a", penwidth=3, label="Using GStreamer\nfilesrc element"]
         gstreamer -> mp3stream [color="#69015a", penwidth=3, label="Using UNIX Pipe"]
         mp3stream -> icecast   [color="#69015a", penwidth=3, label="Using libshout"]
         icecast   -> listener  [color="#69015a", penwidth=3, label="via HTTP"]

      }

The meaning of the background colors are similar to the :doc:`/basics/overview` image.
Purple are the source song files from the users music collection.
Green are MusicDB modules, gray external server programs, and yellow are tools for the user.

The audio files get read by the MusicDB server using the `GStreamer Framework <https://gstreamer.freedesktop.org>`_.
GStreamer decodes the files and encodes it into the mp3 format.
Details about this process is described in :doc:`/lib/mp3transcoder` documentation.

After transcoding, the mp3 frames gets read and processed by the :doc:`/lib/mp3stream`.
Then each mp3 frame gets send to the `Icecast <https://icecast.org/>`_ process using *libshout*

The audio stream provided by Icecast can new be received by any multimedia player that can connect to audio streams.


Stream Implementation
---------------------

The following image shows how the stream management is implemented and integrated into MusicDB.
Furthermore it shows where user actions are handled, and where events come from.

.. figure:: ../images/stream.svg

The *purple* parts are the implementation of the streaming functionality.
It starts from the :doc:`/mdbapi/songqueue` that provides a queue with all songs that shall be streamed.
The :meth:`mdbapi.stream.StreamingThread` gets the song at index 0 and streams it 
using the :class:`lib.stream.icecast.IcecastInterface` (See also :doc:`/lib/icecast`).

The :class:`lib.stream.icecast.IcecastInterface` then loads the audio file of the song that shall be streamed.
Loading, and at the same time transcoding, is done with :doc:`/lib/gstreamer`.
The :class:`lib.stream.gstreamer.GStreamerInterface` class provides the audio data as a stream of MP3 frames.
Those frames are read and analyzed with the :class:`lib.stream.mp3stream.MP3Stream` class
and then send to the `Icecast <https://icecast.org/>`_ server (*dark gray* box).

The *green* components are the interface to manage the behavior of the stream and to get its state.
Depending on the actions, the :class:`mdbapi.songqueue.SongQueue` or :class:`mdbapi.stream.StreamManager` class methods get called.
At the same time, the ``SongQueue`` as well as the ``StreamingThread`` can trigger events that will be propagated back to the WebUI.

Furthermore the *blue* components are involved in the streaming.
The :class:`mdbapi.randy.Randy` class is used to get random songs when the queue runs empty, or when the user wants to add a random song to the queue.

The ``StreamingThread`` informs the :doc:`/mdbapi/tracker` about new played songs and when songs were skipped.

