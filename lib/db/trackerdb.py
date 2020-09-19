# MusicDB,  a music manager with web-bases UI that focus on music.
# Copyright (C) 2017 - 2020  Ralf Stemmer <ralf.stemmer@gmx.net>
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

The database stores the relation between two songs or videos.
That means, whenever two songs or videos were played after each other, this relation gets created
or its wehight incremented.

There are three tables, one for song relations one for video relations and one for artists.
The artist relation will be determined out of the song relations, so the artist relation table can be seen as cache.

.. important::

    Adding a video relation does not influence the artists relation table.
    MusicDB focus on audio-aspects. Videos are an addition that have lower priority.
    So there is a strict separation between songs and videos.
    This separation my be loosened in future versions, but for now videos shall not influence the old behavior of how song relations are tracked.

Because the three tables sore similar information, their data and algorithms are similar. 
All methods are made to work on all tables.
The parameter *target* is either ``"song"``, ``"video"`` or ``"artist"`` and distinguish the tables.
If the documentation mentions *targetid* it either is the term *songid*, *videoid* or *artistid* depending on the argument of the method.

The tables layout is the following:


    +----+-----------+-----------+--------+
    | id | targetida | targetidb | weight |
    +----+-----------+-----------+--------+

id:
    ID of the row

targetida / targetidb:
    IDs of the songs, videos or artists that were played together.
    ID A is the smaller number of the two: ``targetida < targetidb``.
    There will not be the situation where targetida and targetidb have the same ID.
    It is prevented by the method creating the relation.

weight:
    Gets incremented whenever the targetida/targetidb relation already occurred in the past.

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

TrackerDatabaseLock = threading.RLock() # RLock is mandatory for nested calls!

class TrackerDatabase(Database):
    """
    Derived from :class:`lib.db.database.Database`.

    Args:
        path (str): Absolute path to the tracker database file.

    Raises:
        ValueError: When the version of the database does not match the expected version. (Updating MusicDB may failed)
    """

    def __init__(self, path):
        Database.__init__(self, path)
        try:
            result = self.GetFromDatabase("SELECT value FROM meta WHERE key = 'version'")
            version = int(result[0][0])
        except Exception as e:
            raise ValueError("Unable to read version number from Tracker Database")

        if version != 3:
            raise ValueError("Unexpected version number of Tracker Database. Got %i, expected %i", version, 3)
        

    def AddRelation(self, target, ida, idb):
        """
        This method adds a relation between two targets.
        A target can be a song or an artist.
        
        It does not matter which one is greater, *ida* or *idb*.
        This gets handled automatically.
        If *ida* and *idb* are the same ID, they get ignored.

        Args:
            target (str): ``"song"``, ``"video"`` or ``"artist"``
            ida (int): Song ID, Video ID or Artist ID, depending on the target string
            ida (int): Song ID, Video ID or Artist ID, depending on the target string

        Returns:
            ``None``

        Raises:
            ValueError: If *target* not ``"song"``, ``"video"`` or ``"artist"``
            TypeError: If *ida* or *idb* is not of type int
        """
        if target not in ["song", "video", "artist"]:
            raise ValueError("Unknown target \"%s\"! Only \"song\", \"video\" and \"artist\" allowed.", target)

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
        A target can be a song, a video or an artist.
        
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
            target (str): ``"song"``, ``"video"`` or ``"artist"``
            ida (int): Song ID, Video ID or Artist ID, depending on the target string
            ida (int): Song ID, Video ID or Artist ID, depending on the target string

        Returns:
            ``None``

        Raises:
            ValueError: If *target* not ``"song"``, ``"video"`` or ``"artist"``
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
        if target not in ["song", "video", "artist"]:
            raise ValueError("Unknown target \"%s\"! Only \"song\", \"video\" and \"artist\" allowed.", target)

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



    def RemoveArtist(self, artistid):
        """
        This method removes all relations to an artist.
        This is useful in case a artist gets removed from the database.
        Its song relations must be removed separately by calling :meth:`~RemoveSong` for each song.

        If the artist relation does not exist, nothing will be done.

        Args:
            artistid (int): ID of the artist

        Returns:
            ``None``

        Raises:
            TypeError: Invalid artist ID type
        """
        if type(artistid) != int:
            raise TypeError("Song IDs must be of type int!")

        with TrackerDatabaseLock:
            sql = "DELETE FROM artistrelations WHERE artistida = ? OR artistidb = ?"
            self.Execute(sql, (artistid, artistid))

        return None



    def RemoveVideoRelations(self, videoida, videoidb):
        """
        This method removes the relationship between two videos.

        If the video relation does not exist, nothing will be done.

        Args:
            videoida (int): ID of one video
            videoidb (int): ID of the other one

        Returns:
            ``None``

        Raises:
            TypeError: Invalid video IDs
        """
        if type(videoida) != int or type(videoidb) != int:
            raise TypeError("Video IDs must be of type int!")

        with TrackerDatabaseLock:
            self.RemoveRelation("video", videoida, videoidb)

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

