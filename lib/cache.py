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
import os
import logging
from lib.filesystem     import Filesystem
from PIL                import Image



class ArtworkCache(object):
    """
    This class handles the artwork cache.
    Its main job is to scale an image if a special resolution is requested.

    Args:
        artworkdir: Absolute path to the artwork root directory
    """
    def __init__(self, artworkdir):
        self.artworkroot = Filesystem(artworkdir)


    def GetArtwork(self, artworkname, resolution):
        """
        This method returns a valid path to an artwork with the specified resolution.

        The final path will consist of the *artworkdir* given as class parameter, the *resolution* as subdirectory and the *artworkname* as filename. (``{artworkdir}/{resolution}/{artworkname}``)

        If the artwork does not exist for this resolution it will be generated.
        If the directory for that scale does not exist, it will be created.
        In case an error occcurs, an exception gets raised.

        The resolution is given as string in the format ``{X}x{Y}`` (For example: ``100x100``).
        *X* and *Y* must have the same value.
        This method expects an aspect ratio of 1:1.

        Beside scaling the JPEG, it will be made progressive.

        Args:
            artworkname (str): filename of the source artwork (Usually ``$Artist - $Album.jpg``)
            resolution (str): resolution of the requested artwork

        Returns:
            Relative path to the artwork in the specified resolution.

        Raises:
            ValueError: When the source file does not exist

        Example:

            .. code-block:: python

                cache = ArtworkCache("/data/artwork")
                path  = cache.GetArtwork("example.jpg", "150x150")
                # returned path: "150x150/example.jpg"
                # absolute path: "/data/artwork/150x150/example.jpg"
        """
        logging.debug("GetArtwork(%s, %s)", artworkname, resolution)

        # Check if source exists
        if not self.artworkroot.Exists(artworkname):
            logging.error("Source file %s does not exist in the artwork root directory!", artworkname)
            raise ValueError("Source file %s does not exist in the artwork root directory!", 
                    artworkname)

        # Check if already scaled. If yes, our job is done
        scaledfile = os.path.join(resolution, artworkname)
        if self.artworkroot.Exists(scaledfile):
            return scaledfile

        # Check if the scale-directory already exist. If not, create one
        if not self.artworkroot.IsDirectory(resolution):
            logging.debug("Creating subdirectory: %s", resolution)
            self.artworkroot.CreateSubdirectory(resolution)

        # Scale image
        logging.debug("Converting image to %s", resolution)
        abssrcpath = self.artworkroot.AbsolutePath(artworkname)
        absdstpath = self.artworkroot.AbsolutePath(scaledfile)

        # "10x10" -> (10, 10)
        length = int(resolution.split("x")[0])
        size   = (length, length)

        im = Image.open(abssrcpath)
        im.thumbnail(size, Image.BICUBIC)
        im.save(absdstpath, "JPEG", optimize=True, progressive=True)

        return scaledfile


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

