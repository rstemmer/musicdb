Overview of MusicDB
===================

The following graph shows a complete overview of MusicDB's information flow through all its components.
It shows what happens with the music and its annotated information like the meta data and artworks.
Furthermore the image shows how everything is connected and how MusicDB integrates in the system.

.. figure:: ../images/Map2_1.svg

In the following sections, I describe the tasks of each block and how the interact with each other.
The sections represent the colors of the rectangles and arrows, that represent the components of the environment of MusicDB.


Music Information (Purple)
--------------------------

There are two main paths (bold purple arrows) the data of the music collections goes to reach the listener.
One path is for the audio part the listener wants to hear,
the other path is for the information the listener wants to see when he listens to a song or manages the queue of songs that will be played in future.

Everything starts with the users music collection shown in the bottom left corner.
This collection is the source of all information MusicDB works with.
As the arrow shows, MusicDB will never change anything in the users files.

MusicDB Data (Blue)
-------------------

The music files get read by `MusicDB Components (Green)`_.
At this point, the Music Collection gets split in three separate kind of information:
The `Artwork Cache`_ for the artworks, the `MP3 Cache`_ for the audio and the `Music Database`_ for the meta data.

Music Database
^^^^^^^^^^^^^^

The Music Database is the central storage for information of music.
It is a cache for the artist, album and song names.
Furthermore the database contains information associated with the albums and songs like genre tags, mood flags and lyrics.
A detailed explanation of the database can be found in the :doc:`/lib/musicdb` documentation.

Artwork Cache
^^^^^^^^^^^^^

The artwork cache contains all albums artworks and scaled version of those artworks managed by the :doc:`/mdbapi/artwork`.

MusicDB Data & Configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Beside the music database, there are lots of other data in the MusicDB data directory.
For example the :doc:`/basics/config` and the database of the :doc:`/mdbapi/tracker`.
There are also files storing the state of the server (selected genres) and allowing controlling the server via :doc:`/lib/namedpipe`


MusicDB Components (Green)
--------------------------

MusicDB itself can be divided into three parts: The `MusicDB WebUI`_, the `MusicDB Server` and the `Command-Line Modules`_.

Command-Line Modules
^^^^^^^^^^^^^^^^^^^^

The command line modules provide the interface from the users music collection to the MusicDB world.
These modules manage the `Music Database`_, the `Artwork Cache`_ and many more.
Details of the modules can be found in the :doc:`/basics/mods` documentation.
One special module is the `MusicDB Server`_ module that will be described later in this section.

MusicDB WebUI
^^^^^^^^^^^^^

The MusicDB WebUI is the front end part of MusicDB.
It is written in JavaScript and gets executed on the client side.
A WebSocket connection gets established to communicate with the `MusicDB Server`_ using the :doc:`/basics/webapi`.
The WebUI allows the user to interact with the audio stream by adding, removing or moving songs in the queue of songs to play in future.
Furthermore the WebUI shows all kind of information of the music currently playing and the music collection.

MusicDB Server
^^^^^^^^^^^^^^

While the other modules are simple tools that get executed, do their job, and exit, 
the MusicDB Server module runs permanent to serve information to the WebUI via :doc:`/basics/webapi`,
and to provide an audio stream.
Details of how the server works can be found in the :doc:`/mdbapi/server` and :doc:`/mdbapi/stream` documentation.


External Servers (Black)
------------------------

There are two external tools involved in the MusicDB setup.
The `HTTP Server`_ serves the `MusicDB WebUI`_.
The `Icecast Server`_ manages the audio stream provided by the `MusicDB Server`_

HTTP Server
^^^^^^^^^^^

To serve the WebUI files to the client, a HTTP server is needed.
In the setup shown in the figure above, `Apache <https://httpd.apache.org/>`_ is used.
The HTTP server needs to have access to the audio files, artwork cache and the MusicDB WebUI files.
The audio file access is needed by the WebUI to provide the possibility to listen to a single song without having it add to the queue.
Of course it can also be used to serve the documentation.
The HTTP server is not bound to MusicDB in the way MPD is.
So Apache can be replaced by any other web server.

Icecast Server
^^^^^^^^^^^^^^

The `Icecast <https://icecast.org/>`_ server gets the audio data from the `MusicDB Server`_ and provides additional encryption and user management based protection to the stream.
From the point of view from Icecast, MusicDB is a Source Client.
More details are documented in the :doc:`/lib/icecast` documentation.

Consuming Music (Orange)
------------------------

At the top of the figure, all information streams come together to the user.
The user can see and control the audio stream using a web browser.
To listen to the stream the user can connect with any media player that can receive mp3 audio streams.

