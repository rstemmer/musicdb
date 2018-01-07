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
.. attention::

    Keep in mind that the main rule of MusicDB is: **The Filesystem Is Always Right**.

    All data collected via this class shall only be uses as addition information, not as primary source!
"""

import logging
import os
import subprocess
from mutagenx.flac  import FLAC
from mutagenx.mp3   import MP3
from mutagenx.mp4   import MP4
from lib.filesystem import Filesystem

class MetaTags(object):
    """
    This class can be used to access the metadata of the music files.

    Args:
        root (str): All paths used in this class are relative to this path. Default is ``"/"``.
    """

    def __init__(self, root="/"):
        self.fs         = Filesystem(root)
        self.file       = None      # the mutagenx file handler/object
        self.ftype      = None      # contains the identifier of the filetype (m4a, mp3, flac)
        self.extension  = None      # contains the actual file extension
        self.path       = None      # contains the full path of the file for debugging


    def Load(self, path):
        """
        Supported file extensions:

            * For MPEG4: ``mp4``, ``aac``, ``m4a``
            * For MPEG3: ``mp3``, ``MP3``
            * For FLAC: ``flac``

        Args:
            path (str): path to the song file that shall be loaded

        Returns:
            *Nothing*

        Raises:
            TypeError: If path is not a string
            ValueError: If file not exist or file cannot be read.
            ValueError: If the file extension or file format is not supported
        """
        logging.debug("Analysing file from %s", path)
        if type(path) != str:
            raise TypeError("Path must be a string!")

        # do some filename-management
        self.path = self.fs.AbsolutePath(path)
        if not self.fs.IsFile(self.path):
            self.path = None
            raise ValueError("File \"%s\" does not exist"%(self.path))
        
        # remenber the path for debugging
        self.extension = self.fs.GetFileExtension(self.path)

        # normalize the extension
        if self.extension in ["mp4", "aac", "m4a"]:
            self.ftype = "m4a"
        elif self.extension == "flac":
            self.ftype = "flac"
        elif self.extension in ["mp3", "MP3"]:
            self.ftype = "mp3"
        else:
            self.path = None
            raise ValueError("Unsupported file-extension \"%s\" of \"%s\""%(self.extension, path))

        logging.debug("Loading file of type %s from \"%s\"", self.ftype, self.path)

        # open the file
        if self.ftype == "flac":
            self.file = FLAC(self.path)
        elif self.ftype == "mp3":
            self.file = MP3(self.path)
        elif self.ftype == "m4a":
            self.file = MP4(self.path)
        else:
            self.path = None
            raise ValueError("Unsupported file-type %s"%(self.ftype))


    def GetAllMetadata(self):
        """
        This method collects as much information as possible from a file.
        The information gets stored in a dictionary.

            * ``song``: :meth:`~lib.metatags.MetaTags.GetSongname`
            * ``album``: :meth:`~lib.metatags.MetaTags.GetAlbumname`
            * ``artist``: :meth:`~lib.metatags.MetaTags.GetArtistname`
            * ``releaseyear``: :meth:`~lib.metatags.MetaTags.GetReleaseyear`
            * ``cdnumber``: :meth:`~lib.metatags.MetaTags.GetCDNumber`
            * ``songnumber``: :meth:`~lib.metatags.MetaTags.GetTracknumber`
            * ``origin``: :meth:`~lib.metatags.MetaTags.GetOrigin`
            * ``playtime``: :meth:`~lib.metatags.MetaTags.GetPlaytime`
            * ``bitrate``: :meth:`~lib.metatags.MetaTags.GetBitrate`
            * ``lyrics``: :meth:`~lib.metatags.MetaTags.GetLyrics`
        """
        metadata = {}
        metadata["song"]        = self.GetSongname()
        metadata["album"]       = self.GetAlbumname()
        metadata["artist"]      = self.GetArtistname()
        metadata["releaseyear"] = self.GetReleaseyear()
        metadata["cdnumber"]    = self.GetCDNumber()
        metadata["songnumber"]  = self.GetTracknumber()
        metadata["origin"]      = self.GetOrigin()
        metadata["playtime"]    = self.GetPlaytime()
        metadata["bitrate"]     = self.GetBitrate()
        metadata["lyrics"]      = self.GetLyrics()
        return metadata



    def StoreArtwork(self, imgfilename):
        """
        This method stores an artwork from the metadata into a file.
        If there is no artwork in the metadata, ``False`` gets returned.

        If the file already exists, it gets overwritten.

        Args:
            imgfilename (str): Absolute path to an image file to store the image at

        Returns:
            ``True`` on success, otherwise ``False``
        """
        try:
            if self.ftype == "mp3":
                # Source: http://stackoverflow.com/questions/6171565/how-do-i-read-album-artwork-using-python
                artwork = self.file["APIC:"] # access APIC frame and grab the image
                with open(imgfilename, "wb") as img:
                    img.write(artwork.data)
                return True

            elif self.ftype == "m4a":
                artwork = self.file[b"covr"][0]
                with open(imgfilename, "wb") as img:
                    img.write(artwork)
                return True

            elif self.ftype == "flac":
                artwork = self.file.pictures[0].data
                with open(imgfilename, "wb") as img:
                    img.write(artwork)
                return True

        except KeyError:
            logging.debug("File \"%s\" does not have a Cover-Image", self.path)
        except Exception as e:
            logging.warning("Storing artwork to \"\033[0;33m%s\033[1;33m\" failed with error \"%s\"!"
                    , imgfilename, e)

        return False



    def GetSongname(self):
        """
        This method returns the name of a song

        Returns:
            The song name as string, or ``None`` if entry does not exist
        """
        try:
            if self.ftype == "m4a":
                return self.file[b"\xa9nam"][0]

            elif self.ftype == "mp3":
                name = self.file["TIT2"][0]

                # check if the unicodes were read wrong
                try:
                    name = name.encode("latin-1").decode("utf-8")
                except:
                    pass
                return name

            elif self.ftype == "flac":
                return self.file["Title"][0]

        except KeyError:
            logging.debug("File \"%s\" does not have a songname", self.path)
            return None

        return None



    def GetAlbumname(self):
        """
        This method returns the name of the album

        Returns:
            The album name as string, or ``None`` if entry does not exist
        """
        if self.ftype == "m4a":
            if b"\xa9alb" in self.file:
                return self.file[b"\xa9alb"][0]
            else:
                logging.debug("File \"%s\" does not have an albumname", self.path)
                return None

        elif self.ftype == "mp3":
            # some songs dont have this tag
            if "TALB" in self.file:
                name = self.file["TALB"][0]
            else:
                logging.debug("File \"%s\" does not have an albumname", self.path)
                return None

            # check if the unicodes were read wrong
            try:
                name = name.encode("latin-1").decode("utf-8")
            except:
                pass

            return name

        elif self.ftype == "flac":
            return self.file["Album"][0]

        logging.debug("File \"%s\" does not have an albumname", self.path)
        return None



    def GetArtistname(self):
        """
        This method returns the name of the artist

        Returns:
            The artist name as string, or ``None`` if entry does not exist
        """
        try:
            if self.ftype == "m4a":
                return self.file[b"\xa9ART"][0]

            elif self.ftype == "mp3":
                name = self.file["TPE1"][0]
                # check if the unicodes were read wrong
                try:
                    name = name.encode("latin-1").decode("utf-8")
                except:
                    pass
                return name

            elif self.ftype == "flac":
                return self.file["Artist"][0]

        except KeyError:
            logging.debug("File \"%s\" does not have an artistname", self.path)
            return None

        return None


    def GetReleaseyear(self):
        """
        This method returns the release year

        Returns:
            The release year as integer, or ``0`` if entry does not exist
        """
        date = 0
        try:
            if self.ftype == "m4a":
                date = self.file[b"\xa9day"][0]
                date = date.split("-")[0]   # get just the year

            elif self.ftype == "mp3":
                if not "TDRC" in self.file:
                    return int(date)

                date = self.file["TDRC"][0]
                date = date.text

                try:
                    date = date.split("-")[0]
                except:
                    pass

            elif self.ftype == "flac":
                date = self.file["Date"][0]
                date = date.split("-")[0]   # get just the year

        except KeyError:
            logging.debug("File \"%s\" does not have a release year", self.path)
            return None
            
        try:
            date = int(date)
        except ValueError:
            logging.debug("File \"%s\" has a malformed date value!", self.path)
            data = 0
        return date



    def GetCDNumber(self):
        """
        This method returns the CD Number.
        The CD number is only stored in MP4 metadata.
        For all other formats, this method always returns ``0``

        Returns:
            The CD number as integer, or ``0`` if entry does not exist
        """
        number = 0
        if self.ftype == "m4a":
            try:
                number = self.file[b"disk"][0][0]
            except KeyError as e:
                pass
        elif self.ftype == "mp3":
            return 0
        elif self.ftype == "flac":
            return 0

        return int(number)



    def GetTracknumber(self):
        """
        This method returns the track number.

        Returns:
            The track number as integer, or ``0`` if entry does not exist
        """
        number = 0
        try:
            if self.ftype == "m4a":
                number = self.file[b"trkn"][0][0]

            elif self.ftype == "mp3":
                number = self.file["TRCK"][0]

            elif self.ftype == "flac":
                number = self.file["Tracknumber"][0]

        except KeyError:
            logging.debug("File \"%s\" does not have a tracknumber!", self.path)
            return 0

        try:
            number = number.split("/")[0]
        except:
            pass

        # mutagenx has problems with unicode. In some cases, the tracknumber was not read correctly
        # that's sooooo embarrassing for a python3 lib
        try:
            number = int(number)
        except:
            logging.debug("File \"%s\" has a malformated tracknumber!", self.path)
            number = 0
        return number



    def GetOrigin(self):
        """
        This method tries to determine where the file come from.
        The following origins can be detected: 

            * ``"iTunes"``
            * ``"bandcamp"``
            * ``"music163"`` aka 网易云音乐
            * ``"CD"`` as fallback for unknown *flac* files
            * ``"internet"`` as fallback for any other unknown files

        Returns:
            Name of the origin as string
        """
        # check m4a
        if self.ftype == "m4a":
            if b"----:com.apple.iTunes:iTunNORM" in self.file:
                return "iTunes"
            if b"----:com.apple.iTunes:iTunSMPB" in self.file:
                return "iTunes"
            if b"apID" in self.file:
                return "iTunes"

            if b"\xa9cmt" in self.file:
                comment = self.file[b"\xa9cmt"][0]
                comment = comment.lower()
                index   = comment.find("bandcamp")
                return "bandcamp"

        # Check mp3
        elif self.ftype == "mp3":
            # usually, music.163 uses the TPUB frame …
            try:
                if self.file["TPUB"][0] == "网易云音乐":
                    return "music163"
            except KeyError:
                pass
            # … but not always :( - There is a secound way: COMM contains a key
            try:
                if "COMM::\'eng\'" in self.file:
                    if "163 key" in self.file["COMM::\'eng\'"][0]:
                        return "music163"
                    elif "bandcamp" in self.file["COMM::\'eng\'"][0]:
                        return "bandcamp"
            except KeyError:
                pass

        # Check flac
        elif self.ftype == "flac":
            try:
                comments = self.file["Comment"]
                for comment in comments:
                    if "bandcamp" in comment:
                        return "bandcamp"
            except:
                pass

            return "CD"

        # "No" origin? So it's from the internet
        return "internet"



    def GetLyrics(self):
        """
        This method tries to get lyrics from the metadata.
        If on lyrics were found, ``None`` gets returned.

        Returns:
            The lyrics as string, or ``None`` if entry does not exist
        """
        if self.ftype == "m4a":
            return None

        elif self.ftype == "flac":
            try:
                lyrics = self.file[b"\xa9lyr"][0]
            except:
                return None

        elif self.ftype == "mp3":
            try:
                lyrics = self.file.tags.getall('USLT')[0].text
                if type(lyrics) == str and len(lyrics) > 0:
                    return lyrics
            except:
                return None

        return None



    def GetPlaytime(self):
        """
        This method tries to determine the playtime of a song.
        It first calls :meth:`~lib.metatags.MetaTags.AnalysePlaytime` which gets the playtime direct form file
        using ``ffprobe``.
        Only if this method fails, the playtime gets read from the meta data.

        Returns:
            playtime in second, or ``0`` if there is no way to get the time
        """
        time = 0

        if self.ftype in ["m4a", "mp3", "flac"]:
            try:
                analtime = round(self.AnalysePlaytime())
            except:
                analtime = None

            # never trust metadata, if we got duration, reading the metadata is not needed anymore
            if analtime:
                time = analtime
            else:
                try:
                    time = round(self.file.info.length)
                except:
                    time = 0

        return int(time)


    def AnalysePlaytime(self):
        """
        Analyses the playtime of a file using ``ffprobe``.

        The corresponding command line is the following:

            .. code-block:: bash

                ffprobe -v error -show_entries format=duration -print_format default=noprint_wrappers=1:nokey=1 $PATH

        Returns:
            The duration in seconds (as float) or ``None`` if the analysis fails
        """
        process = [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-print_format", "default=noprint_wrappers=1:nokey=1",
                self.path
                ]

        logging.debug("Running duration analysis: %s", str(process))
        try:
            retval = subprocess.check_output(process)
            logging.debug("Analysis returned %s", str(retval))
            retval = float(retval)
        except Exception as e:
            logging.error("Error \"%s\" while executing: %s", str(e), str(process))
            return None

        logging.debug("Analysis returned duration of %fs", retval)
        return retval



    def GetBitrate(self):
        """
        This method returns the bitrate of the file.

        Returns:
            bitrate as integer or ``0``
        """
        bitrate = 0

        if self.ftype in ["m4a", "mp3", "flac"]:
            try:
                bitrate = self.file.info.bitrate
            except:
                bitrate = 0

        return int(bitrate)


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

