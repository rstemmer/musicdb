# MusicDB,  a music manager with web-bases UI that focus on music.
# Copyright (C) 2017 - 2021  Ralf Stemmer <ralf.stemmer@gmx.net>
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
All sections and options can be accessed by their names: ``MusicDBConfig(...).section.option``.

Details of the configurations possible for MusicDB can be found in :doc:`/basics/config`.

To create a new entry for the MusicDB Configuration the following steps must be done:

    #. Set the section and option in the configuration file as well as in the template in the share directory
    #. In case a new section shall be created, create an empty class for this section inside this module
    #. Read the option in the constructor of the :class:`~musicdb.lib.cfg.musicdb.MusicDBConfig` class

For example, the following option shall be added:

    .. code-block:: ini

        [newmod]
        enable = True

The option must be read inside the :class:`~musicdb.lib.cfg.musicdb.MusicDBConfig` ``__init__`` method.
The read value must be written into an attribute named as the option, inside an instance of the dummy class named liked the section:

    .. code-block:: python

        self.newmod = SECTION()
        self.newmod.enable = self.Get(bool, "newmod", "enable", False)

Now, the new option is available in the configuration object created using this class:

    .. code-block:: python

        cfg = MusicDBConfig("musicdb.ini")
        if cfg.newmod.enable:
            print("newmod enabled!")

