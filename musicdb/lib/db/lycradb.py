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
"""
Lyrics cache entry:

    +----+---------+--------+------------+-----+--------+
    | id | crawler | songid | updatetime | url | lyrics |
    +----+---------+--------+------------+-----+--------+

    crawler:
        Name of the crawler

    updatetime:
        Unix timestamp when this crawler entry was updated the last time

    url:
        URL from that the lyrics were loaded

    lyrics:
        The lyrics itself.
        This entry will be compressed using the :meth:`musicdb.lib.db.database.Database.Compress` method.
"""

from musicdb.lib.db.database import Database
import time
import logging

DBCOL_ID            = 0
DBCOL_CRAWLER       = 1
DBCOL_SONGID        = 2
DBCOL_UPDATETIME    = 3
DBCOL_URL           = 4
DBCOL_LYRICS        = 5

class LycraDatabase(Database):
    """
    Derived from :class:`musicdb.lib.db.database.Database`.

    Args:
        path (str): Absolute path to the LyCra database file.

    Raises:
        ValueError: When the version of the database does not match the expected version. (Updating MusicDB may failed)
    """

    def __init__(self, path):
        Database.__init__(self, path)
        try:
            result = self.GetFromDatabase("SELECT value FROM meta WHERE key = 'version'")
            version = int(result[0][0])
        except Exception as e:
            raise ValueError("Unable to read version number from Lycra Database")

        if version != 2:
            raise ValueError("Unexpected version number of Lycra Database. Got %i, expected %i", version, 2)



    def __LyricsCacheEntryToDict(self, entry):
        data = {}
        data["id"]           = entry[DBCOL_ID]
        data["crawler"]      = entry[DBCOL_CRAWLER]
        data["songid"]       = entry[DBCOL_SONGID]
        data["updatetime"]   = entry[DBCOL_UPDATETIME]
        data["url"]          = entry[DBCOL_URL]
        data["lyrics"]       = self.Decompress(entry[DBCOL_LYRICS])
        return data 



    def WriteLyricsToCache(self, crawler, songid, lyrics, url):
        """
        This method writes the lyrics a crawler found into the database.
        If there is already an entry for the combination of *songid* and *crawler*, this entry gets updated.

        The lyrics will be compressed.

        Args:
            crawler (str): Name of the crawler that found the lyrics
            songid (int): ID of the song of that the lyrics are
            lyrics (str): The lyrics that shall be stored
            url (str): The source of the lyrics

        Returns:
            None
        """
        # Get unixtime
        updatetime = int(time.time())

        # Get entry if already exists
        sql     = "SELECT * FROM lyricscache WHERE songid = ? AND crawler = ?"
        values  = (songid, crawler)
        results = self.GetFromDatabase(sql, values);
        if results:
            result = results[0]
        else:
            result = None

        lyrics = self.Compress(lyrics)

        # update if there is a result
        if result:
            sql    = "UPDATE lyricscache SET lyrics = ?, updatetime = ?, url = ? WHERE id = ?"
            values = (lyrics, updatetime, url, result[DBCOL_ID])
        # create new entry otherwise
        else:
            sql    = "INSERT INTO lyricscache (crawler, songid, lyrics, updatetime, url) VALUES (?, ?, ?, ?, ?)"
            values = (crawler, songid, lyrics, updatetime, url)

        self.Execute(sql, values)
        return None



    def GetLyricsFromCache(self, songid):
        """
        This method returns a list of all entries from the cache, that matches the *songid*.

        Args:
            songid (int): ID of a song

        Returns:
            A list of entries with lyrics, or ``None`` if nothing found.
        """
        sql     = "SELECT * FROM lyricscache WHERE songid = ?"
        results = self.GetFromDatabase(sql, songid)

        lyrics = []
        for entry in results:
            lyric = self.__LyricsCacheEntryToDict(entry)
            lyrics.append(lyric)

        return lyrics


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

