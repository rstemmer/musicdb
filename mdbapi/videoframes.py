# MusicDB,  a music manager with web-bases UI that focus on music.
# Copyright (C) 2020  Ralf Stemmer <ralf.stemmer@gmx.net>
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
This module handles the thumbnails (frames) and previews (git-animation) of videos.
Its main task is to cache, scale and provide them to the GUI.

Definitions
-----------

frame:
    One frame extracted from a music video stored as a picture.

thumbnail:
    One video frame that is used as image to represent the video in the UI.
    File format is JPEG.

preview:
    A short gif-animation consisting of several frames of the video.
    This animation will can be played when the cursor hovers above the video.


Database
--------

The thumbnail and preview data is part of the video entry in the MusicDB Database.
The thumbnail and preview part consists of the following entries:

    +------------+
    | framespath |
    +------------+

framespath:
    The path to a frame relative to the thumbnails root directory set in the MusicDB Configuration.
    To access a scaled version of the artwork, the scale as prefix can be used.

    For example, to access a thumbnail, the absolute path would be ``/$THUMBNAILCACHE/$THUMBNAILPATH``,
    a scaled version can be found in ``$THUMBNAILCACHE/50x50/$THUMBNAILPATH``.
    Of cause only if the scale of 50x50 is supported (= configured in the Config-File).


Path structure
--------------

The video frames root directory can be configured in the MusicDB Configuration file.
Everything related to video frames takes place in this directory.
To use the artwork inside a web frontend, the HTTPS server needs access to this directory.

Relative to the frames root directory are the frames paths stored in the database.
For each video a sub directory exists.
Source-frames and all scaled frames as well as gif animations are stored in this sub directory.

The name of the frames directory for a video, consists of the artist name and video name:
``$Artistname - $Videoname``.
This guarantees unique file names that are human readable at the same time.

Inside this sub directory the following files exists:

frame-$i.jpg:
    The source video frames.
    ``$i`` is a continuing number with two digits starting by 1.
    For one video, multiple frames will be extracted.
    The exact number of frames can be defined in the configuration file.
    The file format is JPEG.
    The samples are collected uniform distributed over the video length.

frame-$i ($s×$s).jpg:
    A scaled version of *frame-$i*.
    ``$s`` represents the scaled size that can be configured in the configuration file.
    The separator is a multiplication sign × (U+00D7) to make the name more human readable.
    Multiple scales are possible.
    For example, the name of the 5th frame scaled down to a size of max 100px would be ``frame-5 (100×100).jpg``

preview.gif:
    A preview of the video as animation.
    All source frames available as JPEG are combined to the GIF animation.
    The amount of frames can be configured, as well as the animation length.
    The frames are uniform distributed over the animation length.

preview-$i ($s×$s).gif:
    A scaled version of the preview animation.

The sub directory name for each video gets created by
the method :meth:`~mdbapi.videoframes.VideoFrames.CreateFramesDirectoryName`.
This method replaces "/" by an Unicode division slash (U+2215) to avoid problems with the filesystem.

All new creates files and directories were set to the ownership ``[music]->owner:[music]->group``
and gets the permission ``rw-rw-r--`` (``+x`` for directories)


HTTPS Server
------------

Web browsers has to prefix the path with ``videoframes/``.
So, the server must be configured.


Scaling
--------

Scales that shall be provides are set in the MusicDB Configuration as list of edge-lengths.
For example, to generate 50x50, 100x100 and 500x500 versions of a frame,
the configuration would look like this: ``scales=50, 100, 500``
The scaled frames get stored as progressive JPEGs to get a better responsiveness for the WebUI.

Usually videos do not have a ration of 1:1. TODO


Configuration
-------------

An example configuration can look like the following one:

.. code-block:: ini

    [videoframes]
    path=/data/musicdb/videoframes  ; Path to the sub directories for videos
    frames=5                        ; Grab 5 frames from the video
    scales=50, 150                  ; Provide scales of 50px and 150px
    previewlength=3

Under these conditions, a 150×150 pixels preview animation of a video "Sonne" from "Rammstein"
would have the following absolute path:
``/data/musicdb/videoframes/Rammstein - Sonne/preview (150×150).gif``.
Inside the database, this path is stored as ``Ramstein - Sonne``.
Inside the HTML code of the WebUI the following path would be used: ``Rammstein - Sonne/preview (150×150).gif``.


Algorithm
---------

To update the frames cache the following steps are done:

TODO

    #. Create a sun directory for the frames via :meth:`~mdbapi.videoframes.VideoFrames.CreateFramesDirectory`
    #. Generate the frames from a video with :meth:`~mdbapi.videoframes.VideoFrames.GenerateFrames`
    #. Generate the previews from the frames with :meth:`~mdbapi.videoframes.VideoFrames.GeneratePreviews`
    #. Update database entry with the directory name

    #. Read metadata from file in :meth:`~mdbapi.artwork.MusicDBArtwork.GetArtworkFromFile`
    #. Create scaled versions of the new artwork in :meth:`~mdbapi.artwork.MusicDBArtwork.SetArtwork`
    #. Create database entry in :meth:`~mdbapi.artwork.MusicDBArtwork.SetArtwork`

