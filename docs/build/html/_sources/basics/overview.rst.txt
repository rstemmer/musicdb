Overview of MusicDB
===================

The following graph shows a complete overview of MusicDB's information flow through all its components.

.. figure:: ../images/Map.svg

In the following sections, I describe the tasks of each block and how the interact with each other.
The sections represent the colors of the rectangles and arrows, that represent the components of the environment of MusicDB.


Music Information (Purple)
--------------------------

There are two main paths (bold purple arrows) the data of the music collections goes to reach the listener.
One path is for the audio part the listener wants to hear,
the other path is for the information the listener wants to see when he listens to a song or manages the queue of songs that will be played in future.

Starting at the music collection where all music files are stored, **the audio part** goes straight up to the audio streaming server `Music Player Daemon (MPD) <https://musicpd.org/>`_.
MPD reads the music files and streams them to a client that can receive audio streams.
For example VLC, iTunes or the Windows Media Player.
If you stream into the internet, you may want to use `Icecast <https://icecast.org/>`_ for encrypting the steam.
Icecast would be placed on server side right behind MPD.

The second main path is **the meta data path**.
The music files get read by `MusicDB Components (Green)`_ and meta data will be cached in the `Music Database`_
Those meta data will be served by the MusicDB WebSocket Server to the clients web browser.
Meta data are for example the names of the songs, albums and artists.
Genres associated to songs and albums, and other information.

There are two further paths towards the `HTTP Server (Black)`_ component.
The audio files that will be directly accessed from the music collection is for prelistening to songs in the WebUI.
And the image files of the album artworks, cached and scaled by MusicDB in the `Artwork Cache`_

**Conclusion:**

   * Audio goes through MPD to the clients audio player
   * Artwork will be processed by MusicDB and gets served by an HTTP Server
   * Meta data are cached in the Music Database and gets served via WebSockets by the MusicDB WebSocket Server


Music Player Daemon (Cyan)
--------------------------

The `Music Player Daemon (MPD) <https://musicpd.org/>`_ streams the music to the clients.
The MPD process is strict bound to MusicDB, this is why the configuration is stored in the MusicDB data directory.
MusicDB will not work correctly when using a MPD process that does not use the configuration optimized to the MusicDB working environment.
So by using a configuration separated from the operating systems default configuration allows the user to use this instance of MPD in parallel to another instance you may already use.
The MPD process gets controlled by the MusicDB WebSocket Server and should not be influenced by other clients like *mpc*.

The documentation of how MusicDB accesses MPD can be found here: :doc:`/mdbapi/mpd`.

**Conclusion:**

   * Music Player Daemon provides the audio stream.


MusicDB Components (Green)
--------------------------

MusicDB itself can be divided into three parts: The WebUI, the WebSocket Server and the Command-Line Modules.

The **MusicDB WebUI** is the front end part of MusicDB.
It is written in JavaScript and gets executed on the client side.
A WebSocket connection gets established to communicate with the MusicDB Server using the :doc:`/basics/webapi`.
The WebUI allows the user to interact with the audio stream by adding, removing or moving songs in the queue of songs to play in future.
Furthermore the WebUI shows all kind of information of the music currently playing and the music collection.

The server side of MusicDB are the **MusicDB Command-Line Modules**.
They are the core of MusicDB.
These modules manage the `Music Database`_ and the `Artwork Cache`_.
Details of the modules can be found in the :doc:`/basics/mods` documentation.
One special module is the WebSocket Server module.

While the other modules are simple tools that get executed, do their job, and exit, 
the **MusicDB WebSocket Server** module runs permanent to serve
information to the WebUI.
Details of how the server works can be found in the :doc:`/mdbapi/server` documentation.

**Conclusion:**

   * MusicDB is a WebUI, Command-line tools and a WebSocket server

In the following subsections, some important information storage (Blue) gets describes.

Music Database
^^^^^^^^^^^^^^

The Music Database is the central storage for information of music.
It is a cache for the artist, album and song names.
Furthermore the database contains information associated with the albums and songs like genre tags, mood flags and lyrics.
A detailed explanation of the database can be found in the :doc:`/lib/musicdb` documentation.

MusicDB Data & Configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Beside the music database, there are lots of other data in the MusicDB data directory.
For example the :doc:`/basics/config` and the database of the :doc:`/mdbapi/tracker`.
There are also files storing the state of the server (selected genres) and allowing controlling the server via :doc:`/lib/namedpipe`

Artwork Cache
^^^^^^^^^^^^^

The artwork cache contains all albums artworks and scaled version of those artworks managed by the :doc:`/mdbapi/artwork`.


HTTP Server (Black)
-------------------

To serve the WebUI files to the client, a HTTP server is needed.
In the setup shown in the figure above, `Apache <https://httpd.apache.org/>`_ is used.
The HTTP server needs to have access to the audio files, artwork cache and the MusicDB WebUI files.
The audio file access is needed by the WebUI to provide the possibility to listen to a single song without having it add to the queue.
Of course it can also be used to serve the documentation.
The HTTP server is not bound to MusicDB in the way MPD is.
So Apache can be replaced by any other web server.

**Conclusion:**

   * The HTTP server serves the WebUI, artwork, and audio files.


