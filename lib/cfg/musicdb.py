# MusicDB,  a music manager with web-bases UI that focus on music.
# Copyright (C) 2017  Ralf Stemmer <ralf.stemmer@gmx.net>
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

To create a new entry for the MusicDB Configuration the following steps must be done:

    #. Set the section and option in the configuration file as well as in the template in the share directory
    #. In case a new section shall be created, create an empty class for this section inside this module
    #. Read the option in the constructor of the :class:`~lib.cfg.musicdb.MusicDBConfig` class

For example, the following option shall be added:

    .. code-block:: ini

        [newmod]
        enable = True

Then, first a new dummy class named ``NEWMOD`` must be added:

    .. code-block:: python

        class NEWMOD:
            pass

Finaly, the option must be read inside the :class:`~lib.cfg.musicdb.MusicDBConfig` ``__init__`` method.
The read value must be writen into an attribute named as the option, inside an instance of the dummy class named liked the section:

    .. code-block:: python

        self.newmod = NEWMOD()
        self.newmod.enable = self.Get(bool, "newmod", "enable", False)

Now, the new option is availabe in the configuration object created using this class:

    .. code-block:: python

        cfg = MusicDBConfig("musicdb.ini")
        if cfg.newmod.enable:
            print("newmod enabled!")

"""

import logging
import grp
import pwd
from lib.cfg.config import Config
from lib.filesystem import Filesystem

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
class EXTERN:
    pass
class TRACKER:
    pass
class LYCRA:
    pass
class ICECAST:
    pass
class LOG:
    pass
class DEBUG:
    pass
class RANDY:
    pass

class MusicDBConfig(Config):
    """
    This class provides the access to the MusicDB configuration file.
    """
    def __init__(self, filename):
        Config.__init__(self, filename)
        self.fs = Filesystem("/")

        logging.info("Reading and checking MusicDB Configuration")

        # [meta]
        self.meta = META()
        self.meta.version           = self.Get(int, "meta",     "version",      1)
        if self.meta.version < 2:
            logging.warning("Version of musicdb.ini is too old. Please update the MusicDB Configuration!")


        # [server]
        self.server = SERVER()
        self.server.pidfile         = self.Get(str, "server",   "pidfile",      "/opt/musicdb/data/musicdb.pid")
        self.server.statedir        = self.Get(str, "server",   "statedir",     "/opt/musicdb/data/mdbstate")
        self.server.fifofile        = self.Get(str, "server",   "fifofile",     "/opt/musicdb/data/musicdb.fifo")


        # [websocket]
        self.websocket = WEBSOCKET()
        self.websocket.address      = self.Get(str, "websocket","address",      "127.0.0.1")
        self.websocket.port         = self.Get(int, "websocket","port",         9000)
        self.websocket.url          = self.Get(str, "websocket","url",          "wss://localhost:9000")
        self.websocket.opentimeout  = self.Get(int, "websocket","opentimeout",  10)
        self.websocket.closetimeout = self.Get(int, "websocket","closetimeout",  5)
        self.websocket.apikey       = self.Get(str, "websocket","apikey",       None)
        if not self.websocket.apikey:
            logging.warning("Value of [websocket]->apikey is not set!")


        # [TLS]
        self.tls = TLS()
        self.tls.cert               = self.GetFile( "tls",      "cert",         "/dev/null")
        self.tls.key                = self.GetFile( "tls",      "key",          "/dev/null")
        if self.tls.cert == "/dev/null" or self.tls.key == "/dev/null":
            logging.warning("You have to set a valid TLS certificate and key!")


        # [database]
        self.database = DATABASE()
        self.database.path          = self.GetFile( "database", "path",         "/opt/musicdb/data/music.db")


        # [music]
        self.music = MUSIC()
        self.music.path             = self.GetDirectory("music",    "path",     "/var/music")
        self.music.owner            = self.Get(str, "music",    "owner",        "user")
        self.music.group            = self.Get(str, "music",    "group",        "musicdb")
        try:
            pwd.getpwnam(self.music.owner)
        except KeyError:
            logging.warning("The group name for [music]->owner is not an existing UNIX user!")
        try:
            grp.getgrnam(self.music.group)
        except KeyError:
            logging.warning("The group name for [music]->group is not an existing UNIX group!")

        ignorelist = self.Get(str, "music",    "ignoreartists","lost+found")
        ignorelist = ignorelist.split("/")
        self.music.ignoreartists = [item.strip() for item in ignorelist]

        ignorelist = self.Get(str, "music",    "ignorealbums", "")
        ignorelist = ignorelist.split("/")
        self.music.ignorealbums = [item.strip() for item in ignorelist]

        ignorelist = self.Get(str, "music",    "ignoresongs",  ".directory / desktop.ini / Desktop.ini / .DS_Store / Thumbs.db")
        ignorelist = ignorelist.split("/")
        self.music.ignoresongs = [item.strip() for item in ignorelist]


        # [artwork]
        self.artwork = ARTWORK()
        self.artwork.path           = self.GetDirectory("artwork",  "path",     "/opt/musicdb/data/artwork")
        self.artwork.scales         = self.Get(int, "artwork",  "scales",       "50, 150, 500", islist=True)
        for s in [50, 150, 500]:
            if not s in self.artwork.scales:
                logging.error("Missing scale in [artwork]->scales: The web UI expects a scale of %d (res: %dx%d)", s, s, s)
        self.artwork.manifesttemplate=self.GetFile( "artwork",  "manifesttemplate", "/opt/musicdb/server/manifest.txt", logging.warning) # a missing manifest does not affect the main functionality
        self.artwork.manifest       = self.Get(str, "artwork",  "manifest",     "/opt/musicdb/server/webui/manifest.appcache")


        # [videoframes]
        self.videoframes = VIDEOFRAMES()
        self.videoframes.path           = self.GetDirectory("videoframes",  "path",     "/opt/musicdb/data/videoframes")
        self.videoframes.frames         = self.Get(int, "videoframes",  "frames",       "5")
        self.videoframes.previewlength  = self.Get(int, "videoframes",  "previewlength","3")
        self.videoframes.scales         = self.Get(str, "videoframes",  "scales",       "50x27, 150x83", islist=True)
        for s in ["150x83"]:
            if not s in self.videoframes.scales:
                logging.error("Missing scale in [videoframes]->scales: The web UI expects a scale of %s", s)
        for scale in self.videoframes.scales:
            try:
                width, height   = map(int, scale.split("x"))
            except Exception as e:
                logging.error("Invalid video scale format in [videoframes]->scales: Expected format WxH, with W and H as integers. Actual format: %s.", scale)


        # [extern]
        self.extern = EXTERN()
        self.extern.configtemplate  = self.GetFile( "extern",   "configtemplate","/opt/musicdb/server/share/extconfig.ini")
        self.extern.statedir        = self.Get(str, "extern",   "statedir",     ".mdbstate")
        self.extern.configfile      = self.Get(str, "extern",   "configfile",   "config.ini")
        self.extern.songmap         = self.Get(str, "extern",   "songmap",      "songmap.csv")
        

        # [tracker]
        self.tracker = TRACKER()
        self.tracker.dbpath         = self.GetFile( "tracker",  "dbpath",       "/opt/musicdb/data/tracker.db")
        self.tracker.cuttime        = self.Get(int, "tracker",  "cuttime",      "30")


        # [lycra]
        self.lycra = LYCRA()
        self.lycra.dbpath           = self.GetFile( "lycra",    "dbpath",       "/opt/musicdb/data/lycra.db")


        # [Icecast]
        self.icecast    = ICECAST()
        self.icecast.port           = self.Get(int, "Icecast",  "port",     "6666")
        self.icecast.user           = self.Get(str, "Icecast",  "user",     "source")
        self.icecast.password       = self.Get(str, "Icecast",  "password", "hackme")
        self.icecast.mountname      = self.Get(str, "Icecast",  "mountname","/stream")


        # [Randy]
        self.randy      = RANDY()
        self.randy.nodisabled       = self.Get(bool, "Randy",   "nodisabled",   True)
        self.randy.nohated          = self.Get(bool, "Randy",   "nohated",      True)
        self.randy.minsonglen       = self.Get(int,  "Randy",   "minsonglen",   120)
        self.randy.maxsonglen       = self.Get(int,  "Randy",   "maxsonglen",   600)
        self.randy.songbllen        = self.Get(int,  "Randy",   "songbllen",    50)
        self.randy.albumbllen       = self.Get(int,  "Randy",   "albumbllen",   20)
        self.randy.artistbllen      = self.Get(int,  "Randy",   "artistbllen",  10)
        self.randy.videobllen       = self.Get(int,  "Randy",   "videobllen",   10)
        self.randy.maxblage         = self.Get(int,  "Randy",   "maxblage",     24)


        # [log]
        self.log        = LOG()
        self.log.logfile            = self.Get(str, "log",      "logfile",      "stderr")
        self.log.loglevel           = self.Get(str, "log",      "loglevel",     "WARNING")
        if not self.log.loglevel in ["DEBUG", "INFO", "WARNING", "ERROR"]:
            logging.error("Invalid loglevel for [log]->loglevel. Loglevel must be one of the following: DEBUG, INFO, WARNING, ERROR")
        self.log.debugfile          = self.Get(str, "log",      "debugfile",    None)
        if self.log.debugfile == "/dev/null":
            self.log.debugfile = None
        self.log.ignore             = self.Get(str, "log",      "ignore",       None, islist=True)


        # [debug]
        self.debug      = DEBUG()     
        self.debug.disablestats     = self.Get(int, "debug",    "disablestats",     0)
        self.debug.disabletracker   = self.Get(int, "debug",    "disabletracker",   0)
        self.debug.disableai        = self.Get(int, "debug",    "disableai",        1)
        self.debug.disabletagging   = self.Get(int, "debug",    "disabletagging",   0)
        self.debug.disableicecast   = self.Get(int, "debug",    "disableicecast",   0)

        logging.info("\033[1;32mdone")



    def GetDirectory(self, section, option, default, logger=logging.error):
        """
        This method gets a string from the config file and checks if it is an existing directory.
        If not it prints an error.
        Except printing the error nothing is done.
        The \"invalid\" will be returned anyway, because it may be OK that the directory does not exist yet.
        
        Args:
            section (str): Section of an ini-file
            option (str): Option inside the section of an ini-file
            default (str): Default directory if option is not set in the file
            logger: Logging-handler. Default is logging.error. logging.warning can be more appropriate in some situations.

        Returns:
            The value of the option set in the config-file or the default value.
        """
        path = self.Get(str, section, option, default)
        if not self.fs.IsDirectory(path):
            logger("Value of [%s]->%s does not address an existing directory.", section, option)
        return path # return path anyway, it does not matter if correct or not. Maybe it will be created later on.


    def GetFile(self, section, option, default, logger=logging.error):
        """
        This method gets a string from the config file and checks if it is an existing file.
        If not it prints an error.
        Except printing the error nothing is done.
        The \"invalid\" will be returned anyway, because it may be OK that the file does not exist yet.
        
        Args:
            section (str): Section of an ini-file
            option (str): Option inside the section of an ini-file
            default (str): Default file path if option is not set in the file
            logger: Logging-handler. Default is logging.error. logging.warning can be more appropriate in some situations.

        Returns:
            The value of the option set in the config-file or the default value.
        """
        path = self.Get(str, section, option, default)
        if not self.fs.IsFile(path):
            logger("Value of [%s]->%s does not address an existing file.", section, option)
        return path # return path anyway, it does not matter if correct or not. Maybe it will be created later on.


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

