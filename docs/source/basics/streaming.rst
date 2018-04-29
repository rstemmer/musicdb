
MusicDB Stream
==============

This is the overall documentation of the streaming process in MusicDB

For streaming, two major open source projects are involved.
Reading and transcoding the audio files is done by the `GStreamer Framework<https://gstreamer.freedesktop.org>`_.
Streaming the done using `Icecast <https://icecast.org/>`_.

The following graph shows the data flow from the audio file to the listener:

.. graphviz::

   digraph hierarchy {
      size="5,8"

      files       [shape=box, style=filled, fillcolor="#adc5e7", label="Audio files\n(mp3, m4a, flac)"]
      gstreamer   [shape=box, style=filled, fillcolor="#8ccfb7", label="GStreamer"]
      mp3stream   [shape=box, style=filled, fillcolor="#8ccfb7", label="MP3 stream\n(mp3)"]
      icecast     [shape=box, style=filled, fillcolor="#cccccc", label="Icecast"]
      listener    [shape=box, style=filled, fillcolor="#fedcc6", label="Listener"]

      files     -> gstreamer [label="Using GStreamer\nfilesrc element"]
      gstreamer -> mp3stream [label="Using GStreamer\nfdsink element"]
      mp3stream -> icecast   [label="Using libshout"]
      icecast   -> listener  [label="via HTTP"]

   }

The meaning of the background colors are similar to the :doc:`/basics/overview` image.
Blue are MusicDB related files.
Green are MusicDB modules, gray external server programs, and yellow are tools for the user.

The audio files get read by the MusicDB server using the `GStreamer Framework<https://gstreamer.freedesktop.org>`_.
GStreamer decodes the files and encodes it into the mp3 format.
Details about this process is described in :mod:`/lib/mp3transcoder` documentation.

After transcoding, the mp3 frames gets read and processed by the :doc:`/lib/mp3stream`.
Then each mp3 frame gets send to the `Icecast <https://icecast.org/>`_ process using *libshout*

The audio stream provided by Icecast can new be received by any multimedia player that can connect to audio streams.

