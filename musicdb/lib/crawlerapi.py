# MusicDB,  a music manager with web-bases UI that focus on music.
# Copyright (C) 2017 - 2021  Ralf Stemmer <ralf.stemmer@gmx.net>
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

import logging
from musicdb.lib.db.lycradb import LycraDatabase
import time

# User must implement def DoCrawl(self, artistname, albumname, songname)
class LycraCrawler(object):
    """
    This is the base class for all crawler.

    Args:
        db: A :class:`~musicdb.lib.db.lycra.LycraDatabase` database object.
        name (str): Name of the crawler. It should be the same name the class and file have.
        version (str): A version number in format major.minor.patchlevel as string. For example ``"1.0.0"``

    Raises:
        TypeError: If the *db* argument is not of type :class:`~musicdb.lib.db.lycra.LycraDatabase`
        TypeError: If name or version number are not of type ``str``
    """
    def __init__(self, db, name, version):
        if type(db) != LycraDatabase:
            logging.error("Database of unknown type!")
            raise TypeError("Database of unknown type!")
        if type(name) != str or type(version) != str:
            logging.error("Invalid name or version type!")
            raise TypeError("Invalid name or version type!")

        self.name    = name
        self.version = version
        self.db      = db



    def Crawl(self, artistname, albumname, songname, songid):
        """
        This method gets called by the lyrics manager :class:`musicdb.mdbapi.lycra.Lycra`.
        It provides a small environment to fit the crawler into MusicDBs infrastructure.
        It catches exceptions and measures the time the crawler needs to run.

        Args:
            artistname (str): The name of the artist as stored in the MusicDatabase
            albumname (str): The name of the album as stored in the MusicDatabase
            songname (str): The name of the song as stored in the MusicDatabase
            songid (int): The ID of the song to associate the lyrics with the song

        Returns:
            ``True`` if the crawler found lyrics, otherwise ``False``
        """
        logging.info("Run Crawler \033[1;35m%s [\033[0;35m%s\033[1;35m]", str(self.name), str(self.version))
        starttime = time.time()
        try:
            retval = self.DoCrawl(artistname, albumname, songname, songid)
        except Exception as e:
            logging.error("Crawer %s failed with Error: %s.", str(self.name), str(e))
            return False
        duration = time.time() - starttime

        if retval == True:
            logging.debug("Lyrics found with crawler %s for song %s.", str(self.name), str(songname))
            found = "\033[1;32mYes"
        else:
            logging.debug("No Lyrics found with crawler %s.", str(self.name))
            found = "\033[1;31mNo"

        logging.info("Crawler \033[1;35m%s\033[1;34m finished after \033[1;36m%d\033[1;34ms. Lyrics found: %s", 
                str(self.name), duration, found)

        return retval



    def DoCrawl(self, artistname, albumname, songname, songid):
        """
        This is the prototype the derived class has to implement for crawling.

        Args:
            artistname (str): The name of the artist as stored in the music database
            albumname (str): The name of the album as stored in the music database
            songname (str): The name of the song as stored in the music database
            songid (int): The ID of the song to associate the lyrics with the song

        Returns:
            ``True`` if the crawler found lyrics, otherwise ``False``
        """
        return False



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

