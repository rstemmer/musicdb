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
This module is used to manage the Tracker Database.

The database stores the relation between two songs.
That means, whenever two songs were played after each other, the relation gets created,
or its wehight incremented.

There are two tables, one for song relations and one for artists.
The artist relation could be determined out of the song relations, so the artist relation table can be seen as cache.

Because the two tables, their data and algorithms are similar, all methods are made to work on both tables.
The parameter *target* is either ``"song"`` or ``"artist"`` and distinguish the tables.
If the documentation mentions *targetid* it either is the term *songid* or *artistid* depending on the argument of the methond.


    +----+-----------+-----------+--------+
    | id | targetida | targetidb | weight |
    +----+-----------+-----------+--------+

id:
    ID of the row

targetida / targetidb:
    IDs of the songs or artists that were played together.
    ID A is the smaller number of the two: ``xida < xidb``.
    There will not be the situation where xida and xidb have the same ID.
    It is prevented by the method creating the relation.

weight:
    Gets incremented whenever the xida/xidb relation occures.

This classes uses a global lock (using Python ``threading.RLock``) to avoid that relations change during complex operation.
For example, when removing a songs relation, the artists relation weight must be decreased.
There are multiple database accesses necessary to do so.
Meanwhile, nothing should be changed by other threads.
"""

import logging
import sqlite3
import threading
from lib.db.database import Database
from lib.db.musicdb  import MusicDatabase

TrackerDatabaseLock = threading.RLock() # RLock is mandatory for nested calles!

class TrackerDatabase(Database):
    """
    Derived from :class:`lib.db.database.Database`.

    Args:
        path (str): Absolute path to the tracker database file.
    """

    def __init__(self, path):
        Database.__init__(self, path)
        

    def AddRelation(self, target, ida, idb):
        """
        This method adds a relation between two targets.
        A target can be a song or an artist.
        
        It does not matter which one is greater, *ida* or *idb*.
        This gets handled automatically.
        If *ida* and *idb* are the same ID, they get ignored.

        Args:
            target (str): ``song`` or ``artist``
            ida (int): Song ID or Artist ID, depending on the target string
            ida (int): Song ID or Artist ID, depending on the target string

        Returns:
            ``None``

        Raises:
            ValueError: If *target* not ``"song"`` or ``"artist"``
            TypeError: If *ida* or *idb* is not of type int
        """
        if target not in ["song", "artist"]:
            raise ValueError("Unknown target \"%s\"! Only \"song\" and \"artist\" allowed.", target)

        if type(ida) != int or type(idb) != int:
            raise TypeError("IDs must be of type int!")

        if ida == idb:
            logging.debug("%s IDs are the same. They will be ignored", target)
            return None

        # ida must be less than idb, if not, exchange the values
        if ida > idb:
            idb, ida = ida, idb

        with TrackerDatabaseLock:
            # Get edge if it already exists
            sql    = "SELECT id, weight FROM "+target+"relations WHERE "+target+"ida = ? AND "+target+"idb = ?"
            result = self.GetFromDatabase(sql, (ida, idb))

            # Define new weight - new edges have weight 1
            # if there is a result, increas the weight
            if result:
                relationid = result[0][0]# [(id, weight)]
                weight     = result[0][1]# [(id, weight)]

                sql = "UPDATE "+target+"relations SET weight = ? WHERE id = ?"
                self.Execute(sql, (weight + 1, relationid))
            else:
                sql = "INSERT INTO "+target+"relations ("+target+"ida, "+target+"idb) VALUES (?, ?)"
                self.Execute(sql, (ida, idb))

        return None



    def RemoveRelation(self, target, ida, idb):
        """
        This method removes a relation between two targets.
        A target can be a song or an artist.
        
        It does not matter which one is greater, *ida* or *idb*.
        This gets handled automatically.
        If *ida* and *idb* are the same ID, they get ignored.

        .. warning::

            Only the addressed edge gets removed!

            Removing an artist for example, does not remove song relations to this artist.
            You should use the following two higher level methods:
            
                * :meth:`~lib.db.trackerdb.TrackerDatabase.RemoveSongRelations`
                * :meth:`~lib.db.trackerdb.TrackerDatabase.RemoveArtistRelations`


        Args:
            target (str): ``song`` or ``artist``
            ida (int): Song ID or Artist ID, depending on the target string
            ida (int): Song ID or Artist ID, depending on the target string

        Returns:
            ``None``

        Raises:
            ValueError: If *target* not ``"song"`` or ``"artist"``
            TypeError: If *ida* or *idb* is not of type int

        Examples:

            Remove an artist connection and take care of removing its connection to songs.
            This is only an example! User :meth:`~lib.db.trackerdb.TrackerDatabase.RemoveArtistRelations` instead of this example code!

            .. code-block:: python

                # Defining the environment
                musicdb   = MusicDatabase("./music.db")
                trackerdb = TrackerDatabase("./tracker.db")
                artistida = 42
                artistidb = 23

                # Remove artist connection
                trackerdb.RemoveRelation("artist", artistida, artistidb)

                # Get all songs
                songlista = musicdb.GetSongsByArtistId(artistida)
                songlistb = musicdb.GetSongsByArtistId(artistidb)

                # Try remove all possible song connections
                for songa in songlista:
                    for songb in songlistb:
                        trackerdb.RemoveRelation("song", songa["id"], songb["id"])

        """
        if target not in ["song", "artist"]:
            raise ValueError("Unknown target \"%s\"! Only \"song\" and \"artist\" allowed.", target)

        if type(ida) != int or type(idb) != int:
            raise TypeError("IDs must be of type int!")

        if ida == idb:
            logging.debug("%s IDs are the same. They will be ignored", target)
            return None

        # ida must be less than idb, if not, exchange the values
        if ida > idb:
            idb, ida = ida, idb

        # Remove relation
        with TrackerDatabaseLock:
            sql = "DELETE FROM "+target+"relations WHERE "+target+"ida = ? AND "+target+"idb = ?"
            self.Execute(sql, (ida, idb))

        return None



    def RemoveSongRelations(self, musicdb, songida, songidb):
        """
        This method removes the relation of two songs.
        It also updates the related artist relations by subtracting the weight of the song connection from the connection of those artists.
        If the resulting artists-connection is zero, this relation gets also removed.

        If the song relation does not exist, nothing will be done.
        If the relation exist, there must be an artist relation.
        If not, an AssertionError gets raised.
        Only excepetion is the case where both songs are from the same artist.

        To get information about the songs of the artist, an instance of the :class:`~lib.db.musicdb.MusicDatabase` is necessary.
        This object must be given as argument.

        Args:
            musicdb: An instance of the music database to collect more information of the songs.
            songida (int): ID of one song
            songidb (int): ID of the other one

        Returns:
            ``None``

        Raises:
            TypeError: Invalid *musicdb* argument
            TypeError: Invalid song IDs
            AssertionError: If the artist relation of the two songs (from different artists) does not exist.
        """
        if type(musicdb) != MusicDatabase:
            raise TypeError("Invalid argument. musicdb not of type MusicDatabase")

        if type(songida) != int or type(songidb) != int:
            raise TypeError("Song IDs must be of type int!")

        # Get the weight for the song relation.
        # That value must be subtracted from the artists relation.
        # There is no method to get a specific weight.
        # So we need to access the database using basic methods.

        # be sure the order fulfills the constraint that ID A is smaller than ID B
        [songida, songidb] = sorted([songida, songidb])

        with TrackerDatabaseLock:
            # Get weight
            sql    = "SELECT weight FROM songrelations WHERE songida = ? AND songidb = ?"
            result = self.GetFromDatabase(sql, (songida, songidb))
            
            if not result:
                logging.warning("The expected song connection between %d and %d does not exist. (Doing nothing)",
                        songida, songidb)
                return None
            weight = result[0][0]   # [(weight,)]

            # Remove artist connection
            self.RemoveRelation("song", songida, songidb)

            # Determin the artist IDs
            artistida = musicdb.GetSongById(songida)["artistid"]
            artistidb = musicdb.GetSongById(songidb)["artistid"]

            if artistida == artistidb:
                return None

            # be sure the order fulfills the constraint that ID A is smaller than ID B
            [artistida, artistidb] = sorted([artistida, artistidb])

            # Get weight
            sql    = "SELECT id, weight FROM artistrelations WHERE artistida = ? AND artistidb = ?"
            result = self.GetFromDatabase(sql, (artistida, artistidb))

            if not result:
                # if there was a song connection, there must be an artist connection
                raise AssertionError("The expected artist connection does not exist!")
            edgeid      = result[0][0]   # [(id, weight)]
            edgeweight  = result[0][1]   # [(id, weight)]

            if edgeweight > weight:
                # subtract the weight from the song connection from the artist connection
                sql = "UPDATE artistrelations SET weight = ? WHERE id = ?"
                self.Execute(sql, (edgeweight - weight , edgeid))
            else:
                # Remove the artist connection
                self.RemoveRelation("artist", artistida, artistidb)

        return None



    def RemoveSong(self, songid):
        """
        This method removes all relations to a song.
        This is usefull in case a song gets removed from the database.

        The method does *not* update the artist relations!

        If the song relation does not exist, nothing will be done.

        Args:
            songid (int): ID of the song

        Returns:
            ``None``

        Raises:
            TypeError: Invalid song ID type
        """
        if type(songid) != int:
            raise TypeError("Song IDs must be of type int!")

        with TrackerDatabaseLock:
            sql = "DELETE FROM songrelations WHERE songida = ? OR songidb = ?"
            self.Execute(sql, (songid, songid))

        return None



    def RemoveArtistRelations(self, musicdb, artistida, artistidb):
        """
        This method removes the relationship between two artists and all song relations of them.

        If the artist relation does not exist, nothing will be done.

        To get information about the songs of the artist, an instance of the :class:`~lib.db.musicdb.MusicDatabase` is necessary.
        This object must be given as argument.

        Args:
            musicdb: An instance of the music database to collect more information of the songs.
            artistida (int): ID of one artist
            artistidb (int): ID of the other one

        Returns:
            ``None``

        Raises:
            TypeError: Invalid *musicdb* argument
            TypeError: Invalid artist IDs
        """
        if type(musicdb) != MusicDatabase:
            raise TypeError("Invalid argument. musicdb not of type MusicDatabase")

        if type(artistida) != int or type(artistidb) != int:
            raise TypeError("Artist IDs must be of type int!")

        with TrackerDatabaseLock:
            # Remove artist connection
            self.RemoveRelation("artist", artistida, artistidb)

            # Get all songs
            songlista = musicdb.GetSongsByArtistId(artistida)
            songlistb = musicdb.GetSongsByArtistId(artistidb)

            # Try remove all possible song connections
            for songa in songlista:
                for songb in songlistb:
                    self.RemoveRelation("song", songa["id"], songb["id"])

        return None



    def GetRelations(self, target, targetid):
        """
        This method returns the related songs or artists of a song or an artist, depending on the value of *target*. 

        The method returns a list of dictionaries.
        Each dictionary contains the ID of the related song or artist, and the weight of the relation.


        Args:
            target (str): ``song`` or ``artist``
            targetid (int): Song ID or Artist ID, depending on the target string

        Returns:
            List of relations. The list is empty if there are no relations

        Raises:
            ValueError: If *target* not ``"song"`` or ``"artist"``
            TypeError: If *targetid* is not of type ``int``

        Example:

            .. code-block:: python

                relations = trackerdatabase.GetRelations("song", 1000)
                for r in relations:
                    print("Related song ID: %d; Weight: %d"%(r["id"], r["weight"]))
        """
        if target not in ["song", "artist"]:
            raise ValueError("Unknown target \"%s\"! Only \"song\" and \"artist\" allowed.", target)

        if type(targetid) != int:
            raise TypeError("targetid must be of type int!")

        with TrackerDatabaseLock:
            sqla    = "SELECT "+target+"ida, weight FROM "+target+"relations WHERE "+target+"idb = ?"
            sqlb    = "SELECT "+target+"idb, weight FROM "+target+"relations WHERE "+target+"ida = ?"

            relationsa= self.GetFromDatabase(sqla, targetid)
            relationsb= self.GetFromDatabase(sqlb, targetid)

        if relationsa:
            relations = relationsa
            relations.extend(relationsb)
        else:
            relations = relationsb

        if not relations:
            return []

        results = []
        for (xid, weight) in relations:
            result = {}
            result["id"]    = xid
            result["weight"]= weight

            results.append(result)

        return results


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

