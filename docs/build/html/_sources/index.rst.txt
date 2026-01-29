.. MusicDB documentation master file, created by
   sphinx-quickstart on Sun Apr 23 13:41:48 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to MusicDB's documentation!
===================================

.. figure:: ./images/WebUI-3.2.0.jpg
   :align: center

   MusicDB WebUI. Artworks blurred for copyright reasons.

.. figure:: ./images/mdblogo.png
   :align: right

**MusicDB** is a music manager with focus on remote access to your music collection using a web-based user interface.
It allows you to manage an audio stream based on a song-queue.
The WebUI is focusing on being a presentation of your music rather than being a database front-end.

The music can be streamed by MusicDB and can be received by all kind of players like iTunes or VLC.
For streaming, MusicDB connects as source client to a local `Icecast <https://icecast.org/>`_ server.
This allows encrypted and protected streams so that they can be send out to the internet.
Your Music. Your Cloud.

The stream gets controlled by a WebUI that hides the ugliness of software behind a nice, music-oriented web front-end.
Your music gets presented and is not just a database entry in a boring list of artists and albums.

With MusicDB you control a queue of music that gets streamed.
There is no playlist-management and no repeating loop of songs. 
If you are lazy to fill the queue with new songs, a random songs get append to the queue.
This random song selector does not use cryptographic randomness.
It uses lots of constraints that the selection *feels random*.
So, recently played artists, albums and songs are blocked for a specific time until they can be added again.
Furthermore, only songs with a playtime within a configurable span will be append to prevent adding intros or "long-silent-songs".

MusicDB is for people who hate all other players. If there is another music player/manager you like (Beets, iTunes, Spotify, Ampache ...), you will probably hate this one ;)
In the :doc:`/basics/comparison` chapter is a comparison with tools similar to MusicDB.

The following user documentation will guide you through the installation process and the initial setup of MusicDB.

.. toctree::
   :maxdepth: 1
   :caption: User Documentation
   :glob:

   usage/install
   usage/import
   usage/music
   usage/webui
   usage/stream
   usage/*


------------------------------------

MusicDB has several abstraction layers shown in the following table:

+-------------------+-------------------+
| Bash Scripts      | HTML Documents    |
+-------------------+-------------------+
| MusicDB CLI       | MusicDB WebUI     |
+-------------------+-------------------+
| MusicDB API                           |
+-------------------+-------------------+
| MusicDB Libraries                     |
+-------------------+-------------------+
| Python            | Linux Tools       |
+-------------------+-------------------+

In the following chapters, the basic concepts and philosophy of MusicDB and its components are explained.
Furthermore usage guides for MusicDB and how to handle its environment are provided.
Those chapters are for users as well as for developers.

See the :doc:`/basics/concept` chapter and  :doc:`/basics/overview` to get an idea what it is like to use MusicDB.

.. toctree::
   :maxdepth: 1
   :caption: Concepts and Configuration
   :glob:

   basics/concept
   basics/config
   basics/security
   basics/data
   basics/definitions
   basics/overview
   basics/comparison

.. toctree::
   :maxdepth: 1
   :caption: Deeper Insight for Hackers
   :glob:

   basics/streaming
   basics/mods
   basics/development
   basics/distribution
   basics/webapi


MusicDB API
===========

The MusicDB API Classes are made to be used inside MusicDB or by command line modules.
These classes implement the features of MusicDB.
Their input will not be perfectly checks for sanity, so do not confront those classes with the wild.
Check user-inputs before applying them to these classes - This should be done in the MusicDB CLI modules.
The documentation for these classes are for developer.
Users may also want look at this documentation to understand whats behind the functionality.

If MusicDB has a feature, it is here. If there is no class providing a feature, the feature does not exist.

The next section lists some quick links to introductions for easy extending MusicDB.
Then a section with all API modules follows

Quick Development Start
-----------------------

Here are some links to places worth reading before starting with working on the MusicDB code:

   * An overview of the whole MusicDB Environment: :doc:`/basics/overview`
   * Adding a new column into the music database: :mod:`musicdb.lib.db.musicdb`
   * Creating a new command line module: :doc:`/basics/mods`
   * Adding a new option to the MusicDB Configuration: :mod:`musicdb.lib.cfg.musicdb`

The best way to start learning how a feature works is by starting reading the API module description.

.. toctree::
   :maxdepth: 1
   :caption: API Classes
   :glob:

   mdbapi/*



MusicDB Libraries
=================

These chapters document the low level classes and modules used by the MusicDB API classes.
This documentation is important for developer.
Those modules provide some abstractions mandatory for the functionality of all modules of MusicDB.
When developing a new module for MusicDB, never bypass these libraries!

.. toctree::
   :maxdepth: 1
   :caption: Libraries
   :glob:

   lib/*


MusicDB Task Management Modules
===============================

The MusicDB task management system is used to perform several tasks on the Music Database and Music Directory
triggered by the WebUI.

.. toctree::
   :maxdepth: 1
   :caption: Management Modules
   :glob:

   taskmanagement/*


MusicDB Maintaining Modules
===========================

The MusicDB Maintaining Modules take care that the file structure, databases and configurations
will stay valid.
With these modules, missing information will be created and invalid settings detected.
With each start of the MusicDB back-end, these modules check if the environment MusicDB is running in is still valid.

.. toctree::
   :maxdepth: 1
   :caption: Maintain Modules
   :glob:

   maintain/*


MusicDB Web User Interface
==========================

The documentation of the WebUI is not complete yet.

.. toctree::
   :maxdepth: 1
   :caption: JaveScript Classes
   :glob:

   webui/*


Other tools and Libraries
=========================

There are some external tools used by MusicDB's modules.
Whenever a method or function uses an external program, it is mentioned in the documentation.

``ID3Edit`` (optional):
   Is a tool that is used by MusicDB to edit and repair `ID3 Tags (no HTTPS) <http://id3.org/>`_ in mp3-files.
   Type ``id3edit --help`` for a short help. There is no more documentation yet, sorry.
   Source code can be found at `GitHub <https://github.com/rstemmer/id3edit>`_.

``FFmpeg`` (mandatory):
   Used for analyzing music files. `FFmpeg <https://www.ffmpeg.org/>`_ is used a lot by MusicDB for collecting
   all kind of information (like meta data or play-time) from music files.
   This is a mandatory dependency.

``gstreamer`` (mandatory):
   The `gstreamer <https://gstreamer.freedesktop.org/>`_ framework is used for providing the audio stream of music.
   It is used as interface to `Icecast <https://icecast.org/>`_.

``Icecast`` (optional, but highly recommended):
  `Icecast <https://icecast.org/>`_ is a streaming service that not just allows to provide an audio stream.
  It also come with user management and encryption so that the audio stream can be made private.

``SQLite`` (mandatory):
   All databases used and maintained by MusicDB are managed via `SQLite <sqlite>`_.


Third Party Resources
---------------------

The following free third party components are included in MusicDB WebUI:

   * `Source Sans Pro <https://github.com/adobe-fonts/source-sans-pro>`_ and `Source Serif Pro <https://github.com/adobe-fonts/source-serif-pro>`_
   * `DejaVuSans <https://github.com/dejavu-fonts/dejavu-fonts>`_


Indices and tables
==================

   * :ref:`genindex`
   * :ref:`modindex`

.. toctree::
   :maxdepth: 1
   :caption: Other
   :glob:

   other/*

