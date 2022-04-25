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
This module maintains the MusicDB Artwork caches
"""

import logging
from musicdb.lib.filesystem     import Filesystem
from musicdb.lib.cache          import ArtworkCache


class ArtworkMaintainer(object):
    """
    This class provides a basic set of tools to check and create required files for MusicDB.

    Args:
        config (MusicDBConfig): Configuration object for MusicDB

    """
    def __init__(self, config, database):
        self.config       = config
        self.musicdb      = database
        self.artworkdir   = Filesystem(self.config.directories.artwork)
        self.artworkcache = ArtworkCache(self.config.directories.artwork)

        self.albumartworkscales = self.config.albumcover.scales
        self.user       = self.config.musicdb.username
        self.group      = self.config.musicdb.groupname



    def Validate(self):
        """
        This method checks if all cache directories exist.
        If not, the directory will be created.

        For all existing albums, their artwork will be scaled down and cached.
        This can take a while.

        Returns:
            ``True`` if everything is correct. Otherwise ``False``.
        """
        for scale in self.albumartworkscales:
            scaledir = str(scale) + "x" + str(scale)

            if self.artworkdir.IsDirectory(scaledir):
                continue

            logging.warning("Artwork cache for scale \"%s\" missing in \"%s\". \033[1;30m(Will be created)", scaledir, self.config.directories.artwork)

            # Create Directory
            self.artworkdir.CreateSubdirectory(scaledir)

            # Fill cache
            albums = self.musicdb.GetAllAlbums()

            logging.warning("Artwork cache for scale \"%s\" will be updated for %i artworks. This can take a while!", scaledir, len(albums))
            for album in albums:
                artworkpath = album["artworkpath"]
                try:
                    success = self.artworkcache.GetArtwork(artworkpath, scaledir)
                except Exception as e:
                    logging.exception("Cache artwork for %s scale from %s failed with error %s",
                            scaledir, artworkpath, str(e))
                    return False

                if not success:
                    logging.fatal("Cache artwork for %s scale from %s failed",
                            scaledir, artworkpath)
                    return False


        return True






# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

