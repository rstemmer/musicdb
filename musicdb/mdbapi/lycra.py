# MusicDB,  a music manager with web-bases UI that focus on music.
# Copyright (C) 2017-2021  Ralf Stemmer <ralf.stemmer@gmx.net>
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
import imp
from musicdb.lib.cfg.musicdb    import MusicDBConfig
from musicdb.lib.db.lycradb     import LycraDatabase
from musicdb.lib.filesystem     import Filesystem

import os, sys
CRAWLERPATH = os.path.join(os.path.dirname(sys.argv[0]), "lib/crawler")

class Lycra(object):
    """
    This class does the main lyrics management.

    Args:
        config: MusicDB Configuration object.

    Raises:
        TypeError: when *config* is not of type :class:`~musicdb.lib.cfg.musicdb.MusicDBConfig`
    """
    def __init__(self, config):

        if type(config) != MusicDBConfig:
            logging.error("Config-class of unknown type!")
            raise TypeError("config argument not of type MusicDBConfig")

        logging.debug("Crawler path is %s", CRAWLERPATH)

        self.config     = config
        self.lycradb    = LycraDatabase(self.config.lycra.dbpath)
        self.fs         = Filesystem(CRAWLERPATH)
        self.crawlers   = None



    def LoadCrawlers(self):
        """
        This method loads all crawlers inside the crawler directory.

        .. warning::

            Changes at crawler may not be recognized until the whole application gets restarted.
            Only new added crawler gets loaded.
            Already loaded crawler are stuck at Pythons module cache.

        Returns:
            ``None``
        """
        # Get a list of all modules
        crawlerfiles = self.fs.GetFiles(".")
        modulenames  = [self.fs.GetFileName(x) for x in crawlerfiles if self.fs.GetFileExtension(x) == "py"]
        if len(modulenames) == 0:
            logging.warning("No modules found in \"%s\"! \033[1;30m(… but crawler cache is still usable.)", self.fs.AbsolutePath(CRAWLERPATH))
            self.crawlers = None
            return None

        # load all modules
        self.crawlers = []
        for modulename in modulenames:
            modfp, modpath, moddesc = imp.find_module(modulename, [CRAWLERPATH])

            try:
                logging.debug("Loading %s …", str(modpath))
                module = imp.load_module(modulename, modfp, modpath, moddesc)
            except Exception as e:
                logging.error("Loading Crawler %s failed with error: %s! \033[1;30m(Ignoring this specific Crawler)",
                        str(e),
                        str(modpath))
            finally:
                # Since we may exit via an exception, close fp explicitly.
                if modfp:
                    modfp.close()

            crawler = {}
            crawler["module"]       = module
            crawler["modulename"]   = modulename
            self.crawlers.append(crawler)

        if len(self.crawlers) == 0:
            logging.warning("No crawler loaded from \"%s\"! \033[1;30m(… but crawler cache is still usable.)", self.fs.AbsolutePath(CRAWLERPATH))
            self.crawlers = None
        return None 



    def RunCrawler(self, crawler, artistname, albumname, songname, songid):
        """
        This method runs a specific crawler.
        This crawler gets all information available to search for a specific songs lyric.

        This method is for class internal use.
        When using this class, call :meth:`~musicdb.mdbapi.lycra.Lycra.CrawlForLyrics` instead of calling this method directly.
        Before calling this method, :meth:`~musicdb.mdbapi.lycra.Lycra.LoadCrawlers` must be called.

        The crawler base class :class:`musicdb.lib.crawlerapi.LycraCrawler` catches all exceptions so that they do not net to be executed in an try-except environment.

        Args:
            crawler (str): Name of the crawler. If it addresses the file ``lib/crawler/example.py`` the name is ``example``
            artistname (str): The name of the artist as stored in the MusicDatabase
            albumname (str): The name of the album as stored in the MusicDatabase
            songname (str): The name of the song as stored in the MusicDatabase
            songid (int): The ID of the song to associate the lyrics with the song

        Returns:
            ``None``
        """
        crawlerclass    = getattr(crawler["module"], crawler["modulename"])
        crawlerentity   = crawlerclass(self.lycradb)
        crawlerentity.Crawl(artistname, albumname, songname, songid)
        return None



    def CrawlForLyrics(self, artistname, albumname, songname, songid):
        """
        Loads all crawler from the crawler directory via :meth:`~musicdb.mdbapi.lycra.Lycra.LoadCrawlers` 
        and runs them via :meth:`~musicdb.mdbapi.lycra.Lycra.RunCrawler`.

        Args:
            artistname (str): The name of the artist as stored in the music database
            albumname (str): The name of the album as stored in the music database
            songname (str): The name of the song as stored in the music database
            songid (int): The ID of the song to associate the lyrics with the song

        Returns:
            ``False`` if something went wrong. Otherwise ``True``. (This is *no* indication that there were lyrics found!)
        """
        # Load / Reload crawlers
        try:
            self.LoadCrawlers()
        except Exception as e:
            logging.error("Loading Crawlers failed with error \"%s\"! \033[1;30m(… but crawler cache is still usable.)", str(e))
            return False

        if not self.crawlers:
            return False

        for crawler in self.crawlers:
            self.RunCrawler(crawler, artistname, albumname, songname, songid)

        return True



    def GetLyrics(self, songid):
        """
        This method returns the lyrics of a song.
        See :meth:`musicdb.lib.db.lycradb.LycraDatabase.GetLyricsFromCache`
        """
        return self.lycradb.GetLyricsFromCache(songid)




# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

