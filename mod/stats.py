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
This command line module just prints some statistics. There are no further arguments.

Example:

    .. code-block:: bash

        musicdb -q stats
"""

import argparse
from lib.modapi     import MDBModule
from lib.db.musicdb import MusicDatabase


class stats(MDBModule):
    def __init__(self, config, database):
        MDBModule.__init__(self)
        self.database = database


    @staticmethod
    def MDBM_CreateArgumentParser(parserset, modulename):
        parser = parserset.add_parser(modulename, help="show statistics")
        parser.set_defaults(module=modulename)


    def CountOrigin(self, albums):
        counter = {}
        counter["iTunes"]   = 0
        counter["CD"]       = 0
        counter["internet"] = 0
        counter["music163"] = 0
        counter["bandcamp"] = 0

        for album in albums:
            if album["origin"] == "iTunes":
                counter["iTunes"] += 1
            elif album["origin"] == "CD":
                counter["CD"] += 1
            elif album["origin"] == "internet":
                counter["internet"] += 1
            elif album["origin"] == "music163":
                counter["music163"] += 1
            elif album["origin"] == "bandcamp":
                counter["bandcamp"] += 1
            else:
                print("\033[1;31mERROR: Invalid origin for album %s: %s\033[0m" % (album["name"], album["origin"]))

        return counter


    def CountBitrate(self, songs):
        counter = {}
        for song in songs:
            bitrate = int(song["bitrate"] / 1000)
            if not str(bitrate) in counter:
                counter[str(bitrate)] = 1
            else:
                counter[str(bitrate)] += 1
        return counter


    def CountReleaseYear(self, albums):
        counter = {}
        for album in albums:
            year = str(album["release"])
            if not year in counter:
                counter[year] = 1
            else:
                counter[year] += 1
        return counter


    # return exit-code
    def MDBM_Main(self, args):
        # read database
        artists      = self.database.GetAllArtists()
        albums       = self.database.GetAllAlbums()
        songs        = self.database.GetAllSongs()

        # get stats
        numartists   = len(artists)
        numalbums    = len(albums)
        numsongs     = len(songs)
        origincounter=  self.CountOrigin(albums)
        releasecounter= self.CountReleaseYear(albums)
        bitratecounter= self.CountBitrate(songs)

        # print stats

        # Artists
        print("\033[1;34mNumber of \033[1;37mArtists\033[1;34m:\033[1;36m%4i\033[0m" % numartists)
        
        # Albums
        print("\033[1;34mNumber of \033[1;37mAlbums\033[1;34m: \033[1;36m%4i\033[1;34m \t⌀ \033[1;36m%.2f\033[1;34m Albums/Artist\033[0m" 
                % (numalbums, (numalbums / numartists)))
        for origin in ["iTunes","CD","internet","music163","bandcamp"]:
            print("\t\033[1;34m%8s: \033[1;36m%4i\033[0;36m % 2.2f%%\033[0m" % (origin, origincounter[origin], (origincounter[origin]*100)/numalbums))

        releaselist = list(releasecounter.keys())
        releaselist = sorted([int(x) for x in releaselist])
        for release in releaselist:
            release = str(release)

            # calc some more values
            percentage = (releasecounter[release]*100)/numalbums

            # highlight bad quality
            if int(release) < 1990:
                color = "\033[1;31m"
            elif int(release) < 2000:
                color = "\033[1;33m"
            elif int(release) < 2010:
                color = "\033[1;36m"
            else:
                color = "\033[1;32m"
            print(color + "\t%4s\033[1;34m:  \033[1;36m%3i\033[0;36m % 2.2f%%\033[0m" % (release, releasecounter[release], percentage))

        # Songs
        print("\033[1;34mNumber of \033[1;37mSongs\033[1;34m: \033[1;36m%5i\033[1;34m \t⌀ \033[1;36m%.2f\033[1;34m Songs/Album\033[0m"
                % (numsongs, (numsongs  / numalbums)))
        bitratelist = list(bitratecounter.keys())
        bitratelist = sorted([int(x) for x in bitratelist])
        others = numsongs
        for bitrate in bitratelist:
            bitrate = str(bitrate)
            # ignore if less than 2 avarage albums use this bitrate
            if bitratecounter[bitrate] < int(numsongs/numalbums)*2:
                continue

            # calc some more values
            percentage = (bitratecounter[bitrate]*100)/numsongs
            others    -= bitratecounter[bitrate]

            # highlight bad quality
            if int(bitrate) < 160:
                color = "\033[1;31m"
            elif int(bitrate) < 192:
                color = "\033[1;33m"
            elif int(bitrate) < 256:
                color = "\033[1;36m"
            else:
                color = "\033[1;32m"
            print(color + "\t%3s\033[0;34mkbps\033[1;34m:  \033[1;36m%4i\033[0;36m % 2.2f%%\033[0m" % (bitrate, bitratecounter[bitrate], percentage))
        print(color + "\t\033[1;34m others\033[1;34m:  \033[1;36m%4i\033[0;36m % 2.2f%%\033[0m \033[1;30m(Invalid, VBR, …)" % (others, (others*100)/numsongs))

        return 0

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

