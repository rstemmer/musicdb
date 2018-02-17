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


from lib.database import Database

artists_scheme = """
    CREATE TABLE IF NOT EXISTS artists 
    (
        artistid    INTEGER PRIMARY KEY,
        name        TEXT,
        path        TEXT
    )
    """
albums_scheme = """
    CREATE TABLE IF NOT EXISTS albums 
    (
        albumid     INTEGER PRIMARY KEY, 
        artistid    INTEGER, 
        name        TEXT, 
        path        TEXT, 
        numofsongs  INTEGER, 
        numofcds    INTEGER, 
        origin      TEXT, 
        release     INTEGER,
        artworkpath TEXT DEFAULT 'default.jpg',
        bgcolor     TEXT DEFAULT '#080808',
        fgcolor     TEXT DEFAULT '#F0F0F0',
        hlcolor     TEXT DEFAULT '#909090'
    )
    """
songs_scheme = """
    CREATE TABLE IF NOT EXISTS songs 
    (
        songid      INTEGER PRIMARY KEY, 
        albumid     INTEGER, 
        artistid    INTEGER, 
        name        TEXT, 
        path        TEXT, 
        number      INTEGER, 
        cd          INTEGER,
        disabled    INTEGER,
        playtime    INTEGER,
        bitrate     INTEGER,
        likes       INTEGER DEFAULT 0,
        dislikes    INTEGER DEFAULT 0,
        qskips      INTEGER DEFAULT 0,
        qadds       INTEGER DEFAULT 0,
        qremoves    INTEGER DEFAULT 0,
        favorite    INTEGER DEFAULT 0,
        qrndadds    INTEGER DEFAULT 0,
        lyricsstate INTEGER DEFAULT 0
    )
    """

class LocalDatabase(Database):
    """

    Args:
        path (str): absolute path to the database file.

    Raises:
        TypeError: When *path* is not a string
    """

    def __init__(self, path):
        # check path
        if type(path) != str:
            raise TypeError("A valid database path is necessary")

        Database.__init__(self, path)

        # Create scheme if not exists
        self.Execute(artists_scheme)
        self.Execute(albums_scheme)
        self.Execute(songs_scheme)




# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

