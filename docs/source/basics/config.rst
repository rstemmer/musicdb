
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

cache (path to directory):
   This is the place where MusicDB caches all songs as clean tagged mp3 files.
   
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


MusicAI
-------

modelpath (path to directory):
   Directory where the models and training data are stored

tmppath (path to directory):
   A path to store temporary data.

logpath (path to directory):
   Path for logfiles of training runs

spectrogrampath (path to directory):
   Temporary path for generated spectrograms
   This path should survives reboots.
   Because the data generation takes much time,
   it is better to have a "backup" of the temporary data.
   So, they must not be generated again after changes or crashes.
   If the model is trained, they can be removed.

genrelist (a list of genrenames):
   These are the genres the AI will use.
   They must have the same name as they are listed in the database.
   **Once this value is set, it should never be changed because it destroys the datasets and models the list was used for.**
   **This entry is bound to the model name**

modelname (string):
   Name of the model.
   **This entry is bound to the genre list.**
   All data is bound to the model name.
   Different CDNNs can be trained/used by changing this name.

slicesize (number ∈ ℕ):
   Size of a slice of a spectrogram to work with

epoch (number ∈ ℕ):
   Number of epoch for the training

batchsize (number ∈ ℕ):
   Size of one training batch - This should be as much as the GPUs Memory can hold, but not one byte more.

usegpu (boolean):
   Can be used to disable using the GPU - Not recommended!


Randy
-----

nodisabled (boolean):
   If ``true`` no disabled songs will be chosen

nohated (boolean):
   If ``true`` no hated songs will be chosen

minsonglen (number ∈ ℕ):
   Determines the minimum length of a song in seconds to be in the set of possible songs

songbllen (number ∈ ℕ):
   Blacklist length for songs (``0`` to disable the blacklist)

albumbllen (number ∈ ℕ):
   Blacklist length for albums (``0`` to disable the blacklist)

artistbllen (number ∈ ℕ):
   Blacklist length for artists (``0`` to disable the blacklist)

maxage (time in hours as integer):
   The highest age an entry in one of the three blacklist can have until it gets automatically removed.


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
   At least ``requests, urllib3, PIL, tensorflow`` is recommended


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


