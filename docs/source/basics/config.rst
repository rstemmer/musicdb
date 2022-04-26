
MusicDB Configuration
=====================

The following sections represent the sections of the MusicDB Configuration file.
The data structure for that some basic settings are mentioned here is documented at :doc:`/basics/data`.

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


musicdb
-------

username (string with UNIX user name):
   This is the user configured to run the MusicDB websocket server.
   This must match the systemd unit file settings.

groupname (string with UNIX group name):
   This is the group configured under which the MusicDB websocket server runs.
   This must match the systemd unit file settings.



directories
-----------

For details see :doc:`/basics/data`.

music (directory path):
   This is the place where the music files are expected.

data (directory path):
   This is the directory used by MusicDB to store internal data.
   The databases, artworks and states of MusicDB and the WebUI are stored at this place.



websocket
---------

Please keep in mind that websockets are secured.
TLS is always enabled.
So, the protocol is ``wss``.

bind (IP address):
   The address the server is listening to.
   For example, ``0.0.0.0`` for global listening.
   After installation, this address is set to ``127.0.0.1`` so that the server cannot be addressed from the internet accidentally 

port (socket port):
   The number of the port, the server is listening on.
   Because MusicDB is executed as non-root user, the port number must be above ``1024``.

   After changing the port number, you also have to update the ``config.js`` file in the ``webdata`` directory.
   The default path is ``/var/lib/musicdb/webdata/config.js``, so that the MusicDB WebUI knows which number to use.

opentimeout (time in seconds):
   Time until the connection to the websocket server raises a timeout exception

closetimeout (time in seconds):
   Time until the disconnection process of the websocket server raises a timeout exception

apikey (base64 encoded key):
   A key that is used to identify clients that are allowed to use the websocket interface.

cert (path to SSL Certificate file):
   File to the certificate used for the TLS secured websockets

key (path to SSL Key file):
   File of the key for the certificate



music
-----

ignoreartists (/ separated list of directory names):
   Ignore these directory names when looking for artists

ignorealbums (/ separated list of directory names):
   Ignore these directory names when looking for albums

ignoresongs (/ separated list of file names):
   Ignore these files names when looking for songs



albumcover
----------

scales (list of numbers ∈ ℕ):
   A list of scales that will be used to create thumbnails. 
   At least ``"150, 200, 500, 1000"`` should appear in the list because those are used by the MusicDB WebUI

   

videoframes
-----------

frames (numbers ∈ ℕ):
   Amount of frames used for a preview animation

scales (list of in format "XxY" where X,Y ∈ ℕ and "x" the lower case character x):
   A list of scales that will be used to create thumbnails. 
   At least ``"150x83"`` should appear in the list because those are used by the MusicDB WebUI

previewlength (seconds ∈ ℕ):
   Length of the preview in seconds.



uploads
-------

allow (list of strings):
   If not empty users are allowed to upload files of certain categories.
   The categories are defined in that list.
   The default is ``allow=artwork, albumfiles``.

   The following categories exist:

   -  artwork: Album artwork
   -  albumfiles: Song files, booklets and other files that are related to a music album.

   .. warning::

      The WebUI does not know about this settings and assumes that uploads are possible.
      So when setting this to ``False``, the WebUI still provided the UI elements.
      The server just rejects all attempts to upload files.
      This of course will be reflected by a meaningful error message in the WebUI.



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

cuttime (integer, time in minutes):
   Time until a relation gets cut.
   If there is a time gap of *cuttime* minutes or more between the current played song and the previous one,
   the relationship gets ignored.

trackrandom (boolean ∈ {True, False}):
   If set to ``True``, the tracker tracks also random song.
   Otherwise the song gets ignored.

   A detailed description of the behavior can be found in the documentation of the tracking algorithm:
   :meth:`musicdb.mdbapi.tracker.Tracker.Track`.


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



log
---

logfile (path to file):
   Output for the logs. Can also be ``stdout``, ``stderr`` or ``journal``

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

disablestats (number ∈ {True, False}):
   Ignore statistic changes for songs (Like, Dislike…).
   They will not be written to the database.

disabletracker (number ∈ {True, False}):
   Do not track the songs that were played

disableai (number ∈ {True, False}):
   Do not use AI related things.
   On weak computers this should be ``True``.

disabletagging (number ∈ {True, False}):
   Do not set or remove any tags for songs or albums

disableicecast (number ∈ {True, False}):
   Do not try to connect to an IceCast server

disablevideos (number ∈ {True, False}):
   Disable the support for music videos.
   This is ``True`` (disabled) by default.
   Currently, the Music Video feature is in beta state.