"""

import os
import stat
from lib.filesystem     import Filesystem
from lib.cfg.musicdb    import MusicDBConfig
from lib.db.musicdb     import *

class VideoFrames(object):
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
        self.musicroot  = Filesystem(self.cfg.music.path)
        self.framesroot = Filesystem(self.cfg.videoframes.path)

        # Check if all paths exist that have to exist
        pathlist = []
        pathlist.append(self.cfg.music.path)
        pathlist.append(self.cfg.videoframes.path)

        for path in pathlist:
            if not self.fs.Exists(path):
                raise ValueError("Path \""+ path +"\" does not exist.")



    def CreateFramesDirectoryName(self, artistname, videoame):
        """
        This method creates the name for a frames directory regarding the following schema:
        ``$Artistname - $Videoname``.
        If there is a ``/`` in the name, it gets replaced by ``∕`` (U+2215, DIVISION SLASH)

        Args:
            artistname (str): Name of an artist
            videoname (str): Name of a video

        Returns:
            valid frames sub directory name for a video
        """
        artistname = artistname.replace("/", "∕")
        videoname  = videoname.replace( "/", "∕")
        dirname    = artistname + " - " + videoname
        return dirname



    def CreateFramesDirectory(self, artistname, videoname):
        """
        This method creates the directory that contains all frames and previews for a video.
        The ownership of the created directory will be the music user and music group set in the configuration file.
        The permissions will be set to ``rwxrwxr-x``.

        Args:
            artistname (str): Name of an artist
            videoname (str): Name of a video

        Returns:
            The name of the directory.
        """
        # Determine directory name
        dirname = self.CreateFramesDirectoryName(artistname, videoname)

        # Create directory
        self.framesroot.CreateSubDirectory(dirname)

        # Set permissions to -rwxrwxr-x
        try:
            self.framesroot.SetAttributes(dirname,
                    self.cfg.music.owner, self.cfg.music.group,
                    stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |
                    stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP | stat.S_IROTH)
        except Exception as e:
            logging.warning("Setting frames sub directory attributes failed with error %s. \033[1;30m(Leaving them as they are)", str(e))

        return dirname



    def GenerateFrames(self, dirname, videopath):
        """
        This method creates all frame files, including scaled frames, from a video.
        After generating the frames, animations can be generated via :meth:`~GeneratePreviews`.
        """
        pass



    def GeneratePreviews(self, dirname):
        """
        This method creates all preview animations, including scaled versions, from frames.
        The frames can be generated via :meth:`~GenerateFrames`.
        """
        pass


#######################################################################################
# OLD

    def GetArtworkFromFile(self, album, tmpawfile):
        """
        This method tries to get an artwork from the metadata of the first song of an album.
        With the first song, the first one in the database related to the album is meant.
        The metadata gets loaded and the artwork stored to a temporary file using the method
        :meth:`lib.metatags.MetaTags.StoreArtwork`.

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
            #. Create scaled Versions of the artwork by calling :meth:`lib.cache.ArtworkCache.GetArtwork` for each resolution.
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
            self.artworkroot.CopyFile(abssrcpath, absdstpath)

            # Set permissions to -rw-rw-r--
            try:
                self.artworkroot.SetAttributes(artworkname, self.cfg.music.owner, self.cfg.music.group, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH)
            except Exception as e:
                logging.warning("Setting artwork file attributes failed with error %s. \033[1;30m(Leaving them as they are)", str(e))

        if not self.artworkroot.Exists(artworkname):
            logging.error("Artwork \"%s\" does not exist but was expected to exist!", artworkname)
            return False

        # Scale file
        # convert edge-size to resolution
        # [10, 20, 30] -> ["10x10", "20x20", "30x30"]
        resolutions = [ str(s)+"x"+str(s) for s in self.cfg.artwork.scales ]

        for resolution in resolutions:
            relpath = self.awcache.GetArtwork(artworkname, resolution)

            if not self.artworkroot.Exists(relpath):
                logging.error("Artwork \"%s\" does not exist but was expected to exist!", relpath)
                return False

            # Set permissions to -rw-rw-r--
            try:
                self.artworkroot.SetAttributes(relpath, self.cfg.music.owner, self.cfg.music.group, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH)
            except Exception as e:
                logging.warning("Setting artwork file attributes failed with error %s. \033[1;30m(Leaving them as they are)", str(e))

        # Update database entry
        self.db.SetArtwork(albumid, artworkname)

        return True


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

