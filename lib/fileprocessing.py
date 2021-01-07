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
import shutil
import logging
import subprocess
import hashlib

from lib.filesystem import Filesystem

class Fileprocessing(Filesystem):
    """
    This class extends the interface to the :class:`lib.filesystem.Filesystem` class.
    It provides file processing methods.
    These methods may execute other linux shell commands.

       .. graphviz::

          digraph hierarchy {
             size="5,5"
             node[shape=record,style=filled,fillcolor=gray95]
             edge[dir=back, arrowtail=empty]

             filesystem     [label = "{Filesystem||}"]
             fileprocessing [label = "{Fileprocessing||}"]

             filesystem -> fileprocessing
          }

    Whenever I write about *root director* the path set in this class as root is meant.
    Otherwise I would call it *system root directory*.

    All paths of the methods provided by this class can be absolute or relative.
    The paths of methods from :class:`lib.filesystem.Filesystem` must be in the format as defined for that class.


    Args:
        root(str): Path to the internal used root directory. It is allowd to start with "./".

    Raises:
        ValueError: if the root path does not start with ``"/"`` or does not exist
    """
    def __init__(self, root="/"):
        Filesystem.__init__(self, root)



    def Checksum(self, path, algorithm="sha256"):
        """
        This method calculates the checksum of a file and returns it hexadecimal encoded as a string.
        If the file does not exists, ``None`` gets returned.

        The default algorithm is SHA-256

        Args:
            path (str): Path to the file from that the checksum shall be calculated
            algorithm (str): Checksum algorithm: ``"sha256"``, ``"sha1"``

        Returns:
            Checksum as string, or ``None`` if the file does not exist.

        Raises:
            ValueError: For unknown algorithm argument.

        Example:

            .. code-block:: python

                checksum = fs.Checksum(song["path"])
                print("Checksum: %s" % (checksum))
        """
        if algorithm not in ["sha256", "sha1"]:
            raise ValueError("algorithm must be \"sha256\" or \"sha1\"")

        abspath = self.AbsolutePath(path)

        if not self.IsFile(abspath):
            return None

        with open(abspath, "rb") as f:
            if algorithm == "sha256":
                checksum = hashlib.sha256(f.read()).hexdigest()
            elif algorithm == "sha1":
                checksum = hashlib.sha1(f.read()).hexdigest()

        return checksum



    def ConvertToMP3(self, srcpath, dstpath):
        """
        This method converts any audio file format to an mp3 file using ``ffmpeg``.

        The encoder is *libmp3lame* and the bitrate is esoteric 320kbit/s.
        If the destination file exists, it will be overwritten.

        Source and destination path must be different.

        This method corresponds to the following command line:

        .. code-block:: bash

            ffmpeg -v quiet -y -i $abssrcpath -acodec libmp3lame -ab 320k $absdstpath < /dev/null > /dev/null 2>&1
        
        .. warning::

            Call ``os.sync`` if the generated file will be further processed.
            In the past, there were lots of trouble with "incomplete" files.

        Args:
            srcpath (str): source path of a song file with any encoding
            dstpath (str): destination path of the new generated song file with mp3 encoding.

        Returns:
            ``True`` on success, otherwise ``False``

        Raises:
            ValueError: When ``srcpath`` and ``dstpath`` address the same file
        """
        abssrcpath = self.AbsolutePath(srcpath)
        absdstpath = self.AbsolutePath(dstpath)

        if abssrcpath == absdstpath:
            logging.error("Source (%s) and Destination (%s) address the same file!", abssrcpath, absdstpath)
            raise ValueError("Source and Destination path address the same file!")

        logging.debug("Converting %s to %s …", abssrcpath, absdstpath)
        process =[
            "ffmpeg",
            "-v", "quiet",  # do not be verbose
            "-y",           # overwrite
            "-i", abssrcpath,
            "-acodec", "libmp3lame", "-ab", "320k",
            absdstpath]

        try:
            self.Execute(process)
        except Exception as e:
            logging.error("Error \"%s\" while executing: %s", str(e), str(process))
            return False

        return True


    def OptimizeMP3Tags(self, mdbsong, mdbalbum, mdbartist, srcpath, dstpath, absartworkpath=None, forceID3v230=False):
        """
        This method fixed the ID3 tags of an mp3 file.
        For writing the new ID3 tags, ``id3edit`` is used.

        Source and destination path can be the same.
        The artwork path must be absolute!

        The call of ``id3edit`` corresponds to the following command line, reduced to just setting the songname.

            .. code-block:: bash

                id3edit --clear --create --set-name "Name of the Song" --outfile $absdstpath $abssrcpath < /dev/null > /dev/null 2>&1

        The following tags will be set. All other will be removed.

            * Song name
            * Album name
            * Artist name
            * Release date
            * Track number
            * CD number
            * Artwork

        .. warning::

            All other tags will not be copied to the new file.
            The ``id3edit`` call creates a totaly new *ID3v2* header for the mp3 file.

        Args:
            mdbsong: The corresponding song-object from the MusicDB Database
            mdbalbum: The corresponding album-object from the MusicDB Database
            mdbartist: The corresponding artist-object from the MusicDB Database
            srcpath (str): absolute source path of the mp3-file (must be mp3!)
            dstpath (str): absolute destination path for the new mp3-file. (Can be the same as the source path)
            absartworkpath (str): if  not ``None`` the album artwork will be stored inside the ID3 tags. Otherwise it will be removed.
            forceID3v230 (bool): use old ID3v2.3.0 tags instead of modern 2.4.0. Some player don't like a version number other than 2.3.0.

        Returns:
            ``True`` on success, otherwise ``False``

        Raises:
            ValueError: When the source or destination path is not an mp3 file.
        """
        abssrcpath = self.AbsolutePath(srcpath)
        absdstpath = self.AbsolutePath(dstpath)

        logging.debug("Optimize %s to %s for songid=%d, artwork=%s, prescale=%s, forceID3v230=%s", 
                abssrcpath, absdstpath, int(mdbsong["id"]), str(absartworkpath), str("500x500"), str(forceID3v230))

        # Check if paths are mp3-files! - caused a crash at least one times
        if self.GetFileExtension(abssrcpath) != "mp3":
            logging.error("%s is not a mp3-file and cannot be optimized by id3edit!", str(abssrcpath))
            raise ValueError("srcpath is not a mp3-file")
        if self.GetFileExtension(absdstpath) != "mp3":
            logging.error("%s is not a mp3-file. Output of id3edit is an mp3-file!", str(absdstpath))
            raise ValueError("dstpath is not a mp3-file")

        # Create tags
        songname    = mdbsong["name"]
        albumname   = mdbalbum["name"]
        artistname  = mdbartist["name"]
        release     = str(mdbalbum["release"])
        track       = "%02d/%02d" % (mdbsong["number"], mdbalbum["numofsongs"])
        cd          = "%1d/%1d"   % (mdbsong["cd"],     mdbalbum["numofcds"])

        # start optimizing the tags - at the same time the file gets copied to the new place
        process = ["id3edit", "--clear", "--create"]
        
        if forceID3v230:
            process += ["--force230"]

        process += [
            "--set-name",    songname,
            "--set-album",   albumname,
            "--set-artist",  artistname,
            "--set-release", release,
            "--set-track",   track,
            "--set-cd",      cd
            ]
        
        if absartworkpath:
            if not self.IsFile(absartworkpath):
                logging.error("Artwork \"%s\" does not exist but was expected to exist!", artworkpath)
                return False

            process += ["--set-artwork", absartworkpath]

        process += ["--outfile", absdstpath, abssrcpath]

        try:
            self.Execute(process)
        except Exception as e:
            logging.error("Error \"%s\" while executing: %s", str(e), str(process))
            return False

        return True



    def OptimizeM4ATags(self, mdbsong, mdbalbum, mdbartist, srcpath, dstpath):
        """
        This method fixes the Tags of an m4a file.
        The data for the Tags come from the MusicDBDatabase.
        For writing the new tags, ``ffmpeg`` is used.

        Source and destination path must be different.
        
        The call of ``ffmpeg`` corresponds to the following command line that got condensed to just setting the songname.

            .. code-block:: bash

                ffmpeg -v quiet -y -i $abssrcpath -vn -acodec copy -metadata title="Name of the Song" $absdstpath < /dev/null > /dev/null 2>&1

        The following tags will be set:

            * Song name
            * Album name
            * Artist name
            * Release date
            * Track number
            * CD number

        .. warning::

            Other tags could be removed - I don't care about them. 
            If ``ffmpeg`` also doesn't care, they are lost.
            This will definitely happen with iTunes related tags like the Apple ID and purchase-date.

            **Artwork will be removed, too** :( - This is considered as a bug. I just have no solution to fix it right now.

            The following code should preserve the artwork but throws an error:
            ``ffmpeg -y -i src.m4a -map 0:0 -map 0:1 -vcodec copy -acodec copy -metadata "title=Title" dst.m4a``

        Source and destination file must be different.
        The source file must have the file extension ``.m4a`` or ``.mp4``.

        Args:
            mdbsong: The corresponding song-object from the MusicDB Database
            mdbalbum: The corresponding album-object from the MusicDB Database
            mdbartist: The corresponding artist-object from the MusicDB Database
            srcpath (str): source path of the m4a-file (must be m4a!)
            dstpath (str): destination path for the new m4a-file. (Must be different from the source path)

        Returns:
            ``True`` on success, otherwise ``False``
        """
        abssrcpath = self.AbsolutePath(srcpath)
        absdstpath = self.AbsolutePath(dstpath)

        if abssrcpath == absdstpath:
            logging.error("Source (%s) and Destination (%s) address the same file!", abssrcpath, absdstpath)
            raise ValueError("Source and Destination path address the same file!")

        logging.debug("Optimize %s to %s for songid=%d", 
                abssrcpath, absdstpath, int(mdbsong["id"]))

        # Check if paths are valid
        if self.GetFileExtension(abssrcpath) not in ["m4a","mp4"]:
            logging.error("%s is not a m4a-file and cannot be optimized by this function - Check said song is of type %s", str(abssrcpath), str(os.path.splitext(abssrcpath)[1]))
            return False
        if abssrcpath == absdstpath:
            logging.error("source and destination paths are the same. This is not supported by this function.")
            return False

        # Create tags
        songname    = mdbsong["name"]
        albumname   = mdbalbum["name"]
        artistname  = mdbartist["name"]
        release     = str(mdbalbum["release"])
        track       = "%02d/%02d" % (mdbsong["number"], mdbalbum["numofsongs"])
        cd          = "%1d"       % (mdbsong["cd"])

        # start optimizing the tags - at the same time the file gets copied to the new place
        process = [
            "ffmpeg", "-v", "quiet",
            "-y",
            "-i", abssrcpath,
            "-vn",
            "-acodec", "copy",
            "-metadata", "title="  + songname  ,
            "-metadata", "album="  + albumname ,
            "-metadata", "author=" + artistname,
            "-metadata", "year="   + release   ,
            "-metadata", "track="  + track     ,
            "-metadata", "disc="   + cd        ,
            absdstpath
            ]
        
        try:
            self.Execute(process)
        except Exception as e:
            logging.error("Error \"%s\" while executing: %s", str(e), str(process))
            return False

        return True



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

