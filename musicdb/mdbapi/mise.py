# MusicDB,  a music manager with web-bases UI that focus on music.
# Copyright (C) 2017 - 2024  Ralf Stemmer <ralf.stemmer@gmx.net>
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
This module provides a class to search for songs, albums and artists.
A fuzzy search algorithm gets used.
This not only allows typos, it also adapts the search to the natural situation that song names are hard to remember.

Before an object can be used, the :meth:`~musicdb.mdbapi.mise.MusicDBMicroSearchEngine.UpdateCache`
method must be called to generate the cache.

The cache consists of three lists of tuples. One list for Artists, Albums and Songs.
The Tuples contain the *ID* and the *normalized Name* (see :meth:`~musicdb.mdbapi.mise.MusicDBMicroSearchEngine.NormalizeString`).

If the `Levenshtein module <https://pypi.python.org/pypi/python-Levenshtein>`_ is installed, the search through all artists, albums and song is usually done in less than 100ms.
Without this module, you better not use this module only if time does matter.

Example:

    .. code-block:: python

        database = MusicDBConfig()
        mise     = MusicDBMicroSeachEngine(database)

        mise.UpdateCache()

        (artists, _ , _ ) = mise.Find("Rammsein")
        for artistid, conf in artists:
            artist = database.GetArtistById(artistid)
            print("Artist: %s, Confidence: %d"%(artist["name"], conf))

"""

import unicodedata
import re
from rapidfuzz          import fuzz
import datetime
import logging
from musicdb.lib.db.musicdb     import MusicDatabase
from musicdb.lib.cfg.musicdb    import MusicDBConfig


class MusicDBMicroSearchEngine(object):
    """
    Before an object can be used, the :meth:`~musicdb.mdbapi.mise.MusicDBMicroSearchEngine.UpdateCache`
    method must be called to generate the cache.

    Because a cache update can be triggered from any thread, a new database instance will be created
    for reading information from the database.

    Args:
        config: :class:`musicdb.lib.cfg.musicdb.MusicDBConfig` object for the path to the music database.

    Raises:
        TypeError: When the database argument is invalid.
    """
    def __init__(self, config):
        if type(config) != MusicDBConfig:
            logging.error("Configuration-class of unknown type or None! (MusicDBConfig instance expected)")
            raise TypeError("Configuration-class of unknown type or None! (MusicDBConfig instance expected)")

        self.config = config

        # the caches are lists of tuple of name and id (name, id)
        self.songcache   = None
        self.albumcache  = None
        self.artistcache = None


    def UpdateCache(self):
        """
        Updates the internal cache used for searching.

        This is the only place in this class where the music database gets accessed.

        .. warning::

            This method must be called in the same thread the database object was instantiated!

        Returns:
            ``None``
        """
        musicdb = MusicDatabase(self.config.files.musicdatabase)
        t_start = datetime.datetime.now()

        # 1. get all data from the database
        artists = musicdb.GetAllArtists()
        albums  = musicdb.GetAllAlbums()
        songs   = musicdb.GetAllSongs()

        # 2. build caches
        self.artistcache = self.__BuildCache(artists)
        self.albumcache  = self.__BuildCache(albums)
        self.songcache   = self.__BuildCache(songs)

        t_stop = datetime.datetime.now()
        logging.debug("Updating MiSE caches took %s.", str(t_stop - t_start))

        return None



    # data has to be a list of dicts with "id" and "name" as elements
    def __BuildCache(self, data):
        # first, sort the data
        data = sorted(data, key = lambda k: k["name"].lower())

        # now create a cache with the id and the normalized name
        cache = []
        for item in data:
            itemname = item["name"]
            itemid   = item["id"]

            # optimize name to make it faulttollerant
            itemname = self.NormalizeString(itemname)

            # add to cache
            cache.append((itemname, itemid))

        return cache



    def NormalizeString(self, string):
        """
        This method normalizes a string so that it is easier to find.
        The normalization is done in the following steps:

            #. Unicode normalization (method: NFKC)
            #. all characters to Lower Case
            #. removes leading and training spaces
            #. replaces multiple spaces to one space

        Args:
            string (str): A string that shall be normalized

        Returns:
            A normalized string
        """
        string = unicodedata.normalize("NFKC", string)
        string = string.lower()
        string = string.strip()
        string = re.sub(" +", " ", string)  # remove double/multi spaces
        return string
        


    # returns a tuple of artists albums and songs
    def Find(self, userinput):
        """
        This method searches through the caches of song, album and artist names.
        A fuzzy search gets applied and so the results matches only with a certain probability.

        Args:
            userinput (str): Search-Sting to search for. 
                             This string gets normalized before it is used to search.

        Returns:
            A tuple of lists of artists, albums and songs that were found.
            Each list entry is a tuple of an *ID* and the *Confidence*

        Example::

            (artists, albums, songs) = mise.Find("Rammsein")
            for artistid, conf in artists:
                print("ID: %d, Confidence: %d"%(artistid, conf))

        """
        if type(userinput) != str:
            return (None,None,None)

        searchstring = self.NormalizeString(userinput)

        t_start = datetime.datetime.now()
        artists = self.__FindInData(searchstring, self.artistcache)
        albums  = self.__FindInData(searchstring, self.albumcache)
        songs   = self.__FindInData(searchstring, self.songcache)
        t_stop  = datetime.datetime.now()
        t_diff  = t_stop - t_start

        if t_diff.seconds >= 1:
            logging.warning("Searching took %s", str(t_diff))
        else:
            logging.debug("Searching took %s", str(t_diff))

        return (artists, albums, songs)


    # return a tuple of id and ratio
    def __FindInData(self, searchstring, cache, threshold=80):
        result = []
        for element in cache:
            ratio = fuzz.partial_ratio(element[0], searchstring)
            if ratio >= threshold:
                result.append((element[1], ratio))

        # sort for highest ratio
        if result:
            result = sorted(result, key = lambda k: k[1], reverse=True)

        return result


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

