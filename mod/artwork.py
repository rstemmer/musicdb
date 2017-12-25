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
This module manages the artworks of an album and caches several scaled versions of it.

There are two main options: ``-u`` to update one or all artworks, and the ``-m`` to update the cache manifest for the webui. Updating artwork implies a manifest update.

Iff there is no artwork assigned to the album, this artwork manager tries to extract the artwork from the metadata of a file of an album.
If there is an artwork assigned, it will only be scaled to resolution it is not already available yet.

If only one album shall be updated, it must be addressed by using the ``--album PATH`` option.
Is this option set, a further option ``--artwork PATH`` can be used to specify an artwork that shall be used for the album.
If no artwork is given, or if the whole cache shall be updated, the artwork inside the audio-files of an album are used.

All new creates files were set to the ownership ``[music]->owner:[music]->group`` and gets the permission ``rw-rw-r--``

Examples:

    Update the whole cache (Using :meth:`~mod.artwork.artwork.UpdateArtist`)

    .. code-block:: bash

        musicdb artwork -u

    Update only for a new album (Using :meth:`~mod.artwork.artwork.UpdateAlbum`)

    .. code-block:: bash

        musicdb artwork --album $Albumpath -u

    Update only the manifest file (Using :meth:`~mdbapi.artwork.GenerateAppCacheManifest`)

    .. code-block:: bash

        musicdb artwork -m

    For a user-defined artwork (Using :meth:`~mod.artwork.artwork.UpdateAlbum`)

    .. code-block:: bash

        musicdb artwork --artwork $Artworkpath --album $Albumpath -u
"""

import argparse
from lib.modapi     import MDBModule
from mdbapi.artwork import MusicDBArtwork
from tqdm           import tqdm

class artwork(MDBModule, MusicDBArtwork):
    def __init__(self, config, database):
        MusicDBArtwork.__init__(self, config, database)


    @staticmethod
    def MDBM_CreateArgumentParser(parserset, modulename):
        parser = parserset.add_parser(modulename, help="do artwork management")
        parser.set_defaults(module=modulename)
        parser.add_argument("--artwork", action="store", type=str, default=None,
                help="Force using this given artwork (only possible when updating a single album)")
        parser.add_argument("--album",   action="store", type=str, default=None,
                help="Only update this album")

        parser.add_argument("-m", "--manifest", action="store_true", help="generate a new app-cache-manifest")
        parser.add_argument("-u", "--update",   action="store_true", help="update artwork-cache on the disk (updates also the manifest)")


    def UpdateArtist(self):
        """
        This method does an update for all artists in the music collection.

        Returns:
            *Nothing*
        """
        artists = self.db.GetAllArtists()
        for artist in tqdm(artists, unit="Artists"):
            albums = self.db.GetAlbumsByArtistId(artist["id"])
            for album in albums:
                self.UpdateAlbumArtwork(album)


    def UpdateAlbum(self, albumpath, artworkpath=None):
        """
        This method does partial update and can be used to force a specific artwork.
        If *artworkpath* is given, that artwork will be copied to the cache instead of extraction one from the metadata.

        Args:
            albumpath (str): Path to an album. This can be absolute or relative to the music directory.
            artworkpath (str / NoneType): Absolute path to the artwork that shall be used if given.

        Return:
            ``True`` on success, otherwise ``False``
        """
        if not albumpath:
            print("\033[1;31mNo albumpath given!\033[0m")
            return False
        
        try:
            albumpath = self.musicroot.AbsolutePath(albumpath)  # First make userinput valid
            albumpath = self.musicroot.RemoveRoot(albumpath)    # Then try to get relative path
        except Exception as e:
            print("\033[1;31mInvalid albumpath: \"%s\". \033[0;31m(%s)\033[0m" % (albumpath, str(e)))
            return False
        
        album = self.db.GetAlbumByPath(albumpath)
        if not album:
            print("\033[1;31mInvalid albumpath: \"%s\". \033[0;31m(No album with this path in database.)\033[0m" % (albumpath))
            return False

        if not artworkpath:
            self.UpdateAlbumArtwork(album)
        else:
            artist    = self.db.GetArtistById(album["artistid"])
            imagename = self.CreateArtworkName(artist["name"], album["name"])
            retval    = self.SetArtwork(album["id"], artworkpath, imagename)
            if retval == False:
                print("\033[1;31mSetting artwork failed!\033[0m")
                return False

        return True



    def MDBM_Main(self, args):

        # Update Cache and Manifest
        if args.update:
            if args.album:
                self.UpdateAlbum(args.album, args.artwork)
            else:
                self.UpdateArtist()

            self.GenerateAppCacheManifest()

        # Only update Manifest
        elif args.manifest:
            self.GenerateAppCacheManifest()

        return 0

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

