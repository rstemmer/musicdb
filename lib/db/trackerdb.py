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
or its weight incremented.

There are two tables, one for song relations and one for video relations.

Because the tables contain similar information, their data and algorithms are similar. 
All methods are made to work on all tables.
The parameter *target* is either ``"song"`` or ``"video"`` and distinguish the tables.
If the documentation mentions *targetid* it either is the term *songid* or *videoid* depending on the argument of the method.

The tables layout is the following:


    +----+-----------+-----------+--------+
    | id | targetida | targetidb | weight |
    +----+-----------+-----------+--------+

id:
    ID of the row

targetida / targetidb:
    IDs of the songs or videos that were played together.
    ID A is the smaller number of the two: ``targetida < targetidb``.
    There will not be the situation where targetida and targetidb have the same ID.
    It is prevented by the method creating the relation.

weight:
    Gets incremented whenever the targetida/targetidb relation already occurred in the past.

This classes uses a global lock (using Python ``threading.RLock``) to avoid that relations change during complex operation.
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
        A target can be a song or a video.
        
        It does not matter which one is greater, *ida* or *idb*.
        This gets handled automatically.
        If *ida* and *idb* are the same ID, they get ignored.

        Args:
            target (str): ``"song"`` or ``"video"``
            ida (int): Song ID or Video ID, depending on the target string
            ida (int): Song ID or Video ID, depending on the target string

        Returns:
            ``None``

        Raises:
            ValueError: If *target* not ``"song"`` or ``"video"``
            TypeError: If *ida* or *idb* is not of type int
        """
        if target not in ["song", "video"]:
            raise ValueError("Unknown target \"%s\"! Only \"song\" and \"video\" allowed.", target)

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
            # if there is a result, increase the weight
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
        A target can be a song, a video or a video.
        
        It does not matter which one is greater, *ida* or *idb*.
        This gets handled automatically.
        If *ida* and *idb* are the same ID, they get ignored.

        Args:
            target (str): ``"song"``, ``"video"``
            ida (int): Song ID or Video ID, depending on the target string
            ida (int): Song ID or Video ID, depending on the target string

        Returns:
            ``None``

        Raises:
            ValueError: If *target* not ``"song"`` or ``"video"``
            TypeError: If *ida* or *idb* is not of type int

        """
        if target not in ["song", "video"]:
            raise ValueError("Unknown target \"%s\"! Only \"song\" and \"video\" allowed.", target)

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




    def RemoveSong(self, songid):
        """
        This method removes all relations to a song.
        This is usefull in case a song gets removed from the database.

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



    def RemoveVideo(self, videoid):
        """
        This method removes all relations to a video.
        This is useful in case a video gets removed from the database.

        If the video relation does not exist, nothing will be done.

        Args:
            videoid (int): ID of the video

        Returns:
            ``None``

        Raises:
            TypeError: Invalid video ID type
        """
        if type(videoid) != int:
            raise TypeError("Song IDs must be of type int!")

        with TrackerDatabaseLock:
            sql = "DELETE FROM videorelations WHERE videoida = ? OR videoidb = ?"
            self.Execute(sql, (videoid, videoid))

        return None



    def GetRelations(self, target, targetid):
        """
        This method returns the related songs or videos of a song or a video, depending on the value of *target*. 

        The method returns a list of dictionaries.
        Each dictionary contains the ID of the related song or video, and the weight of the relation.


        Args:
            target (str): ``song`` or ``video``
            targetid (int): Song ID or Video ID, depending on the target string

        Returns:
            List of relations. The list is empty if there are no relations

        Raises:
            ValueError: If *target* not ``"song"`` or ``"video"``
            TypeError: If *targetid* is not of type ``int``

        Example:

            .. code-block:: python

                relations = trackerdatabase.GetRelations("song", 1000)
                for r in relations:
                    print("Related song ID: %d; Weight: %d"%(r["id"], r["weight"]))
        """
        if target not in ["song", "video"]:
            raise ValueError("Unknown target \"%s\"! Only \"song\" and \"video\" allowed.", target)

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

