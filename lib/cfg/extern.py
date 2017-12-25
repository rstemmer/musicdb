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
This class reads the configuration of an external music storage.
All sections and options can be accessed by their names: ``ExternConfig(...).section.option``.
If values get changed, they will not be stored!

Example:

    .. code-block:: ini

        [meta]
        version = 1

    .. code-block:: python

        cfg = ExternConfig("test.ini")
        print(cfg.meta.version)
"""

from lib.cfg.config import Config

class META:
    pass
class CONSTRAINTS:
    pass
class PATHS:
    pass
class MP3TAGS:
    pass
class M4ATAGS:
    pass

class ExternConfig(Config):

    def __init__(self, filename):
        Config.__init__(self, filename)

        self.meta        = META()
        self.constraints = CONSTRAINTS()
        self.mp3tags     = MP3TAGS()
        self.m4atags     = M4ATAGS()
        self.paths       = PATHS()

        self.meta.version           = self.Get(int,  "meta",        "version",  0) # 0 = inf
        self.constraints.pathlen    = self.Get(int,  "constraints", "pathlen",  0) # 0 = inf
        self.constraints.charset    = self.Get(str,  "constraints", "charset",  "default")
        self.constraints.forcemp3   = self.Get(bool, "constraints", "forcemp3", False)
        self.mp3tags.optimize       = self.Get(bool, "mp3tags",     "optimize", False)
        self.paths.musicdir         = self.Get(str,  "paths",       "musicdir", "/")
        
        # remove leading / because it is interpreted as "start at root" by join
        if self.paths.musicdir[0] == "/": 
            self.paths.musicdir = self.paths.musicdir[1:]

        self.mp3tags.prescale   = self.Get(str,  "mp3tags", "prescale", "None")
        if self.mp3tags.prescale.lower() == "none":
            self.mp3tags.prescale = None
        elif self.mp3tags.prescale.lower() == "false":
            self.mp3tags.prescale = None
        self.mp3tags.noartwork   = self.Get(bool, "mp3tags", "noartwork",    "False")
        self.mp3tags.forceid3v230= self.Get(bool, "mp3tags", "forceID3v230", "False")

        self.m4atags.optimize       = self.Get(bool, "m4atags",     "optimize", False)

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

