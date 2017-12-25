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

from lib.cfg.config import Config
from lib.db.musicdb import MusicDatabase
import logging

class QUEUE:
    pass

class MDBState(Config, object):
    """
    This class holds the MusicDB internal state.

    Args:
        filename: Absolute path to the MusicDB state file
        musicdb: instance of the MusicDB Database
    """

    def __init__(self, filename, musicdb):
        Config.__init__(self, filename)
        self.musicdb = musicdb;
        self.queue   = QUEUE()

        self.queue.eoqevent = self.Get(str, "queue", "EoQEvent", "add")


    def GetFilterList(self):
        """
        This method returns a list of the activated genre

        Returns:
            A list of main genre names that are activated
        """
        filterlist = []
        genretags   = self.musicdb.GetAllTags(MusicDatabase.TAG_CLASS_GENRE)
        
        self.Reload()
        for tag in genretags:
            state = self.Get(bool, "albumfilter", tag["name"], False)
            if state:
                filterlist.append(tag["name"])

        return filterlist

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

