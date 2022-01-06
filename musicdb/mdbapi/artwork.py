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
This module handles the artwork (cover) of albums.
Its main task is to cache, scale and provide them to the GUI.


Artwork Related Database Entries
--------------------------------

The artwork data is part of the album entry in the MusicDB Database.
The artwork part consists of the following entries:

    +-------------+---------+---------+---------+
    | artworkpath | bgcolor | fgcolor | hlcolor |
    +-------------+---------+---------+---------+

artworkpath (string)
    The path to the cover relative to the artwork root directory set in the MusicDB Configuration.
    To access a scaled version of the artwork, the scale as prefix can be used.

    For example, to access a cover, the absolute path would be ``$ARTWORKCACHE/$ARTWORKPATH``,
    a scaled version can be found in ``$ARTWORKCACHE/50x50/$ARTWORKPATH``.
    Of cause only if the scale of 50x50 is supported (= configured in the Config-File).

bgcolor, fgcolor, hlcolor (string)
    HTML-Color-Code that shall be used by the UI.
    This color is set by the user.
    Its format is ``"#" + RR + GG + BB`` with *RR*, *GG*, *BB* as a two digit hexadecimal number.

    *bgcolor* is for background, *fgcolor* is the primary foreground color and *hlcolor* is the secondary color for less important elements in the foreground (like frames).
    For a complementary color scheme use *bgcolor* and *fgcolor* only.
    For a monochromatic scheme use *bgcolor* in a darker and less saturated variant for the background. The lighter and more saturated variant for the foreground.
    Keep in mind that the user may set all three colors to the same hue so that a monochromatic scheme gets forced.
    

Artwork Path structure
----------------------

The artwork root directory can be configured in the MusicDB Configuration file.
Everything related to artwork takes place in this directory.
To use the artwork inside a web frontend, the HTTPS server needs access to this directory.

Relative to the artwork root directory are the artwork paths stored in the database.
Source-Artworks, those who are not scaled, are in this directory.
All scaled artworks are in sub-directories named by the resolution of the images.

The name of an image, scaled and non-scaled, consists of the artist name and album name.
The file format is JPEG. So a name looks like this: ``$Artistname - $Albumname.jpg``.
This guarantees unique file names that are human readable at the same time.
To get the 100x100 scaled version of this artwork just prepend ``100x100/`` to the path set in the database: ``100x100/$Artistname - $Albumname.jpg``

The file name gets created by the method :meth:`~musicdb.mdbapi.artwork.MusicDBArtwork.CreateArtworkName`.
This method replaces "/" by an Unicode division slash to avoid problems with the filesystem.

In case there is no artwork given for an album, the default artwork is ``default.jpg``.

All new creates files were set to the ownership ``[musicdb]->username:[musicdb]->groupname`` and gets the permission ``rw-rw-r--``

Web Browsers
^^^^^^^^^^^^

Web browsers have to prefix the path with ``artwork/``.
So, the server must be configured.

Scaled Artwork
--------------

Scales that shall be provides are set in the MusicDB Configuration as list of edge-lengths.
For example, to generate 50x50, 100x100 and 500x500 versions of an artwork, the configuration would look like this: ``scales=50, 100, 500``
The **scaled artwork gets stored as progressive JPEGs** to get a better responsiveness for the WebUI.


Configuration for Artworks
--------------------------

.. code-block:: ini

    [albumcover]
    scales=50, 150, 500


Algorithm to Create Artworks
----------------------------

To update the album artwork cache the following steps are done:

    #. Read metadata from file in :meth:`~musicdb.mdbapi.artwork.MusicDBArtwork.GetArtworkFromFile`
        #. If there is no artwork, use default settings
        #. If there is an artwork, copy it to the artwork-directory
    #. Create scaled versions of the new artwork in :meth:`~musicdb.mdbapi.artwork.MusicDBArtwork.SetArtwork`
    #. Create database entry in :meth:`~musicdb.mdbapi.artwork.MusicDBArtwork.SetArtwork`

