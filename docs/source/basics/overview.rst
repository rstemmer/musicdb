Overview of MusicDB
===================

The following figure shows a complete overview of MusicDB and how it is integrated into the operating system.
It shows what happens with the music and its annotated information like the meta data and artworks.
Furthermore the image shows how the client applications are connected to the server.

.. figure:: ../images/overview.svg

In the following sections, I describe the purpose of each block and how the interact with each other.
The sections represent the colors of the rectangles and arrows, that represent the components of the environment of MusicDB.


MusicDB (Green)
---------------

MusicDB is split into two applications.
The *MusicDB Server* as back-end and the *MusicDB WebUI* as front-end.

MusicDB Server
^^^^^^^^^^^^^^

The MusicDB Server runs as daemon on the server. The daemon is managed via `systemd <https://systemd.io/>`_.
For streaming, the MusicDB Server connects to an `Icecast <https://icecast.org/>`_ server.
In this figure, Icecast is executed on the same server as MusicDB.
It is also possible to connect to a remote Icecast server.

MusicDB WebUI
^^^^^^^^^^^^^

The second part of MusicDB is the MusicDB WebUI (or only WebUI).
This is a JavaScript application being executed in the clients web browser.
Beside other data this application gets served by a HTTP server.
A WebSocket connection gets established to communicate with the MusicDB Server using the :doc:`/basics/webapi`.


External Servers (Black)
------------------------

There are two external tools involved in the MusicDB setup.
The HTTP Server serves the MusicDB WebUI.
The Icecast Server manages the audio stream provided by the MusicDB Server.

HTTP Server
^^^^^^^^^^^

To serve the WebUI files to the client, a HTTP server is needed.
In the setup shown in the figure above, `Apache <https://httpd.apache.org/>`_ is used.
The HTTP server needs to have access to the audio files, artwork cache and the MusicDB WebUI files.
The audio file access is needed by the WebUI to provide the possibility to listen to a single song without having it add to the queue.
Of course it can also be used to serve the documentation.

Icecast Server
^^^^^^^^^^^^^^

The `Icecast <https://icecast.org/>`_ server gets the audio data from the MusicDB Server and provides additional encryption and user management based protection to the stream.
From the point of view from Icecast, MusicDB is a Source Client.
More details are documented in the :doc:`/lib/icecast` documentation.


Music Information (Purple)
--------------------------

There are two main paths (purple arrows) the data of the music collections goes to reach the listener.
One path is the audio stream that is managed by the MusicDB server.
The other path through the HTTP server is a direct access to the music files so that the user can "preview" singe files.

The primary way a user listens to music via MusicDB is through streams.
To provide a continuous stream of music, MusicDB reads the music files from the Music Directory (Purple)
and sends the audio data to an `Icecast <https://icecast.org/>`_ server.
The Icecast server then provides the stream to any Audio Player including the users Web Browser.
Details can be found at :doc:`/basics/streaming`.

If the user wants to listen into a song directly, the WebUI provides a preview feature.
The audio file can then be played in the browser without adding it into the stream.
Therefore the HTTP server needs to have read access to the Music Directory.
See :doc:`/usage/install` on how to setup the HTTP server.


MusicDB Data (Blue)
-------------------

Beside the music itself MusicDB manages lots of other data.
For example meta data from the music files, annotated information by the user and also album artworks.


Music Database
^^^^^^^^^^^^^^

The Music Database is the central storage for information of music.
It is a cache for the artist, album and song names.
Furthermore the database contains information associated with the albums and songs like genre tags, mood flags and lyrics.
A detailed explanation of the database can be found in the :doc:`/lib/musicdb` documentation.

Artwork Cache
^^^^^^^^^^^^^

The artwork cache contains all albums artworks and scaled version of those artworks managed by the :doc:`/mdbapi/artwork`.