"""

import logging
import grp
import pwd
import stat
from musicdb.lib.cfg.config import Config
from musicdb.lib.filesystem import Filesystem

class META:
    pass
class SERVER:
    pass
class WEBSOCKET:
    pass
class SOCKET:
    pass
class TLS:
    pass
class DATABASE:
    pass
class MUSIC:
    pass
class ARTWORK:
    pass
class VIDEOFRAMES:
    pass
class UPLOAD:
    pass
class EXTERN:
    pass
class TRACKER:
    pass
class ICECAST:
    pass
class LOG:
    pass
class DEBUG:
    pass
class RANDY:
    pass


class SECTION:
    pass

class MusicDBConfig(Config):
    """
    This class provides the access to the MusicDB configuration file.

    By default, the configuration will be read from ``/etc/musicdb.ini``.

    Args:
        path (str): Optional alternative configuration path. Default is ``/etc/musicdb.ini``
    """
    def __init__(self, path="/etc/musicdb.ini"):
        Config.__init__(self, path)
        self.fs = Filesystem("/")

        logging.info("Reading and checking MusicDB Configuration at \033[0;36m%s", path)

        # [meta]
        self.meta = META()
        self.meta.version           = self.Get(int, "meta",     "version",      1)
        if self.meta.version < 6:
            logging.warning("Version of \"%s\" is too old. Please update the MusicDB Configuration!", path)


        # [musicdb]
        self.musicdb = SECTION()
        self.musicdb.username       = self.Get(str, "musicdb",  "username",     "musicdb")
        self.musicdb.groupname      = self.Get(str, "musicdb",  "groupname",    "musicdb")
        try:
            pwd.getpwnam(self.musicdb.username)
        except KeyError:
            logging.warning("The user name \"%s\" for [musicdb]->username is not an existing UNIX user!", self.musicdb.username)
        try:
            grp.getgrnam(self.musicdb.groupname)
        except KeyError:
            logging.warning("The group name \"%s\" for [musicdb]->groupname is not an existing UNIX group!", self.musicdb.groupname)


        # [directories]
        self.directories = SECTION()
        self.directories.music      = self.GetDirectory("directories",  "music",    "/var/music")
        self.directories.data       = self.GetDirectory("directories",  "data",     "/var/lib/musicdb")
        self.directories.webdata    = self.directories.data + "/webdata"
        self.directories.uploads    = self.directories.data + "/uploads"
        self.directories.tasks      = self.directories.data + "/tasks"
        self.directories.state      = self.directories.data + "/state"
        self.directories.share      = "/usr/share/musicdb"
        self.directories.artwork    = self.directories.webdata + "/artwork"

        # files
        self.files = SECTION()
        self.files.webuiconfig      = self.directories.data + "/webui.ini"
        self.files.musicdatabase    = self.directories.data + "/music.db"
        self.files.trackerdatabase  = self.directories.data + "/tracker.db"
        self.files.defaultalbumcover= self.directories.artwork + "/default.jpg"
        self.files.webuijsconfig    = self.directories.webdata + "/config.js"


        # [log]
        self.log = SECTION()
        self.log.logfile            = self.Get(str, "log",      "logfile",      "journal")
        self.log.loglevel           = self.Get(str, "log",      "loglevel",     "WARNING").upper()
        if not self.log.loglevel in ["DEBUG", "INFO", "WARNING", "ERROR"]:
            logging.error("Invalid loglevel for [log]->loglevel. Loglevel must be one of the following: DEBUG, INFO, WARNING, ERROR")
        self.log.debugfile          = self.Get(str, "log",      "debugfile",    None)
        if self.log.debugfile == "/dev/null":
            self.log.debugfile = None
        self.log.ignore             = self.Get(str, "log",      "ignore",       None, islist=True)


        # [debug]
        self.debug = SECTION()
        self.debug.disablestats     = self.Get(bool, "debug",   "disablestats",     False)
        self.debug.disabletracker   = self.Get(bool, "debug",   "disabletracker",   False)
        self.debug.disableai        = self.Get(bool, "debug",   "disableai",        True)
        self.debug.disabletagging   = self.Get(bool, "debug",   "disabletagging",   False)
        self.debug.disableicecast   = self.Get(bool, "debug",   "disableicecast",   False)
        self.debug.disablevideos    = self.Get(bool, "debug",   "disablevideos",    False)


        # [websocket]
        self.websocket = SECTION()
        self.websocket.bind         = self.Get(str, "websocket",    "bind",         "127.0.0.1")
        self.websocket.port         = self.Get(int, "websocket",    "port",         9000)
        self.websocket.opentimeout  = self.Get(int, "websocket",    "opentimeout",  10)
        self.websocket.closetimeout = self.Get(int, "websocket",    "closetimeout",  5)
        self.websocket.apikey       = self.Get(str, "websocket",    "apikey",       None)
        if not self.websocket.apikey:
            logging.warning("Value of [websocket]->apikey is not set!")
        self.websocket.cert         = self.Get(str, "websocket", "cert", self.directories.data + "websocket.cert")
        self.websocket.key          = self.Get(str, "websocket", "key",  self.directories.data + "websocket.key")
        # The certificate and key files are validated in detail when MusicDB starts. No need to check them here.


        # [uploads]
        self.uploads = SECTION()
        self.uploads.allow          = self.Get(str, "uploads", "allow",         "artwork, songs", islist=True)
        

        # [tracker]
        self.tracker = SECTION()
        self.tracker.cuttime        = self.Get(int,  "tracker", "cuttime",      30)
        self.tracker.trackrandom    = self.Get(bool, "tracker", "trackrandom",  False)


        # [Icecast]
        self.icecast = SECTION()
        self.icecast.port           = self.Get(int, "Icecast",  "port",         6666)
        self.icecast.user           = self.Get(str, "Icecast",  "user",         "source")
        self.icecast.password       = self.Get(str, "Icecast",  "password",     None)
        self.icecast.mountname      = self.Get(str, "Icecast",  "mountname",    "/stream")


        # [randy]
        self.randy = SECTION()
        self.randy.nodisabled       = self.Get(bool, "randy",   "nodisabled",   True)
        self.randy.nohated          = self.Get(bool, "randy",   "nohated",      True)
        #self.randy.nohidden         = self.Get(bool, "randy",   "nohidden",     True) # TODO
        #self.randy.nobadaudio       = self.Get(bool, "randy",   "nobadaudio",   True) # TODO
        self.randy.minsonglen       = self.Get(int,  "randy",   "minsonglen",   120)
        self.randy.maxsonglen       = self.Get(int,  "randy",   "maxsonglen",   600)
        self.randy.songbllen        = self.Get(int,  "randy",   "songbllen",    50)
        self.randy.albumbllen       = self.Get(int,  "randy",   "albumbllen",   20)
        self.randy.artistbllen      = self.Get(int,  "randy",   "artistbllen",  10)
        self.randy.videobllen       = self.Get(int,  "randy",   "videobllen",   10)
        self.randy.maxblage         = self.Get(int,  "randy",   "maxblage",     24)
        self.randy.maxtries         = self.Get(int,  "randy",   "maxtries",     10)


        # [music]
        self.music = SECTION()
        ignorelist = self.Get(str, "music",    "ignoreartists","lost+found")
        ignorelist = ignorelist.split("/")
        self.music.ignoreartists = [item.strip() for item in ignorelist]

        ignorelist = self.Get(str, "music",    "ignorealbums", "")
        ignorelist = ignorelist.split("/")
        self.music.ignorealbums = [item.strip() for item in ignorelist]

        ignorelist = self.Get(str, "music",    "ignoresongs",  ".directory / desktop.ini / Desktop.ini / .DS_Store / Thumbs.db")
        ignorelist = ignorelist.split("/")
        self.music.ignoresongs = [item.strip() for item in ignorelist]


        # [albumcover]
        self.albumcover = SECTION()
        self.albumcover.scales          = self.Get(int, "albumcover",   "scales",   "50, 150, 500", islist=True)


        # [videoframes]
        self.videoframes = SECTION()
        self.videoframes.frames         = self.Get(int, "videoframes",  "frames",       "5")
        self.videoframes.previewlength  = self.Get(int, "videoframes",  "previewlength","3")
        self.videoframes.scales         = self.Get(str, "videoframes",  "scales",       "50x27, 150x83", islist=True)
        for scale in self.videoframes.scales:
            try:
                width, height   = map(int, scale.split("x"))
            except Exception as e:
                logging.error("Invalid video scale format in [videoframes]->scales: Expected format WxH, with W and H as integers. Actual format: %s.", scale)


        # [extern]
        self.extern = SECTION()
        self.extern.configtemplate  = self.GetFile( "extern",   "configtemplate","/usr/share/musicdb/extconfig.ini")
        self.extern.statedir        = self.Get(str, "extern",   "statedir",     ".mdbstate")
        self.extern.configfile      = self.Get(str, "extern",   "configfile",   "config.ini")
        self.extern.songmap         = self.Get(str, "extern",   "songmap",      "songmap.csv")


        # [music] # TODO: OLD -> REMOVE
        # TODO: REMOVE:
        self.music.owner            = self.Get(str, "music",    "owner",        "user")
        self.music.group            = self.Get(str, "music",    "group",        "musicdb")



    def GetDirectory(self, section, option, default):
        """
        This method gets a string from the configuration file and checks if it is an existing directory.
        If not it prints a warning.
        The \"invalid\" path will be returned anyway, because it may be OK that the directory does not exist yet.

        Args:
            section (str): Section of an ini-file
            option (str): Option inside the section of an ini-file
            default (str): Default directory path if option is not set in the file

        Returns:
            The value of the option set in the config-file or the default value.
        """
        path = self.Get(str, section, option, default)
        if not self.fs.IsDirectory(path):
            logging.warning("Value of [%s]->%s=%s does not address an existing directory.", section, option, path)
        return path



    def GetFile(self, section, option, default):
        """
        This method gets a string from the configuration file and checks if it is an existing file.
        If not it prints a warning.
        The \"invalid\" path will be returned anyway, because it may be OK that the file does not exist yet.
        
        Args:
            section (str): Section of an ini-file
            option (str): Option inside the section of an ini-file
            default (str): Default file path if option is not set in the file

        Returns:
            The value of the option set in the config-file or the default value.
        """
        path = self.Get(str, section, option, default)
        if not self.fs.IsFile(path):
            logging.warning("Value of [%s]->%s=%s does not address an existing file.", section, option, path)
        return path


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