"""

import os
import stat
from musicdb.lib.filesystem     import Filesystem
from musicdb.lib.metatags       import MetaTags
from musicdb.lib.cache          import ArtworkCache
from musicdb.lib.cfg.musicdb    import MusicDBConfig
from musicdb.lib.db.musicdb     import *
from musicdb.mdbapi.accesspermissions   import AccessPermissions

class MusicDBArtwork(object):
    """
    Args:
        config: MusicDB configuration object
        database: MusicDB database

    Raises:
        TypeError: if config or database are not of the correct type
        ValueError: If one of the working-paths set in the config file does not exist
    """
    def __init__(self, config, database):

        if type(config) != MusicDBConfig:
            raise TypeError("Config-class of unknown type")
        if type(database) != MusicDatabase:
            raise TypeError("Database-class of unknown type")

        self.db     = database
        self.cfg    = config
        self.fs     = Filesystem()
        self.musicroot   = Filesystem(self.cfg.directories.music)
        self.artworkroot = Filesystem(self.cfg.directories.artwork)

        # Check if all paths exist that have to exist
        pathlist = []
        pathlist.append(self.cfg.directories.music)
        pathlist.append(self.cfg.directories.artwork)

        for path in pathlist:
            if not self.fs.Exists(path):
                raise ValueError("Path \""+ path +"\" does not exist.")

        ap = AccessPermissions(self.cfg)
        ap.EvaluateArtworkDirectory()

        # Instantiate dependent classes
        self.meta    = MetaTags(self.cfg.directories.music)
        self.awcache = ArtworkCache(self.cfg.directories.artwork)


    def GetArtworkFromFile(self, album, tmpawfile):
        """
        This method tries to get an artwork from the metadata of the first song of an album.
        With the first song, the first one in the database related to the album is meant.
        The metadata gets loaded and the artwork stored to a temporary file using the method
        :meth:`musicdb.lib.metatags.MetaTags.StoreArtwork`.

        Args:
            album: Album entry from the MusicDB Database
            tmpawfile (str): Temporary artwork path (incl filename) to which the artwork shall be written

        Returns:
            ``True`` on success, otherwise ``False``
        """
        # Load the first files metadata
        songs = self.db.GetSongsByAlbumId(album["id"])
        firstsong = songs[0]

        self.meta.Load(firstsong["path"])
        retval = self.meta.StoreArtwork(tmpawfile)
        return retval


    def SetArtwork(self, albumid, artworkpath, artworkname):
        """
        This method sets a new artwork for an album.
        It does the following things:

            #. Copy the artwork from *artworkpath* to the artwork root directory under the name *artworkname*
            #. Create scaled Versions of the artwork by calling :meth:`musicdb.lib.cache.ArtworkCache.GetArtwork` for each resolution.
            #. Update entry in the database

        All new creates files ownership will be set to ``[music]->owner:[music]->group`` and gets the permission ``rw-rw-r--``

        Args:
            albumid: ID of the Album that artwork shall be set
            artworkpath (str, NoneType): The absolute path of an artwork that shall be added to the database. If ``None`` the method assumes that the default artwork shall be set. *artworkname* will be ignored in this case.
            artworkname (str): The relative path of the final artwork.

        Returns:
            ``True`` on success, otherwise ``False``

        Examples:
            
            .. code-block:: python

                # Copy from metadata extracted temporary artwork to the artwork directory
                self.SetArtwork(albumid, "/tmp/musicdbtmpartwork.jpg", "Artist - Album.jpg")

                # Copy a user-defined artwork to the artwork directory
                self.SetArtwork(albumid, "/home/username/downloads/fromzeintanetz.jpg", "Artist - Album.jpg")

                # Set the default artwork
                self.SetArtwork(albumid, None, any)
        """
        if artworkpath:
            abssrcpath = self.fs.AbsolutePath(artworkpath)
            absdstpath = self.artworkroot.AbsolutePath(artworkname)

            # Copy file
            logging.debug("Copying file from \"%s\" to \"%s\"", abssrcpath, absdstpath)
            try:
                self.artworkroot.CopyFile(abssrcpath, absdstpath)
            except PermissionError as e:
                logging.exception("Copying artwork into the artwork directory failed with error: %s", str(e))
                return False

            # Set permissions to rw-rw-r--
            self.UpdateFileAttributes(artworkname)

        if not self.artworkroot.Exists(artworkname):
            logging.error("Artwork \"%s\" does not exist but was expected to exist!", artworkname)
            return False

        # Scale file
        # convert edge-size to resolution
        # [10, 20, 30] -> ["10x10", "20x20", "30x30"]
        resolutions = [ str(s)+"x"+str(s) for s in self.cfg.albumcover.scales ]

        for resolution in resolutions:
            success = self.awcache.RebuildArtwork(artworkname, resolution)

            if not success:
                logging.error("Artwork \"%s\" does not exist but was expected to exist!", relpath)
                return False

            relpath = self.awcache.GetArtwork(artworkname, resolution)

            # Try setting permissions to -rw-rw-r--
            self.UpdateFileAttributes(artworkname)

        # Update database entry
        self.db.SetArtwork(albumid, artworkname)

        return True



    def UpdateFileAttributes(self, path):
        """
        Tries to set the on owner of a file as configured in the MusicDB Configuration and
        the access permission to ``rw-rw-r--``.

        If the path is ``"default.jpg"`` only ``True`` gets returned without changing anything.
        The default artwork is part of the MusicDB data and gets managed by high level classes.

        Args:
            path: path to the artwork

        Returns:
            ``True`` on success, otherwise ``False``
        """
        if path == "default.jpg":
            logging.debug("File attributes of default.jpg will not be changed.")
            return True

        logging.debug("Trying to changing file attributes of \"%s\" to rw-rw-r-- and ownership to %s:%s.",
                path,
                self.cfg.musicdb.username, self.cfg.musicdb.groupname)

        # Set permissions to rw-rw-r--
        try:
            self.artworkroot.SetAccessPermissions(path, "rw-rw-r--")
        except Exception as e:
            logging.warning("Setting artwork file attributes to rw-rw-r-- failed with error %s. \033[1;30m(Leaving them as they are)", str(e))
            return False

        # Set Owner
        if not self.artworkroot.SetOwner(path, self.cfg.musicdb.username, self.cfg.musicdb.groupname):
            logging.warning("Setting artwork owner to %s:%s not allowed. \033[1;30m(Leaving them as they are)",
                    self.cfg.musicdb.username, self.cfg.musicdb.groupname)
            return False
        return True


    @staticmethod
    def CreateArtworkName(artistname, albumname):
        """
        This method creates the name for an artwork regarding the following schema:
        ``$Artistname - $Albumname.jpg``.
        If there is a ``/`` in the name, it gets replaced by ``∕`` (U+2215, DIVISION SLASH)

        Args:
            artistname (str): Name of an artist
            albumname (str): Name of an album

        Returns:
            valid artwork filename
        """
        artistname = artistname.replace("/", "∕")
        albumname  = albumname.replace( "/", "∕")
        imagename = artistname + " - " + albumname + ".jpg" 
        return imagename


    def UpdateAlbumArtwork(self, album, artworkpath=None):
        """
        This method updates the artwork path entry of an album and the artwork files in the artwork directory.
        If a specific artwork shall be forced to use, *artworkpath* can be set to this artwork file.
        Following the concept *The Filesystem Is Always Right* and *Do Not Trust Metadata*, the user specified artwork path has higher priority.
        Metadata will only be processed if *artworkpath* is ``None``

        So an update takes place if *at least one* of the following condition is true:

            #. The database entry points to ``default.jpg``
            #. *artworkpath* is not ``None``
            #. If the database entry points to a nonexistent file

        Args:
            album: An Album Entry from the MusicDB Database
            artworkpath (str, NoneType): Absolute path of an artwork that shall be used as album artwork. If ``None`` the Method tries to extract the artwork from the meta data of an albums song.

        Returns:
            ``True`` If either the update was successful or there was no update necessary.
            ``False`` If the update failed. Reasons can be an invalid *artworkpath*-Argument
        """
        # Create relative artwork path
        artist    = self.db.GetArtistById(album["artistid"])
        imagename = self.CreateArtworkName(artist["name"], album["name"])

        # Check if there is no update necessary
        dbentry   = album["artworkpath"]
        if dbentry != "default.jpg" and artworkpath == None:
            if self.artworkroot.IsFile(dbentry):    # If the file does not extist, it must be updated!
                return True

        # Check if the user given artworkpath is valid
        if artworkpath and not self.fs.IsFile(artworkpath):
            logging.error("The artworkpath that shall be forces is invalid (\"%s\")! \033[1;30m(Artwork update will be canceled)", str(artworkpath))
            return False

        # If there is no suggested artwork, try to get one from the meta data
        # In case this failes, use the default artwork
        if not artworkpath:
            artworkpath = "/tmp/musicdbtmpartwork.jpg"  # FIXME: Hardcoded usually sucks
            retval      = self.GetArtworkFromFile(album, artworkpath)
            if not retval:
                imagename   = "default.jpg"
                artworkpath = None

        # Set new artwork
        logging.info("Updating artwork for album \"%s\" to \"%s\" at \"%s\".", album["name"], imagename, artworkpath)
        retval = self.SetArtwork(album["id"], artworkpath, imagename)
        return retval



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

