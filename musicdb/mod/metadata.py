# MusicDB,  a music manager with web-bases UI that focus on music.
# Copyright (C) 2017 - 2022  Ralf Stemmer <ralf.stemmer@gmx.net>
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
The metadata command line module loads all meta data from a file.
The read data gets printed to the screen.
Therefor each method of the :doc:`/lib/metatags` module gets applied.

This module is made for testing and analysing bugs in the :class:`musicdb.lib.metatags.MetaTags` class.

Example:

    .. code-block:: bash

        musicdb metadata /data/music/Artist/2000\ -\ Album/01\ Song.m4a
"""

import argparse
from musicdb.lib.filesystem     import Filesystem
from musicdb.lib.modapi         import MDBModule
from musicdb.lib.metatags       import MetaTags


class metadata(MDBModule, MetaTags):
    def __init__(self, config, database):
        MetaTags.__init__(self)


    def CheckFile(self, path):
        self.Load(path)
        print(self.file.info.__dict__)
        print("\033[1;34mAll meta data:\n\033[0;37m" + self.file.pprint())
        print("\033[1;34mSongname:    \033[0;36m" + str(self.GetSongname()))
        print("\033[1;34mAlbumname:   \033[0;36m" + str(self.GetAlbumname()))
        print("\033[1;34mArtistname:  \033[0;36m" + str(self.GetArtistname()))
        print("\033[1;34mReleaseyear: \033[0;36m" + str(self.GetReleaseyear()))
        print("\033[1;34mCD-Number:   \033[0;36m" + str(self.GetCDNumber()))
        print("\033[1;34mTracknumber: \033[0;36m" + str(self.GetTracknumber()))
        print("\033[1;34mOrigin:      \033[0;36m" + str(self.GetOrigin()))
        print("\033[1;34mPlaytime:    \033[0;36m" + str(self.GetPlaytime()))
        print("\033[1;34mBitrate:     \033[0;36m" + str(self.GetBitrate()))
        print("\033[1;34mLyrics:      \033[0;36m" + str(self.GetLyrics()))
        print("\033[1;34mMetadata:    \033[0;36m" + str(self.GetAllMetadata()))

        print("\033[1;34mStore artwork to /tmp/mdbmetadatatest.jpg…\033[0m")
        self.StoreArtwork("/tmp/mdbmetadatatest.jpg")
        print("\033[1;32mdone\033[0m")
        

    @staticmethod
    def MDBM_CreateArgumentParser(parserset, modulename):
        parser = parserset.add_parser(modulename, help="manage external storage")
        parser.set_defaults(module=modulename)
        parser.add_argument("path", help="absolute path to the file.")



    # return exit-code
    def MDBM_Main(self, args):

        fs = Filesystem()
        path = fs.AbsolutePath(args.path)
        path = fs.ToString(path)

        if not fs.IsFile(path):
            print("\033[1;31mERROR: path \033[1;30m%s\033[1;31m does not exist!\033[0m"%(path))
            return 1

        self.CheckFile(path)

        return 0


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

