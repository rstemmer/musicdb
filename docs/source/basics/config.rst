
MusicDB Configuration
=====================

The following sections represent the sections of the MusicDB Configuration file.
The sections have the following structure:

option (type):
   description

meta
----

version (integer):
   This is the version number of configuration.
   This number is used *internal* to check if the configuration file provides the sections and key expected by MusicDB.
   When new sections or keys are added (or old ones removed), the version number gets incremented.
   After updating MusicDB compare your configuration with the new one and update the file by yourself (including the version number)

server
------

pidfile (path to file):
   This is the place where the PID file gets placed

statedir (path to a directory):
   In this directory the current global state of MusicDB is stored.
   More details can be found in the documentation for the state-file: :mod:`~lib.cfg.mdbstate`

fifofile (path to file):
   This file will be used to communicate with the WebSocket servers internals.
   Read :doc:`/mod/server` for details.

webuiconfig (path to file):
   Configuration file for the WebUI.
   Here, settings done inside the WebUI are stored.

websocket
---------

Please keep in mind that websockets are secured.
TLS is always enabled.
So, the protocol is ``wss``.

address (URL / IP address):
   The address the server is listening to.
   For example, ``0.0.0.0`` for global listening.

port (socket port):
   The number of the port, the server is listening on.

   Here are some lists with restricted ports:

      * `FireFox <https://www-archive.mozilla.org/projects/netlib/PortBanning.html#portlist>`
      * `Chrome <https://src.chromium.org/viewvc/chrome/trunk/src/net/base/net_util.cc?view=markup>`

url (URL):
   **TODO**

opentimeout (time in seconds):
   Time until the connection to the websocket server raises a timeout exception

closetimeout (time in seconds):
   Time until the disconnection process of the websocket server raises a timeout exception

key (base64 encoded key):
   A key that is used to identify clients that are allowed to use the websocket interface.

TLS
---

cert (path to SSL Certificate file):
   File to the certificate used for the TLS secured websockets

key (path to SSL Key file):
   File of the key for the certificate

database
--------

path (path to file):
   Path to the MusicDB Database file

music
-----

path (path to directory):
   Path to the music collection.
   In this directory, the Artist-directories are stored.

owner (UNIX user name):
   Name of the user that shall be the owner of the music files

group (UNIX group name):
   Name of the group that shall be the owner of the music files

ignoreartists (/ separated list of directory names):
   Ignore these directory names when looking for artists

ignorealbums (/ separated list of directory names):
   Ignore these directory names when looking for albums

ignoresongs (/ separated list of file names):
   Ignore these files names when looking for songs
   
artwork
-------

path (path to directory):
   Path to the artwork root directory where all artworks are stored at

scales (list of numbers ∈ ℕ):
   A list of scales that will be used to create thumbnails. 
   At least ``"50, 150, 500"`` should appear in the list because those are used by the MusicDB WebUI

manifesttemplate (path to file):
   Name of the template for the manifest file to tell the browser to cache the artwork

manifest (path to file):
   Name where the manifest file to tell the browser to cache the artwork will be generated at

videoframes
-----------

path (path to directory):
   Path to the video frames root directory where all artworks are stored at

frames (numbers ∈ ℕ):
   Amount of frames used for a preview animation

scales (list of numbers ∈ ℕ):
   A list of scales that will be used to create thumbnails. 
   At least ``"50, 150, 500"`` should appear in the list because those are used by the MusicDB WebUI

previewlength (seconds ∈ ℕ):
   Length of the preview in seconds.

uploads
-------

allow (boolean):
   If ``True`` users are allowed to upload artworks.

   .. warning::

      The WebUI does not know about this settings an assumes that uploads are possible.
      So when setting this to ``False``, the WebUI still provided the UI elements.
      The server just rejects all attempts to upload files.

path (path to directory):
   Path to the directory for temporary uploads and meta data

extern
------

configtemplate (path to file):
   Path to the template configuration for external storages

statedir (directory name):
   Name of the directory on an external storage in that the configuration and state file is stored

configfile (filename):
   Name of the configuration file inside the state directory

songmap (filename):
   Name of the map-file of the stored music


tracker
-------

dbpath (path to file):
   Path to the tracker database

cuttime (integer, time in minutes):
   Time until a relation gets cut.
   If there is a time gap of *cuttime* minutes or more between the current played song and the previous one,
   the relationship gets ignored.


lycra
-----

dbpath (path to file):
   Path to the database the lyrics will be cached at


Icecast
-------

The default values all match the default Icecast configuration provided by MusicDB.
The password got generated during the installation process and can be considered as secure.
The only reason to change something in this section is, that the Icecast server gets shared with multiple sources.

port (number ∈ ℕ):
   Port where Icecast is listening at.
   This is the none SSL secured port.

user (string):
   This is the *source user* MusicDB uses to connect to Icecast.
   By default, ``source`` is the user name.

password (string):
   The password MusicDB needs to authenticate as a valid source for the Icecast server.
   The default password was generated during the installation process of MusicDB and is secure.

mountname (string starting with ``/``):
   This is the name of the mount MusicDB uses.


Randy
-----

nodisabled (boolean):
   If ``true`` no disabled songs will be chosen

nohated (boolean):
   If ``true`` no hated songs will be chosen

minsonglen (number ∈ ℕ):
   Determines the minimum length of a song in seconds to be in the set of possible songs

maxsonglen (number ∈ ℕ):
   Determines the maximum length of a song in seconds to be in the set of possible songs

songbllen (number ∈ ℕ):
   Blacklist length for songs (``0`` to disable the blacklist)

albumbllen (number ∈ ℕ):
   Blacklist length for albums (``0`` to disable the blacklist)

artistbllen (number ∈ ℕ):
   Blacklist length for artists (``0`` to disable the blacklist)

videobllen (number ∈ ℕ):
   Blacklist length for videos (``0`` to disable the blacklist)

maxblage (time in hours as integer):
   The highest age an entry in one of the three blacklist can have until it gets automatically removed.

maxtries (number ∈ ℕ):
   Maximum amount of tries to find a valid random songs.
   This prevents spending infinite amount of time getting a song even if the data base does not provide enough songs.


log
---

logfile (path to file):
   Output for the logs. Can also be ``stdout`` or ``stderr``

loglevel (Loglevel name):
   Log level to run the logger at. Can be one of the following: ``INFO``, ``WARNING``, ``ERROR``

debugfile (path to file):
   File to also store all logs at log level ``DEBUG``.
   If no file shall be created, use ``none``

ignore (list of python module names):
   List of modules to ignore in the logs.
   At least ``requests, urllib3, PIL`` is recommended


debug
-----
These flags can be used to prevent damage or messing up data while debugging or testing.
Furthermore, it can be used to disable some features that do not work.

disablestats (number ∈ {0,1}):
   Ignore statistic changes for songs (Like, Dislike…).
   They will not be written to the database.

disabletracker (number ∈ {0,1}):
   Do not track the songs that were played

disableai (number ∈ {0,1}):
   Do not use AI related things.
   On weak computers this should be ``1``.

disabletagging (number ∈ {0,1}):
   Do not set or remove any tags for songs or albums

disableicecast (number ∈ {0,1}):
   Do not try to connect to an IceCast server

disablevideos (number ∈ {0,1}):
   Disable the support for music videos.
   This is ``1`` (disabled) by default.
   Currently, the Music Video feature is in beta state.

