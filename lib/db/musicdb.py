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
This class manages the *MusicDB Database* the core of *MusicDB*.
It caches information from the filesystem and provides augmentation of those files.
This database handles the following components:

    * `Songs`_
    * `Albums`_
    * `Artists`_
    * `Artworks`_
    * `Lyrics`_
    * `Tags`_

All database entries (= rows) are handled as dictionaries.
The key of the dictionary corresponds to the column name of the database.

If an entry of this dictionary got changed directly, the following methods can be used to store the changes in the database.
This is not the recommended way because the content gets not checked.
The preferred way to change any data is using the related method described in the following sections.

    * :meth:`~lib.db.musicdb.MusicDatabase.WriteArtist`
    * :meth:`~lib.db.musicdb.MusicDatabase.WriteAlbum`
    * :meth:`~lib.db.musicdb.MusicDatabase.WriteSong`
    * :meth:`~lib.db.musicdb.MusicDatabase.WriteTag`

Adding a Column
---------------

When a new column shall be added, the following steps are necessary.

    #. Shutdown the server: ``echo "shutdown" > /data/musicdb/musicdb.fifo``
    #. Backup the database: ``sqlite3 music.db .dump > backup/music.db.bak``
    #. Update this file.
    #. Update the SQL file *sql/music.sql*
    #. Modify the database:
        #. Open: ``sqlite3 music.db``
        #. Add column. For example ``ALTER TABLE songs ADD COLUMN feature INTEGER DEFAULT 0;``
        #. Quit: ``.quit``

Furthermore be sure that all command line modules and API modules handle the new added column, and so new added feature correct.
For example, methods creating a new entry in the modified table may be adopted.

Songs
-----

The columns of the songs table are the following:

    +--------+---------+----------+------+------+
    | songid | albumid | artistid | name | path |
    +--------+---------+----------+------+------+

    +--------+----+----------+----------+---------+
    | number | cd | disabled | playtime | bitrate |
    +--------+----+----------+----------+---------+
    
    +-------+----------+--------+-------+----------+----------+----------+
    | likes | dislikes | qskips | qadds | qremoves | favorite | qrndadds |
    +-------+----------+--------+-------+----------+----------+----------+

    +-------------+----------+------------+
    | lyricsstate | checksum | lastplayed |
    +-------------+----------+------------+

checksum (Text)
    This is the *sha256* hash value of the file addressed by ``path``.
    The checksum will be calculated like shown in the following example:

    .. code-block:: python

        songpath = song["path"]
        songfile = open(songpath, "rb")
        
        with open(songpath, "rb") as songfile:
            checksum = hashlib.sha256(songfile.read()).hexdigest()

        song["checksum"] = checksum

    The hash function will not be changed in future.
    This is OK as long as the hash value will not be used for security related things!

    It can happen, that the value is empty (``""``).
    This only means that the checksum of the song was not calculated yet.
    In this case, just calculate it, and write it into the database.

lastplayed (Integer)
    This value holds the information, when the song was played the last time.
    The thime gets represented as an integer (unixtime).


Song Relates Methods
^^^^^^^^^^^^^^^^^^^^

The following methods exist to handle song entries in the database:

    * :meth:`~lib.db.musicdb.MusicDatabase.AddSong`
    * :meth:`~lib.db.musicdb.MusicDatabase.AddFullSong`
    * :meth:`~lib.db.musicdb.MusicDatabase.GetSongById`
    * :meth:`~lib.db.musicdb.MusicDatabase.GetSongByPath`
    * :meth:`~lib.db.musicdb.MusicDatabase.GetSongsByArtistId`
    * :meth:`~lib.db.musicdb.MusicDatabase.GetSongsByAlbumId`
    * :meth:`~lib.db.musicdb.MusicDatabase.GetAllSongs`
    * :meth:`~lib.db.musicdb.MusicDatabase.GetSongs`
    * :meth:`~lib.db.musicdb.MusicDatabase.GetRandomSong`
    * :meth:`~lib.db.musicdb.MusicDatabase.GetSongIdsByAlbumIds`
    * :meth:`~lib.db.musicdb.MusicDatabase.UpdateSongStatistic`
    * :meth:`~lib.db.musicdb.MusicDatabase.RemoveSong`




Albums
------

Data structure:

    +---------+----------+------+------+------------+----------+--------+---------+
    | albumid | artistid | name | path | numofsongs | numofcds | origin | release |
    +---------+----------+------+------+------------+----------+--------+---------+

    +-------------+---------+---------+---------+
    | artworkpath | bgcolor | fgcolor | hlcolor |
    +-------------+---------+---------+---------+

Album Related Methods
^^^^^^^^^^^^^^^^^^^^^

    * :meth:`~lib.db.musicdb.MusicDatabase.AddAlbum`
    * :meth:`~lib.db.musicdb.MusicDatabase.GetAlbumByPath`
    * :meth:`~lib.db.musicdb.MusicDatabase.GetAlbumById`
    * :meth:`~lib.db.musicdb.MusicDatabase.GetAllAlbums`
    * :meth:`~lib.db.musicdb.MusicDatabase.GetAlbumsByArtistId`
    * :meth:`~lib.db.musicdb.MusicDatabase.GetAlbums`
    * :meth:`~lib.db.musicdb.MusicDatabase.GetAllAlbumIds`
    * :meth:`~lib.db.musicdb.MusicDatabase.RemoveAlbum`

Artworks
^^^^^^^^

    * :meth:`~lib.db.musicdb.MusicDatabase.SetArtwork`
    * :meth:`~lib.db.musicdb.MusicDatabase.SetArtworkColorByAlbumId`

Origin
^^^^^^

Valid values:

    * ``"iTunes"``
    * ``"bandcamp"``
    * ``"music163"`` aka 网易云音乐
    * ``"CD"`` as fallback for unknown *flac* files
    * ``"internet"`` as fallback for any other unknown files

Artists
-------

Database structure:

        +----------+------+------+
        | artistid | name | path |
        +----------+------+------+

    * :meth:`~lib.db.musicdb.MusicDatabase.AddArtist`
    * :meth:`~lib.db.musicdb.MusicDatabase.GetAllArtists`
    * :meth:`~lib.db.musicdb.MusicDatabase.GetArtistByPath`
    * :meth:`~lib.db.musicdb.MusicDatabase.GetArtistById`
    * :meth:`~lib.db.musicdb.MusicDatabase.RemoveArtist`

Lyrics
------

Lyrics state is part of the *songs* table.
The lyrics itself are stored in the *lyrics* table with the following layout:

    +--------+--------+
    | songid | lyrics |
    +--------+--------+

Lyrics are stored in a simple markup language:

    * ``:: ref`` starts a section for the refrain
    * ``:: comment`` starts a section for comments that are not part of the lyrics
    * ``::`` ends a section
    * ``<<…>>`` "highlight" text - use secondary color for printing this text

A lyrics entry could look like the following example:

    .. code-block:: python

        :: comment
        Just a dummy text
        ::

        Lorem ipsum dolor sit amet, 
        consetetur sadipscing elitr, 
        sed diam nonumy eirmod tempor 
        invidunt ut labore et dolore 
        magna aliquyam erat, 
        sed diam voluptua. 
        
        :: ref
        At vero eos et accusam et justo duo dolores et ea rebum. 
        Stet clita kasd gubergren, 
        no sea takimata sanctus est Lorem ipsum dolor sit amet. 
        ::

        << (5 times) >>

    * :meth:`~lib.db.musicdb.MusicDatabase.GetLyrics`
    * :meth:`~lib.db.musicdb.MusicDatabase.SetLyrics`

The *lyrics* column can have the following states:

    * ``SONG_LYRICSSTATE_EMPTY`` - There are no lyrics set yet
    * ``SONG_LYRICSSTATE_FROMFILE`` - The lyrics set come from the metatags of the song file
    * ``SONG_LYRICSSTATE_FROMNET`` - The lyrics were grabbed from the internet by a crawler
    * ``SONG_LYRICSSTATE_FROMUSER`` - The lyrics were reviewed by the user. This noted the highest state of quality for lyrics.
    * ``SONG_LYRICSSTATE_NONE`` - There are no lyrics for this song - it is an instrumental song.

Tags
----

In this section, the tag management is described.
A *Toxi* scheme is used to implement the tag system in MusicDB.
This means there are n+2 tables: 

   #. A Table with the definition of a tag, 
   #. a table that maps the tag to an entity, 
   #. and *n* tables with entities with a global unique identifier.

MusicDB does not have global unique identifier for artists, albums an genres, so instead of one mapping table, there are two.
One for the songs, and one for the albums.
Tags for Artists are not expected.
If there will be a need later on, it an easy be implemented by adding a third mapping table and/or introducing new classes of tags.
A tag must be identifiable by the combination of its name and class.

Tag Definition Table
^^^^^^^^^^^^^^^^^^^^

    +-------+------+-------+----------+----------+------+-------+------+------+
    | 0     | 1    | 2     | 3        | 4        | 5    | 6     | 7    | 8    |
    +-------+------+-------+----------+----------+------+-------+------+------+
    | TagID | Name | Class | ParentID | IconType | Icon | Color | PosX | PosY |
    +-------+------+-------+----------+----------+------+-------+------+------+

TagID (Integer)
   ID of the tag that gets generated by the database

Name (String)
   Name of the tag. It will be used inside the MusicDB code or by the UI as it is stored in the database.
   So, the name is set as it shall be displayed.
   It must also be a unique name inside its class.

Class (Integer)
   ID of the class:
  
   * ``1`` - Genre
   * ``2`` - Subgenre
   * ``3`` - Mood

ParentID (Integer / None)
   ID of a related tag. In case of subgenre, the main genres ID would be the ParentID.
   **Important:** A parent tag must always be of class *Genre*. And only *Subgenre* can and must have a parent!

IconType (Integer / None)
   If ``None`` the icon-column will be ignored. Otherwise it defines the type of icon:

   * ``1`` - Unicode character
   * ``2`` - HTML tag for special fonts: ``<i class="fa fa-beer"></i>``
   * ``3`` - png image **Future feature - specification incomplete**
   * ``4`` - svg image **Future feature - specification incomplete**

Icon (Text / None)
   A shorter version of the name. The Icon must be compatible to the specified type.

Color (Text / None)
   A HTML-like color code that can be used to highlight a very special tag. Do not use this feature too much, it can break the UI visual design.

PosX, PosY (Integer / None)
   The (X;Y) Position of the Name or the Icon in a grid if the tags were presented as grid in an UI.
   The tag position gets stored in the global database to make sure that every UI provides a similar layout of the tags to make it more usable.
   ``(0;0)`` is the upper left corner.
   If not a grid but a list gets described, ``posx`` determines the position and ``posy`` is set to ``NULL``.


Tag Mapping Table
^^^^^^^^^^^^^^^^^

The mapping-tables have all the same layout

    +----------+----------+----------+------------+----------+
    | 0        | 1        | 2        | 3          | 4        |
    +----------+----------+----------+------------+----------+
    | EntryID  | SongID   | TagID    | Confidence | Approval |
    +----------+----------+----------+------------+----------+
    | EntryID  | AlbumID  | TagID    | Confidence | Approval |
    +----------+----------+----------+------------+----------+

EntryID (Integer)
   ID of the entry in the mapping-table

TagID (Integer)
   ID of the tag in the Tag-Definition-Table

xxxID (Integer)
   ID of the song or album entry in the related tables

Confidence (Floating point, Default: 1.0)
   Confidence that the tag is correct.
   This is important in case an AI set the tag (See *Approval*).
   Otherwise this column can be ignored. - Ignoring means setting it to ``1.0``!
   
Approval (Integer, Default: 1)
   Three stages to approve the tag.

   * ``0`` - Set by AI. This tag may be wrong. The *Confidence* value is relevant in this case.
   * ``1`` - Set by the User. *Confidence* must be set to ``1.0``
   * ``2`` - Can be used for training. This Song/Album is a good representation for this tag. It can be used to train an AI.


Database API
^^^^^^^^^^^^^

    * :meth:`~lib.db.musicdb.MusicDatabase.CreateTag`
    * :meth:`~lib.db.musicdb.MusicDatabase.GetAllTags`
    * :meth:`~lib.db.musicdb.MusicDatabase.GetTagByName`
    * :meth:`~lib.db.musicdb.MusicDatabase.DeleteTag`
    * :meth:`~lib.db.musicdb.MusicDatabase.ModifyTag`
    * :meth:`~lib.db.musicdb.MusicDatabase.SetTargetTag`
    * :meth:`~lib.db.musicdb.MusicDatabase.RemoveTargetTag`
    * :meth:`~lib.db.musicdb.MusicDatabase.GetTargetTags`
    * :meth:`~lib.db.musicdb.MusicDatabase.SplitTagsByClass`

The following tag classes exist:

    * ``MusicDatabase.TAG_CLASS_GENRE``: Main genres like Metal, Electro, Classic, …
    * ``MusicDatabase.TAG_CLASS_SUBGENRE``: Subgenre like Dark Metal, New Wave, …
    * ``MusicDatabase.TAG_CLASS_MOOD``: Moods like Lucky, Sad, …

A target can be "song" or "album".
"""

import random
import logging
import threading
from lib.db.database import Database

SONG_LYRICSSTATE_EMPTY    = 0
SONG_LYRICSSTATE_FROMFILE = 1
SONG_LYRICSSTATE_FROMNET  = 2
SONG_LYRICSSTATE_FROMUSER = 3
SONG_LYRICSSTATE_NONE     = 4 # for instrumental songs

MusicDatabaseLock = threading.RLock() # RLock is mandatory for nested calles!

class MusicDatabase(Database):
    """
    This class is the interface to the Music Database.
    It is derived from :class:`lib.db.database.Database`.

    Args:
        path: path to the music database
    """
    ARTIST_ID     = 0
    ARTIST_NAME   = 1
    ARTIST_PATH   = 2

    ALBUM_ID         = 0
    ALBUM_ARTISTID   = 1
    ALBUM_NAME       = 2
    ALBUM_PATH       = 3
    ALBUM_NUMOFSONGS = 4
    ALBUM_NUMOFCDS   = 5
    ALBUM_ORIGIN     = 6 # iTunes, Netz, CD
    ALBUM_RELEASE    = 7
    ALBUM_ARTWORKPATH= 8
    ALBUM_BGCOLOR    = 9
    ALBUM_FGCOLOR    = 10
    ALBUM_HLCOLOR    = 11

    SONG_ID         = 0
    SONG_ALBUMID    = 1
    SONG_ARTISTID   = 2
    SONG_NAME       = 3
    SONG_PATH       = 4
    SONG_NUMBER     = 5
    SONG_CD         = 6
    SONG_DISABLED   = 7
    SONG_PLAYTIME   = 8
    SONG_BITRATE    = 9
    SONG_LIKES      = 10
    SONG_DISLIKES   = 11
    SONG_QSKIPS     = 12
    SONG_QADDS      = 13
    SONG_QREMOVES   = 14
    SONG_FAVORITE   = 15
    SONG_QRNDADDS   = 16
    SONG_LYRICSSTATE = 17
    SONG_CHECKSUM   = 18
    SONG_LASTPLAYED = 19
    # Q* : Queue statistics

    TAG_ID          = 0
    TAG_NAME        = 1
    TAG_CLASS       = 2
    TAG_CLASS_GENRE         = 1 # genre-tags (metal, electro, …)
    TAG_CLASS_SUBGENRE      = 2 # subgenre (dark metal, …)
    TAG_CLASS_MOOD          = 3 # moods (lucky, sad, …)
    TAG_PARENTID    = 3
    TAG_ICONTYPE    = 4
    TAG_ICONTYPE_UNICODE    = 1
    TAG_ICONTYPE_HTML       = 2
    TAG_ICON        = 5
    TAG_COLOR       = 6
    TAG_POSX        = 7
    TAG_POSY        = 8

    # For albumtags and songtags table
    TAGMAP_ENTRYID      = 0
    TAGMAP_TARGETID     = 1 # can be SongID or AlbumID, depening on the map
    TAGMAP_TAGID        = 2
    TAGMAP_CONFIDENCE   = 3
    TAGMAP_APPROVAL     = 4

    LYRIC_SONGID = 0
    LYRIC_LYRIC  = 1

    SUBGENRE_ID         = 0
    SUBGENRE_NAME       = 1
    SUBGENRE_MAINGENRE  = 2

    def __init__(self, path):
        Database.__init__(self, path)
        

    def __ArtistEntryToDict(self, entry):
        artist = {}
        artist["id"]   = entry[self.ARTIST_ID]
        artist["name"] = entry[self.ARTIST_NAME]
        artist["path"] = entry[self.ARTIST_PATH]
        return artist
        
    def __AlbumEntryToDict(self, entry):
        album = {}
        album["id"]         = entry[self.ALBUM_ID]
        album["artistid"]   = entry[self.ALBUM_ARTISTID]
        album["name"]       = entry[self.ALBUM_NAME]
        album["path"]       = entry[self.ALBUM_PATH]
        album["numofsongs"] = entry[self.ALBUM_NUMOFSONGS]
        album["numofcds"]   = entry[self.ALBUM_NUMOFCDS]
        album["origin"]     = entry[self.ALBUM_ORIGIN]
        album["release"]    = entry[self.ALBUM_RELEASE]
        album["artworkpath"]= entry[self.ALBUM_ARTWORKPATH]
        album["bgcolor"]    = entry[self.ALBUM_BGCOLOR]
        album["fgcolor"]    = entry[self.ALBUM_FGCOLOR]
        album["hlcolor"]    = entry[self.ALBUM_HLCOLOR]
        return album

    def __SongEntryToDict(self, entry):
        song = {}
        song["id"]          = entry[self.SONG_ID]
        song["albumid"]     = entry[self.SONG_ALBUMID]
        song["artistid"]    = entry[self.SONG_ARTISTID]
        song["name"]        = entry[self.SONG_NAME]
        song["path"]        = entry[self.SONG_PATH]
        song["number"]      = entry[self.SONG_NUMBER]
        song["cd"]          = entry[self.SONG_CD]
        song["disabled"]    = entry[self.SONG_DISABLED]
        song["playtime"]    = entry[self.SONG_PLAYTIME]
        song["bitrate"]     = entry[self.SONG_BITRATE]
        song["likes"]       = entry[self.SONG_LIKES]
        song["dislikes"]    = entry[self.SONG_DISLIKES]
        song["qskips"]      = entry[self.SONG_QSKIPS]
        song["qadds"]       = entry[self.SONG_QADDS]
        song["qremoves"]    = entry[self.SONG_QREMOVES]
        song["favorite"]    = entry[self.SONG_FAVORITE]
        song["qrndadds"]    = entry[self.SONG_QRNDADDS]
        song["lyricsstate"] = entry[self.SONG_LYRICSSTATE]
        song["checksum"]    = entry[self.SONG_CHECKSUM]
        song["lastplayed"]  = entry[self.SONG_LASTPLAYED]
        return song

    def __TagEntryToDict(self, entry):
        tag = {}
        tag["id"]           = entry[self.TAG_ID]
        tag["name"]         = entry[self.TAG_NAME]
        tag["class"]        = entry[self.TAG_CLASS]
        tag["parentid"]     = entry[self.TAG_PARENTID]
        tag["icontype"]     = entry[self.TAG_ICONTYPE]
        tag["icon"]         = entry[self.TAG_ICON]
        tag["color"]        = entry[self.TAG_COLOR]
        tag["posx"]         = entry[self.TAG_POSX]
        tag["posy"]         = entry[self.TAG_POSY]
        return tag

    def __AlbumTagEntryToDict(self, entry):
        return self.__TagMapToDict(entry, "albumid")
    def __SongTagEntryToDict(self, entry):
        return self.__TagMapToDict(entry, "songid")

    def __TagMapEntryToDict(self, entry, targetidname):
        tag = {}
        tag["entryid"]      = entry[self.TAGMAP_ENTRYID]
        tag[targetidname]   = entry[self.TAGMAP_TARGETID]
        tag["tagid"]        = entry[self.TAGMAP_TAGID]
        tag["confidence"]   = entry[self.TAGMAP_CONFIDENCE]
        tag["approval"]     = entry[self.TAGMAP_APPROVAL]
        return tag

    def __SubgenreEntryToDict(self, entry):
        subgenre = {}
        subgenre["id"]       = entry[self.SUBGENRE_ID]
        subgenre["name"]     = entry[self.SUBGENRE_NAME]
        subgenre["maingenre"]= entry[self.SUBGENRE_MAINGENRE]
        return subgenre 


    def WriteArtist(self, artist):
        """
        Updates the whole row for an artist.
        """
        sql = """
        UPDATE artists SET
            name=:name,
            path=:path
        WHERE
            artistid=:id
        """
        with MusicDatabaseLock:
            self.Execute(sql, artist)
        return None

    def WriteAlbum(self, album):
        """
        Updates the whole row for an album.
        """
        sql = """
        UPDATE albums SET
            artistid=:artistid,
            name=:name,
            path=:path,
            numofsongs=:numofsongs,
            numofcds=:numofcds,
            origin=:origin,
            release=:release,
            artworkpath=:artworkpath,
            bgcolor=:bgcolor,
            fgcolor=:fgcolor,
            hlcolor=:hlcolor
        WHERE
            albumid=:id
        """
        with MusicDatabaseLock:
            self.Execute(sql, album)
        return None

    def WriteSong(self, song):
        """
        Updates the whole row for a song.

        Args:
            song: A dictionary representing a whole row in the songs table

        Returns:
            ``None``
        """
        sql = """
        UPDATE songs SET
            albumid=:albumid,
            artistid=:artistid,
            name=:name,
            path=:path,
            number=:number,
            cd=:cd,
            disabled=:disabled,
            playtime=:playtime,
            bitrate=:bitrate,
            likes=:likes,
            dislikes=:dislikes,
            qskips=:qskips,
            qadds=:qadds,
            qremoves=:qremoves,
            favorite=:favorite,
            qrndadds=:qrndadds,
            lyricsstate=:lyricsstate,
            checksum=:checksum,
            lastplayed=:lastplayed
        WHERE
            songid=:id
        """
        with MusicDatabaseLock:
            self.Execute(sql, song)
        return None

    def WriteTag(self, tag):
        """
        Updates the whole row for a tag.
        """
        sql = """
        UPDATE tags SET
            name=:name,
            class=:class,
            parentid=:parentid,
            icontype=:icontype,
            icon=:icon,
            color=:color,
            posx=:posx,
            posy=:posy
        WHERE
            tagid=:id
        """
        with MusicDatabaseLock:
            self.Execute(sql, tag)
        return None



    ##########################################################################
    # ARTISTS                                                                #
    ##########################################################################


    def AddArtist(self, name, path):
        """
        Adds a new artist into the artists table

        Args:
            name (str): name of the artist
            path (str): relative path of the artist directory

        Returns:
            ``None``

        Raises:
            TypeError: If *path* is not of type ``str``
        """
        # Check arguments
        if type(path) != str:
            raise TypeError("Path must have a string-value!")

        # create new entry
        values = (name, path)
        sql = "INSERT INTO artists (name, path) VALUES ( ?, ?)"
        with MusicDatabaseLock:
            self.Execute(sql, values)
        return None



    def GetAllArtists(self):
        """
        Returns a list of all artists in the artists table.

        Returns:
            List of all artists
        """
        sql = "SELECT * FROM artists"
        with MusicDatabaseLock:
            result = self.GetFromDatabase(sql)

        artists = []
        for entry in result:
            artist = self.__ArtistEntryToDict(entry)

            artists.append(artist)

        return artists



    def GetArtistByPath(self, path):
        """
        Returns the artist by the relative path of the music directory.
        This is usually only a directroy name.

        Args:
            parth (str): relative path of an artist

        Returns:
            The database entry of the artist or ``None`` if there is no entry for this artist directory

        Raises:
            TypeError: When *path* is not a string
            AssertionError: When there is no artist with the given path
        """
        if type(path) != str:
            raise TypeError("Path must have a string-value!")

        # check if this artist exists
        sql = "SELECT * FROM artists WHERE path = ?"
        with MusicDatabaseLock:
            result = self.GetFromDatabase(sql, path)

        # check result
        if not result:
            return None
        
        if len(result) > 1:
            raise AssertionError("Multiple Artist entries for one directory in database!")

        entry = result[0] # remove the list thing, now it's just a tuple
        retval = self.__ArtistEntryToDict(entry)
        return retval


    def GetArtistById(self, artistid):
        """
        Returns the artist by its ID

        Args:
            artistid: ID of the artist in the artist table

        Returns:
            The database entry of the artist or ``None`` if there is no entry for this artist directory

        Raises:
            TypeError: When *artistid* is not an integer or a string
            ValueError: When *artistid* is a string that cannot be interpreted as a decimal number
            AssertionError: When there is more than one entry with the same ID (This should never happen)
        """
        if type(artistid) == str:
            try:
                artistid = int(artistid)
            except ValueError:
                raise ValueError("ArtistID must be a decimal number!")

        if type(artistid) != int:
            raise TypeError("ArtistID must be of type int or str and is a decimal number!")

        # check if this artist exists
        sql = "SELECT * FROM artists WHERE artistid = ?"
        with MusicDatabaseLock:
            result = self.GetFromDatabase(sql, artistid)

        # check result
        if not result:
            return None
        
        if len(result) > 1:
            raise AssertionError("Multiple Artist entries for one ID in database!")

        entry = result[0] # remove the list thing, now it's just a tuple
        retval = self.__ArtistEntryToDict(entry)
        return retval


    def RemoveArtist(self, artistid):
        """
        This method removes an artist entry and all related data from all tables.

        The removed data are:

            * The complete row in the artist-table for this artist

        Args:
            artistid (int): ID of the artist

        Returns:
            ``None``

        Raises:
            TypeError: When *artistid* is not an integer or string
        """
        if type(artistid) != str and type(artistid) != int:
            raise TypeError("artistid must be a decimal number of type integer or string")

        with MusicDatabaseLock:
            sql = "DELETE FROM albums WHERE artistid = ?"
            self.Execute(sql, artistid)

        return None




    ##########################################################################
    # ALBUMS                                                                 #
    ##########################################################################


    def AddAlbum(self, artistid, name, path):
        """
        Creates a new entry for an album.

        Args:
            artistid: ID of the artist who is related to the album
            name (str): name of album
            path (str): relative path of the album

        Returns:
            ``None``

        Raises:
            TypeError: When *path* or *name* is not of type string, and *artistid* not a string or an integer
            ValueError: When *artistid* is not a decimal number
        """
        if type(path) != str:
            raise TypeError("Path must have a string-value!")
        if type(name) != str:
            raise TypeError("Name must have a string-value!")

        if type(artistid) == str:
            try:
                artistid = int(artistid)
            except ValueError:
                raise ValueError("ArtistID must be a decimal number!")

        if type(artistid) != int:
            raise TypeError("ArtistID must be of type int or str and is a decimal number!")

        values = (artistid, name, path)
        sql = "INSERT INTO albums (artistid, name, path) VALUES (?, ?, ?)"
        with MusicDatabaseLock:
            self.Execute(sql, values)
        return None


    def GetAlbumByPath(self, path):
        """
        Returns an album entry if available

        Args:
            path (str): relative path of an album

        Returns:
            An album entry or ``None`` it the album does not exits

        Raises:
            TypeError: If *path* is not of type ``str``
            AssertionError: If there is more than one album with the given path
        """
        if type(path) != str:
            raise TypeError("Path must have a string-value!")

        sql = "SELECT * FROM albums WHERE path = ?"
        with MusicDatabaseLock:
            result = self.GetFromDatabase(sql, path)

        # check result
        if not result:
            return None

        if len(result) > 1:
            raise AssertionError("Multiple Album entries for one directory in the database!")

        entry = result[0]
        retval = self.__AlbumEntryToDict(entry)
        return retval


    # Get album by its id otherwise None
    def GetAlbumById(self, albumid):
        """
        Returns an album entry if available

        Args:
            albumid: entry ID of the album in the album table

        Returns:
            An album entry or ``None`` it the album does not exits

        Raises:
            TypeError: If *albumid* is not set
            AssertionError: If there is more than one album with the given ID
        """
        if type(albumid) != str and type(albumid) != int:
            raise TypeError("AlbumID must have a decimal value!")

        sql = "SELECT * FROM albums WHERE albumid = ?"
        with MusicDatabaseLock:
            result = self.GetFromDatabase(sql, albumid)

        # check result
        if not result:
            return None

        if len(result) > 1:
            raise AssertionError("Multiple Album entries for one ID in the database!")

        entry = result[0]
        retval = self.__AlbumEntryToDict(entry)
        return retval


    def GetAllAlbums(self):
        """
        See :meth:`~lib.db.musicdb.MusicDatabase.GetAlbums` (``GetAlbums(artistid=None, withsongs=False``)
        """
        return self.GetAlbums()

    def GetAlbumsByArtistId(self, artistid):
        """
        See :meth:`~lib.db.musicdb.MusicDatabase.GetAlbums` (``GetAlbums(artistid, withsongs=False``)
        """
        return self.GetAlbums(artistid)

    # returns a list with all artists. Each list element is a dictionary with all columns of the database
    def GetAlbums(self, artistid = None, withsongs = False):
        """
        This method returns a list with all albums in the database, or all albums of an artist if *artistid* is not ``None``.
        If the *withsongs* parameter is ``True``, for each album all songs will be included.
        They are added as list into each album entry under the key ``songs``

        Example:

            The following example prints all songs of the artist with the ID ``1000``

            .. code-block:: python

                albums = musicdb.GetAlbums(artistid = 1000, withsongs = True)
                for album in albums:
                    for song in album["songs"]:
                        print(song["name"])

        Args:
            artistid: ID for an artist whose albums shall be returned. If ``None`` the albums get not filtered by *artistid*.
            withsongs (bool): also return all songs of the album.

        Returns:
            A list with all albums.

        Raises:
            TypeError: If *withsongs* is not of type ``bool``
        """
        if type(withsongs) != bool:
            raise TypeError("WithSongs must have a boolean value!")

        if artistid:
            sql   = "SELECT * FROM albums WHERE artistid = ?"
            value = int(artistid)
        else:
            sql   = "SELECT * FROM albums"
            value = None

        with MusicDatabaseLock:
            result = self.GetFromDatabase(sql, value)

            albums = []
            for entry in result:
                album = self.__AlbumEntryToDict(entry)

                if withsongs:
                    album["songs"] = self.GetSongs(album["id"])

                albums.append(album)

        return albums


    def GetAllAlbumIds(self):
        """
        Returns:
            Returns a list of all album IDs
        """
        sql = "SELECT albumid FROM albums"
        with MusicDatabaseLock:
            albumids = self.GetFromDatabase(sql)
        retval = [x[0] for x in albumids] # do not use tuples
        return retval


    def RemoveAlbum(self, albumid):
        """
        This method removes an album entry and all related data from all tables.

        The removed data are:

            * The complete row in the album-table for this album
            * All tags of this album (not the tag definition)

        Args:
            albumid (int): ID of the album

        Returns:
            ``None``

        Raises:
            TypeError: When *albumid* is not an integer or string
        """
        if type(albumid) != str and type(albumid) != int:
            raise TypeError("albumid must be a decimal number of type integer or string")

        with MusicDatabaseLock:
            sql = "DELETE FROM albums WHERE albumid = ?"
            self.Execute(sql, albumid)
            sql = "DELETE FROM albumtags WHERE albumid = ?"
            self.Execute(sql, albumid)

        return None


    #------------------------------------------------------------------------#
    # ARTWORK                                                                #
    #------------------------------------------------------------------------#


    def SetArtwork(self, albumid, artworkpath):
        """
        This method updates the *artworkpath* entry of the MusicDB Database for an album.

        Args:
            albumid: ID of the album that artwork path shall be updated
            artworkpath (str): New relative artwork path for the album

        Returns:
            ``None``

        Raises:
            TypeError: When *albumid* is not an integer or a string
            TypeError: If *artworkpath* is not of type ``str``
        """
        if type(albumid) != str and type(albumid) != int:
            raise TypeError("AlbumID must have a decimal number of type string or integer!")
        if type(artworkpath) != str:
            raise TypeError("ArtworkName must have a value of type string!")

        sql = "UPDATE albums SET artworkpath = ? WHERE albumid = ?"
        with MusicDatabaseLock:
            self.Execute(sql, (artworkpath, albumid))
        return None


    def SetArtworkColorByAlbumId(self, albumid, colorname, color):
        """
        This method is for setting a color for an album.
        Valid color names are the following and must be given as string to the *colorname* parameter.

        * ``"bgcolor"`` -  Background color
        * ``"fgcolor"`` -  Primary foreground color
        * ``"hlcolor"`` -  Secondary foreground color

        The color itself must be in HTML-Format: ``#RRGGBB``.

        Args:
            albumid: The ID of the album that color shall be set
            colorname (str): Name of the color that shall be set
            color (str): Color in HTML format

        Returns:
            ``None``

        Raises:
            TypeError: If one of the arguments is None
            ValueError: If *colorname* not ``"bgcolor"``, ``"fgcolor"`` or ``"hlcolor"``
            ValueError: If color length is not ``7`` and first character not ``"#"``
        """
        if albumid == None or color == None or colorname == None:
            raise TypeError("All parameters must have a value!")
        if not colorname in ["bgcolor", "fgcolor", "hlcolor"]:
            raise ValueError("colorname must be bgcolor, fgcolor or hlcolor");

        if color[0] != "#":
            raise ValueError("First char in color-code must be \'#\': #RRGGBB !")
        if len(color) != 7:
            raise ValueError("Color-code must have a length of 7 character: #RRGGBB !")

        data = {}
        data["color"]   = color
        data["albumid"] = albumid
        sql = "UPDATE albums SET " + colorname + "=:color WHERE albumid=:albumid"
        with MusicDatabaseLock:
            self.Execute(sql, data)
        return None



    ##########################################################################
    # SONGS                                                                  #
    ##########################################################################


    def AddSong(self, artistid, albumid, name, path):
        """
        This method creates a new database entry for a song and sets the most important values.

        If a song with the same path is already in the database, its *artistid*, *albumid* and *name* gets compared to the arguments.
        If they match, everything is fine and the method returns.
        If they differ, an AssertionError gets raised.
        Adding an existing song is a bug!
        Even if this method allows it under some conditions, this should not be exploited!

        Args:
            artistid (int): ID of the artist of this song
            albumid (int): ID of the album of this song
            name (string): Name of the song
            path (string): Path of the song file relative to the music root directory

        Returns:
            ``None``

        Raises:
            TypeError: If one of the arguments is ``None``
            ValueError: If song is already in the database **and** does not match the other parameters
        """
        if artistid == None or albumid == None or name == None or path == None:
            raise TypeError("All parameters must have a value!")

        # Check if song already exists
        with MusicDatabaseLock:
            song = self.GetSongByPath(path)
            if song:
                if song["artistid"] != artistid or song["albumid"] != albumid or song["name"] != name:
                    raise ValueError("There is a song with the same path already exists in the database but with other attributes!")

                # even if it works, adding an already existing song is a bug. Inform the programmer/user
                logging.warning("Song with path %s does already exist in database. \033[1;30m(It matches the artist ID and album ID so everything is fine right now)", path)
                return None

            sql = "INSERT INTO songs (albumid, artistid, name, path) VALUES (?, ?, ?, ?)"
            self.Execute(sql, (albumid, artistid, name, path))
        return None


    def AddFullSong(self, song):
        """
        This method creates a new entry for a song and adds all its attributes into the database.
        Creating the song is done by calling :meth:`~lib.db.musicdb.MusicDatabase.AddSong`.
        When the song was added a new song ID is generated by the database engine.
        The new entry gets read from the database.
        Then, the new ID is set as song ID to the dictionary given as argument.
        After that, the whole song dictionary gets written to the database via :meth:`~lib.db.musicdb.MusicDatabase.WriteSong`

        In case adding the song fails on half the way, the new added entry gets deleted.
        As long as nothing references the song entry, it is no problem to remove it.
        So, when this method returns ``False`` Nothing changed in the database.

        Args:
            song: A complete dictionary with all keys of a MusicDB Song entry for the database

        Returns:
            ``True`` on success, otherwise ``False`` which indicates that nothing changed in the database.
        """
        with MusicDatabaseLock:
            self.AddSong(song["artistid"], song["albumid"], song["name"], song["path"])

            try:
                entry = self.GetSongByPath(song["path"])
                song["id"] = entry["id"]
                self.WriteSong(song)
            except Exception as e:
                logging.critical("The following Exception occurred: \"%s\". Trying to delete the half added song \"%s\" from database as long as this is save.", str(e), song["path"] )
            
                # At this point, it is better to only rely on the path
                sql = "DELETE FROM songs WHERE path = ?"
                self.Execute(sql, song["path"])
                return False

        return True
        

    def GetSongById(self, songid):
        """
        Returns a song from the database that matches the *songid*

        Args:
            songid (int): ID of the song that shall be returned

        Returns:
            A MusicDB Song dictionary or ``None`` if there is no song with that ID

        Raises:
            TypeError: If *songid* is not an integer or a string
            AssertionError: If there is more than one song with the same ID
        """
        if type(songid) != str and type(songid) != int:
            raise TypeError("SongID must be a decimal number of type integer or string!")

        sql    = "SELECT * FROM songs WHERE songid = ?"
        with MusicDatabaseLock:
            result = self.GetFromDatabase(sql, (songid))

        if not result:
            return None

        if len(result) > 1:
            raise AssertionError("Multiple Song entries for one ID in the database!")

        song   = self.__SongEntryToDict(result[0])
        return song


    def GetSongByPath(self, path):
        """
        Returns a song from the database that matches the *path*

        Args:
            path (str): A song path relative to the music root directory

        Returns:
            A MusicDB Song dictionary or ``None`` if there is no song with that path

        Raises:
            TypeError: If *path* is ``None``
            AssertionError: If there is more than one song with the same path
        """
        if type(path) != str:
            raise TypeError("Path must have a value of type string!")

        sql = "SELECT * FROM songs WHERE path = ?"
        with MusicDatabaseLock:
            result = self.GetFromDatabase(sql, (path))

        # check result
        if not result:
            return None

        if len(result) > 1:
            raise AssertionError("Multiple Song entries for one path in the database! (" + path + ")")

        entry  = result[0]
        retval = self.__SongEntryToDict(entry)
        return retval


    def GetSongsByArtistId(self, artistid):
        """
        This method returns all song entries of an Artist.

        Args:
            artistid (int): ID of an artist

        Returns:
            A list of MusicDB Songs

        Raises:
            TypeError: If artistid is not a decimal number of type integer or sting
        """
        if type(artistid) != str and type(artistid) != int:
            raise TypeError("Artist ID must have be a decimal number of type integer or string!")

        sql    = "SELECT * FROM songs WHERE artistid = ?"
        with MusicDatabaseLock:
            result = self.GetFromDatabase(sql, artistid)

        songs = []
        for entry in result:
            song = {}
            song = self.__SongEntryToDict(entry)
            songs.append(song)

        return songs


    def GetSongsByAlbumId(self, albumid):
        """
        See :meth:`~lib.db.musicdb.MusicDatabase.GetSongs`
        """
        return self.GetSongs(albumid)

    def GetAllSongs(self):
        """
        See :meth:`~lib.db.musicdb.MusicDatabase.GetSongs`
        """
        return self.GetSongs()

    def GetSongs(self, albumid = None):
        """
        This method returns all songs in the database if *albumid* is ``None``, or all songs of an album if *albumid* is set.

        Args:
            albumid (int): ID of an album or ``None``

        Returns:
            A list of MusicDB Songs
        """
        if albumid:
            sql   = "SELECT * FROM songs WHERE albumid = ?"
            value = albumid
        else:
            sql   = "SELECT * FROM songs"
            value = None

        with MusicDatabaseLock:
            result = self.GetFromDatabase(sql, value)

        songs = []
        for entry in result:
            song = {}
            song = self.__SongEntryToDict(entry)
            songs.append(song)

        return songs


    def GetRandomSong(self, filterlist=None, nodisabled=True, nohated=False, minlen=None, albumid=None):
        r"""
        This method returns a random song that fulfills several constraints.

        The ``filterlist`` can be either a set of genre tag IDs or a set of genre names.
        When ``filterlist`` is ``None`` no filter gets applied.
        Otherwise only albums of the genres in the list will be considered.

        When ``albumid`` is not ``None``, then the process of getting valid albums will be skipped.
        Instead the predefined album will be used.
        In that case ``filterlist`` gets ignored.

        Getting a random song is done by the following steps, visualized in the flow chart below:

            #. Get album IDs of all albums in the database
            #. Translate *filterlist* into a list of tag IDs
            #. For each album, get its tags and compare that with the set of tag IDs from the filter. (If there is no filter list set, all album IDs are selected)
            #. Get all song IDs that are related to the filtered album IDs by calling :meth:`~lib.db.musicdb.MusicDatabase.GetSongIdsByAlbumIds`
            #. Select a random song ID and get its song entry from the database

        .. graphviz::

            digraph hierarchy {
                size="5,8"
                start           [label="Start"];
                hasalbumid      [shape=diamond, label="albumid == None"];
                getallalbums    [shape=box,     label="Get all Album IDs"]
                getalltags      [shape=box,     label="Get list of Tag IDs\nfrom filterlist"]
                hasfilterlist   [shape=diamond, label="Is there a filter list"];
                removealbums    [shape=box,     label="Remove albums without\ntags of filter"]
                getallsongs     [shape=box,     label="Get all songs of selected albums"]
                selectsong      [shape=box,     label="Select random song"]


                start           -> hasalbumid;

                hasalbumid      -> getallsongs      [label="No"];
                hasalbumid      -> getallalbums     [label="Yes"];
                getallalbums    -> getalltags

                getalltags      -> hasfilterlist
                hasfilterlist   -> removealbums     [label="Yes"];
                hasfilterlist   -> getallsongs      [label="No"];

                removealbums    -> removealbums     [label="For each album"]
                removealbums    -> getallsongs

                getallsongs     -> selectsong
            }

        Args:
            filterlist: Optional, default value is ``[]``. A list of genre names or genre tag IDs that limits the search set. The tags have *OR* relations.
            nodisabled (bool): If ``True`` no disables songs will be selected
            nohated (bool): If ``True`` no hated songs will be selected
            minlen (int): If set, no songs with less than *minlen* seconds will be selected
            albumid (int): Use album with ID ``albumid`` instead of a random album

        Returns:
            A random MusicDB Song dictionary that fulfills the constraints,
            or ``None`` when there is no song fulfilling the constraints

        Raises:
            TypeError: When *nodisabled* or *nohated* are not of type ``bool``
            TypeError: When *minlen* is not ``None`` and not of type integer
            TypeError: When *filterlist* is not a list and not ``None``
        """
        if type(nodisabled) != bool:
            raise TypeError("nodisabled must be of type bool")
            
        if type(nohated) != bool:
            raise TypeError("nohated must be of type bool")

        if minlen != None and type(minlen) != int:
            raise TypeError("minlen must be None or of type integer")

        if filterlist == None:
            filterlist = []
        if type(filterlist) != list:
            raise TypeError("filterlist must be of type list")

        if albumid and filterlist:
            logging.warning("Ignoring tag filter because there was an Album ID given. \033[1;30m(This may be a symptom of a bug!)")


        # Create a list of tagids that limits the set of albums
        if albumid == None:
            with MusicDatabaseLock:
                tagids = []
                if len(filterlist) > 0:
                    for filterentry in filterlist:
                        if type(filterentry) == str:
                            tag   = self.GetTagByName(filterentry, self.TAG_CLASS_GENRE)
                            tagid = tag["id"]
                        else:
                            tagid = filterentry

                        tagids.append(tagid)

                # create a set from the list to compare it with a set of albumtags
                tagids = set(tagids)

                # Get IDs of all albums existing in the database
                sql      = "SELECT albumid FROM albums"
                retval   = self.GetFromDatabase(sql, None)
                albumids = [entry[self.ALBUM_ID] for entry in retval]

                # Only select albums that have a tag listed in the tagids list
                selectedalbumids = []
                if len(tagids) > 0:
                    for albumid in albumids:
                        # Get tags of the album
                        albumtags = self.GetTargetTags("album", albumid, self.TAG_CLASS_GENRE)
                        if not albumtags:
                            continue

                        # Check if one tag matches the filter
                        albumtagids = { albumtag["id"] for albumtag in albumtags }
                        if not tagids & albumtagids:
                            continue

                        selectedalbumids.append(albumid)
                else:
                    selectedalbumids = albumids

        else:
            # use the predefined album ID
            selectedalbumids = [albumid]

        # Get all Songs that may be candidate
        with MusicDatabaseLock:
            songids = self.GetSongIdsByAlbumIds(selectedalbumids, nodisabled, nohated, minlen)

        if len(songids) == 0:
            return None

        # Choose a random one
        songid   = songids[random.randrange(0, len(songids))]
        song     = self.GetSongById(songid)
        return song


    def GetSongIdsByAlbumIds(self, albumids, nodisabled=True, nohated=False, minlen=None):
        """
        This method returns a list of songs that belong to the albums addressed by their IDs in the *albumids* list.
        The songs of the returned IDs also fulfill the constraints given by the other parameters.

        Args:
            albumids: A list of album IDs that songs are considered to get
            nodisabled (bool): If ``True`` no disables songs will be selected
            nohated (bool): If ``True`` no hated songs will be selected
            minlen (int): If set, no songs with less than *minlen* seconds will be selected

        Returns:
            A list of song IDs

        Raises:
            TypeError: When *nodisabled* or *nohated* are not of type ``bool``
            TypeError: When *minlen* is not ``None`` and not of type integer
            ValueError: When minlen is less than ``0``
            TypeError: When *albumuids* is ``None``
        """
        if type(nodisabled) != bool:
            raise TypeError("nodisabled must be of type bool")
            
        if type(nohated) != bool:
            raise TypeError("nohated must be of type bool")

        if minlen != None and type(minlen) != int:
            raise TypeError("minlen must be None or of type integer")

        if albumids == None:
            raise TypeError("albumids must have a value!")
        if not type(albumids) == list:
            albumids = [albumids]

        sql = "SELECT songid FROM songs WHERE albumid = ?"
        if nodisabled:
            sql += " AND disabled != 1"
        if nohated:
            sql += " AND favorite >= 0"
        if minlen:
            # make sure the argument does not mess up te query-string
            tmp = int(minlen)
            if minlen < 0:
                raise ValueError("minlen must be >= 0")
            sql += " AND playtime >= " + str(minlen)

        with MusicDatabaseLock:
            songids = []
            for albumid in albumids:
                # returns a list of tuples with one element: [(id1,), .., (idn,)]
                result = self.GetFromDatabase(sql, albumid)
                if not result:
                    continue

                for entry in result:
                    songids.append(entry[0])

        return songids



    def GetLyrics(self, songid):
        """
        This method returns the lyrics of a song.

        Args:
            songid (int): ID of the song for that the lyrics shall be returned

        Returns:
            The lyrics of a song or ``None`` if there are no lyrics for the song.

        Raises:
            TypeError: When *sonid* is not an integer or string
            AssertionError: If there were multiple lyrics entries for the given song ID
        """
        if type(songid) != str and type(songid) != int:
            raise TypeError("songid must be a decimal number of type integer or string")

        sql    = "SELECT lyrics FROM lyrics WHERE songid = ?"
        with MusicDatabaseLock:
            result = self.GetFromDatabase(sql, (songid))

        # check result
        if not result:
            return None

        if len(result) > 1:
            raise AssertionError("Multiple lyrics entries for one songid in the database! (" + songid + ")")

        lyrics = result[0]  # list -> tuple
        lyrics = lyrics[0]  # tuple-> string
        return lyrics



    def SetLyrics(self, songid, lyrics, lyricsstate=SONG_LYRICSSTATE_FROMUSER):
        """
        This method can be used to store or to update lyrics of a song.
        It stores the lyrics in the lyrics table and updates the lyrics state in the songs table for a given song.

        If there are no lyrics for the song, or lyrics shall be removed, the lyrics argument must be ``None`` or ``""``.
        In this case the lyrics state gets forced to ``SONG_LYRICSSTATE_EMPTY``.
        Only excepetion is, when the *lyricsstate* is ``SONG_LYRICSSTATE_NONE`` which indicates that the song does not have lyrics at all.
        For example, instrumental songs or intros.

        Args:
            songid (int): ID of the song the lyrics belong to
            lyrics (str): The lyrics to store
            lyricsstate (int): The new state of the lyrics. Default is "From User" (``SONG_LYRICSSTATE_FROMUSER``)

        Returns:
            Always ``True``

        Raises:
            TypeError: When *sonid* is not an integer or string
            TypeError: If lyrics state is not a number.
            ValueError: If lyrics state is not in ``SONG_LYRICSSTATE_*``
        """
        if type(songid) != str and type(songid) != int:
            raise TypeError("songid must be a decimal number of type integer or string")

        try:
            lyricsstate = int(lyricsstate)
        except:
            raise TypeError("lyricsstate is not an integer")

        if lyricsstate not in [SONG_LYRICSSTATE_EMPTY, SONG_LYRICSSTATE_FROMFILE, SONG_LYRICSSTATE_FROMNET, SONG_LYRICSSTATE_FROMUSER, SONG_LYRICSSTATE_NONE]:
            raise ValueError("lyricsstate has an invalid value: "+str(lyricsstate)+" See documentation for valid values!")

        # make sure the states are clear
        if lyrics == "":
            lyrics = None
        # If it is not an instrumental song, the entry is just empty
        if lyrics == None and lyricsstate != SONG_LYRICSSTATE_NONE:
            lyricsstate = SONG_LYRICSSTATE_EMPTY

        if lyricsstate in [SONG_LYRICSSTATE_EMPTY, SONG_LYRICSSTATE_NONE]:
            lyrics = None

        # try to get old lyrics to see if there exists an entry already
        sql    = "SELECT lyrics FROM lyrics WHERE songid = ?"
        with MusicDatabaseLock:
            result = self.GetFromDatabase(sql, (songid))
            if len(result) > 1:
                raise AssertionError("Multiple lyrics entries for one songid in the database! (" + songid + ")")

            if lyrics == None:
                # delete existing lyrics entry
                sql = "DELETE FROM lyrics WHERE songid = ?"
                self.Execute(sql, songid)
            elif result:
                # update existing entry
                sql = "UPDATE lyrics SET lyrics = ? WHERE songid = ?"
                self.Execute(sql, (lyrics, songid))
            else:
                # create new entry
                sql = "INSERT INTO lyrics (songid, lyrics) VALUES (?, ?)"
                self.Execute(sql, (songid, lyrics))

            # Set Lyricsstate
            song = self.GetSongById(songid)
            song["lyricsstate"] = lyricsstate
            self.WriteSong(song)
        return True



    def UpdateSongStatistic(self, songid, stat, value):
        """
        This method updates the song statistics.

        Statistics are: ``"likes"``, ``"dislikes"``, ``"qskips"``, ``"qadds"``, ``"qrndadds"``, ``"qremoves"``, ``"favorite"``, ``"disabled"``

        Values are:
            
            * ``"inc"``, ``"love"``, ``"yes"``: Increment value
            * ``"dec"``, ``"hate"``: Decrement value
            * ``"reset"``, ``"none"``, ``"no"``: Set value to ``0``

        ``favorite`` can have three states:

            * ``-1``: Hated song
            * ``0``: Normal song
            * ``1``: Loved song

        Args:
            songid (int): ID of the song
            stat (str): Name of the statistics to update
            value (str): How to update

        Returns:
            ``None``

        Raises:
            TypeError: When *songid* is not an integer or string
            ValueError: if stats or value have an invalid value
        """
        if type(songid) != str and type(songid) != int:
            raise TypeError("songid must be a decimal number of type integer or string")

        # Check if value and stat are valid
        if stat not in ["likes", "dislikes", "qskips", "qadds", "qrndadds", "qremoves", "favorite", "disable"]:
            raise ValueError("stat has an invalid value \"%s\"", str(stat))
        if value not in ["inc", "dec", "reset", "love", "hate", "none", "yes", "no"]:
            raise ValueError("value has an invalid value \"%s\"", str(value))

        # Get song entry
        with MusicDatabaseLock:
            song = self.GetSongById(songid)

            # generate modifier
            if value in ["inc", "love", "yes"]:
                modifier = int(+1)
            elif value in ["dec", "hate"]:
                modifier = int(-1)
            elif value in ["reset", "none", "no"]:
                modifier = int(0)

            # apply modifier
            if stat == "favorite":
                song["favorite"] = modifier
            elif stat == "disable":
                song["disabled"] = modifier
            elif modifier == 0:
                song[stat]       = 0
            else:
                song[stat]      += modifier

            # Write Song
            self.WriteSong(song)
        return None


    def RemoveSong(self, songid):
        """
        This method removes a song entry and all related data from all tables.

        The removed data are:

            * The complete row in the songs-table for this song
            * The lyrics of this song
            * All tags of this song (not the tag definition)
            * Decrementation of the albums *numofsongs* value. (not the *numofcds* entry!)

        Args:
            songid (int): ID of the song

        Returns:
            ``None``

        Raises:
            TypeError: When *songid* is not an integer or string
        """
        if type(songid) != str and type(songid) != int:
            raise TypeError("songid must be a decimal number of type integer or string")

        with MusicDatabaseLock:
            sql = "DELETE FROM songs WHERE songid = ?"
            self.Execute(sql, songid)
            sql = "DELETE FROM lyrics WHERE songid = ?"
            self.Execute(sql, songid)
            sql = "DELETE FROM songtags WHERE songid = ?"
            self.Execute(sql, songid)

        return None

    ####################################
    # TAG HANDLING
    ####################################

    def GetAllTags(self, tagclass=None):
        """
        This method returns a list of tags from the tags table.
        If *tagclass* is set, only tags of the specified class gets returned.
        Otherwise all tags.

        Args:
            tagclass (int): Optional, to only get tags of the given class

        Returns:
            A list of tags

        Raises:
            ValueError: If *tagclass* is set (not ``None``) with an invalid value

        """
        with MusicDatabaseLock:
            if tagclass == None:
                sql     = "SELECT * FROM tags"
                taglist = self.GetFromDatabase(sql)
            elif tagclass in [self.TAG_CLASS_GENRE, self.TAG_CLASS_SUBGENRE, self.TAG_CLASS_MOOD]:
                sql     = "SELECT * FROM tags WHERE class = ?"
                taglist = self.GetFromDatabase(sql, tagclass)
            else:
                raise ValueError("tagclass must be None or a valid Integer.")

        retval = []
        for tagentry in taglist:
            tag = self.__TagEntryToDict(tagentry)
            retval.append(tag)

        return retval



    def CreateTag(self, tagname, tagclass, parentid=None):
        """
        This method creates a new tag in the tags-table.

        If the tag already exists in its class, it will not be created.

        Args:
            tagname (str): Name of the new tag. This is also the name that gets displayed in the GUI.
            tagclass (int): Defines the class of the tag.
            parentid (int): Optional parent relation to other tags - Mandatory for subgenre

        Returns:
            ``None``

        Raises:
            TypeError: if *tagname* is not a string or *parentid* does not have the value it should have regarding the specification
            ValueError: When *tagclass* has an invalid value
        """
        if type(tagname) != str:
            raise TypeError("Name must be of type string!")
        if tagclass not in [self.TAG_CLASS_GENRE, self.TAG_CLASS_SUBGENRE, self.TAG_CLASS_MOOD]:
            raise ValueError("Invalid tag class")

        if tagclass == self.TAG_CLASS_SUBGENRE and parentid == None:
            raise TypeError("When creating a subgenre, the parent ID must be given!")
        elif tagclass != self.TAG_CLASS_SUBGENRE and parentid != None:
            raise TypeError("When not creating a subgenre, the parent ID must be  None!")

        with MusicDatabaseLock:
            if self.GetTagByName(tagname, tagclass):
                logging.warning("Tag \"%s\" (class=%i) already exists!", tagname, tagclass)
                return None

            sql = "INSERT INTO tags (name, class, parentid) VALUES (?,?,?)"
            self.Execute(sql, (tagname, tagclass, parentid))
        return None



    def DeleteTag(self, tagname, tagclass):
        """
        Deletes an entry from the tags-table with the name *tagname* and that belongs to *tagclass*.

        .. warning::

            This method does NOT delete child tags or the relation between the tag and songs or albums.
            You should only delete new created tags that are not used!

        Args:
            tagname (str):  Name of the tag that shall be deleted.
            tagclass (int): Class of the name the tag belongs to.

        Returns:
            ``None``

        Raises:
            TypeError: If *tagname* is not of type ``str`` 
            ValueError: If *tagclass* is not a valid class ID.
        """
        if type(tagname) != str:
            raise TypeError("Name must be of type string!")
        if tagclass not in [self.TAG_CLASS_GENRE, self.TAG_CLASS_SUBGENRE, self.TAG_CLASS_MOOD]:
            raise ValueError("Invalid tag class")

        logging.debug("Deleting tag \"%s\" of class %i from tags-table!", tagname, tagclass)

        sql = "DELETE FROM tags WHERE name = ? AND class = ?"
        with MusicDatabaseLock:
            self.Execute(sql, (tagname, tagclass))
        return None



    def ModifyTag(self, tagname, tagclass, columnname, newvalue):
        """
        This method allows to modify most of the attributes of a tag.
        The *tagname* and *tagclass* addresses the tag, *columnname* the attribute.
        *newvalue* is the new attribute set for the tag.

        In case the icon gets modified, take care that the icon type is up to date. (update order does not matter).

        Args:
            tagname (str): Name of the tag that shall be modified
            tagclass (int): Class of the tag
            columnname (str): The name of the attribute that shall be modified
            newvalue: The new value. Read the introduction at the top of the document to see what values are possible for a specific attribute

        Returns:
            ``None``

        Raises:
            TypeError: if *tagname* is not a string or *parentid* does not have the value it should have regarding the specification
            ValueError: When *tagclass* has an invalid value
            ValueError: If columnname is not "name", "parentid", "icontype", "icon", "color", "posx", "posy"
            ValueError: If columnname is "color" and *newvalue* is not a valid #RRGGBB-Formated string
            ValueError: If columnname is "icontype" and *newvalue* is not valid
        """
        if type(tagname) != str:
            raise TypeError("Name must be of type string!")
        if tagclass not in [self.TAG_CLASS_GENRE, self.TAG_CLASS_SUBGENRE, self.TAG_CLASS_MOOD]:
            raise ValueError("Invalid tag class")

        if columnname not in ["name", "parentid", "icontype", "icon", "color", "posx", "posy"]:
            raise ValueError("Invalid column name \"%s\"!", columnname)

        if columnname == "color":
            if newvalue[0] != "#":
                raise ValueError("First char in color-code must be \'#\': #RRGGBB !")
            if len(newvalue) != 7:
                raise ValueError("Color-code must have a length of 7 character: #RRGGBB !")

        if columnname == "icontype":
            if newvalue not in [self.TAG_ICONTYPE_UNICODE, self.TAG_ICONTYPE_HTML]:
                raise ValueError("Invalid icontype")

        data = {}
        data["value"] = newvalue
        data["name"]  = tagname
        data["class"] = tagclass
        sql = "UPDATE tags SET " + columnname + "=:value WHERE name=:name AND class=:class"
        with MusicDatabaseLock:
            self.Execute(sql, data)
        return None



    def SetTargetTag(self, target, targetid, tagid, approval=1, confidence=None):
        """
        This method sets a tag for a target. 
        A target can be a song (``target = "song"``) or an album (``target = "album"``).

        The defaults for this method assume that the tag got set by a user.

            * If *approval* equals ``1`` or ``2``, the confidence gets set to ``1.0``.
            * If *approval* equals ``0`` a *confidence* must be given, otherwise an ``AssertionError`` gets thrown.

        If the tag was already set, the *approval* and *confidence* values get updated. 
        But only if the new approval level is greater or equal to the already set one.

        Args:
            target (str):   Target that shall be tagged (``"song"`` for a song, ``"album"`` for an album)
            songid (int):   ID of the target that shall be tagged. (a song ID or an album ID)
            tagid (int):    ID of the tag that shall be associated with the target
            approval (int): Approval of the association. Default is ``1`` - "Set by User"
            confidence (float): Confidence of the association in case *approval* is ``0`` - "Set by AI"

        Return:
            ``None``

        Raises:
            TypeError: If *target* not in *{"song", "album"}*
            TypeError: If ``approval == 0 and confidence == None``
            ValueError: If *approval* not in *{0,1,2}*
            ValueError: If ``songid == None or tagid == None``
            AssertionError: If there already exists more than one entry
        """
        if targetid == None or tagid == None:
            raise TypeError("SongID and TagID must have a value!")

        if approval == 1 or approval == 2:
            confidence = 1.0
        elif approval == 0:
            if confidence == None:
                raise TypeError("If approval is 0 (tagged by AI), the confidence must be given!")
        else:
            raise ValueError("approval must be element of {0,1,2}!")

        # select table
        if target == "song":
            tablename = "songtags"
            idname    = "songid"
        elif target == "album":
            tablename = "albumtags"
            idname    = "albumid"
        else:
            raise ValueError("target must be \"song\" or \"album\"!")

        # check if already tagged
        sql = "SELECT * FROM " + tablename + " WHERE " + idname + " = ? AND tagid = ?"
        with MusicDatabaseLock:
            result = self.GetFromDatabase(sql, (targetid, tagid))
            if len(result) > 1:
                raise AssertionError("More that one tag entry found!")

            # only update an existing entry
            if len(result) == 1:
                tag  = result[0]
                data = {}

                if tag[self.TAGMAP_APPROVAL] > approval:
                    # This can now happen very often due to the DeriveAlbumTags method.
                    # This is no longer a symptom of misbehavior.
                    #logging.warning("The tag was already set and has a higher approval level (%d) than the update (%d)! \033[1;30m(update gets rejected for %s %d)", tag[self.TAGMAP_APPROVAL], approval, target, targetid)
                    return None

                data["entryid"]    = tag[self.TAGMAP_ENTRYID]
                data["approval"]   = approval
                data["confidence"] = confidence
                sql = "UPDATE " + tablename + " SET confidence=:confidence, approval=:approval WHERE entryid=:entryid"
                self.Execute(sql, data)
            # create new entry
            else:
                sql = "INSERT INTO " + tablename + " (" + idname + ", tagid, confidence, approval) VALUES (?, ?, ?, ?)"
                self.Execute(sql, (targetid, tagid, confidence, approval))

        return None



    def RemoveTargetTag(self, target, targetid, tagid):
        """
        Removes an association between a target and a tag in the tag map - Or short: Removes a tag from a song or an album.

        Args:
            target (str):   Target that shall be tagged (``"song"`` for a song, ``"album"`` for an album)
            targetid (int): ID of the target that shall be tagged. (a song ID or an album ID)
            tagid (int):    ID of the tag that shall be associated with the target

        Return:
            ``None``

        Raises:
            ValueError: If *target* not in *{"song", "album"}*
            TypeError: If ``songid == None or tagid == None``
        """
        if targetid == None or tagid == None:
            raise TypeError("SongID and TagID must have a value!")

        # select table
        if target == "song":
            tablename = "songtags"
            idname    = "songid"
        elif target == "album":
            tablename = "albumtags"
            idname    = "albumid"
        else:
            raise ValueError("target must be \"song\" or \"album\"!")

        sql = "DELETE FROM " + tablename + " WHERE " + idname + " = ? AND tagid = ?"
        with MusicDatabaseLock:
            self.Execute(sql, (targetid, tagid))
        return None


    
    def GetTargetTags(self, target, targetid, tagclass=None):
        """
        Returns a list of all tags of a target.
        A target can be a song (``target = "song"``) or an album (``target = "album"``).
        This list contains all classes of tags if *tagclass* is ``None``, otherwise only of type *tagclass*.

        The returned list is the target-tag-mapping augmented with the tag-entry.
        So, each element in the list is a merged dictionary of the table row of the mapping and the tag itself.
        The ``id`` entry in the dictionary is the ID of the Tag and identical to the entry ``tagid``.
        The ID of the ID of the entry in the mapping-table is ``entryid``.
        
        Args:
            target (str):   Target that shall be tagged (``"song"`` for a song, ``"album"`` for an album)
            targetid (int): ID of the target that tags shall be returned (song ID or album ID)
            tagclass (int): If not ``None`` only tags of a specific class will be returned

        Returns:
            A list of tags or ``None`` if there are no tags

        Raises:
            TypeError: If *songid* is ``None``
            ValueError: If *tagclass* is set to an invalid value (``None`` is valid)
            ValueError: If *target* not in *{"song", "album"}*

        Example:

            .. code-block:: python
                
                tags = database.GetTargetTags("song", songid)
                for tag in tags:
                    print("Tagname: %s",  tag["name"], end="; ")
                    print("Approval: %i", tag["approval"])
                    print("Approval: %f", tag["confidence"])

        """

        if targetid == None:
            raise TypeError("Target ID must have a value!")
        if tagclass not in [None, self.TAG_CLASS_GENRE, self.TAG_CLASS_SUBGENRE, self.TAG_CLASS_MOOD]:
            raise ValueError("Invalid tag class")

        # select table
        if target == "song":
            tablename = "songtags"
            idname    = "songid"
        elif target == "album":
            tablename = "albumtags"
            idname    = "albumid"
        else:
            raise ValueError("target must be \"song\" or \"album\"!")

        with MusicDatabaseLock:
            # get all tagids assigned to the target
            sql    = "SELECT * FROM " + tablename + " WHERE " + idname + " = ?"
            result = self.GetFromDatabase(sql, targetid)

            # returns a list of tuples with one element: [(id1,), .., (idn,)]
            if not result:
                return None # no tags set

            # for each tagid
            retval = []
            for entry in result:
                # Translate mapping 
                mapping = self.__TagMapEntryToDict(entry, idname)

                # Get mapped tag
                sql      = "SELECT * FROM tags WHERE tagid = ?"
                tagentry = self.GetFromDatabase(sql, mapping["tagid"])
                if len(tagentry) == 0:
                    logging.warning("\033[1;33mUnknown tag ID " + str(mapping["tagid"]) + " for " + target + " ID " + str(songid))
                    continue

                tag = self.__TagEntryToDict(tagentry[0])

                # Check if it shall be filtered
                if tagclass and tag["class"] != tagclass:
                    continue

                # Add tag-information to mapping
                mapping.update(tag)
                retval.append(mapping)

        return retval



    def SplitTagsByClass(self, tags):
        """
        Splits a list of tags into several lists, each of a specific class.

        If the *tags* parameter is ``None``, this method returns ``[]`` for each class.

        Args:
            tags (list): A list of tags

        Returns:
            three lists, each of a specific class: genres, subgenres, moods

        Raises:
            ValueError: If a tag contains an invalid class ID

        Exampe:

            .. code-block:: python

                tags = database.GetTagretTags("song", songid)
                genres, subgenres, moods = database.SplitTagsByClass(tags)
        """
        genres    = []
        subgenres = []
        moods     = []

        if tags == None:
            return genres, subgenres, moods

        for tag in tags:
            if tag["class"] == self.TAG_CLASS_GENRE:
                genres.append(tag)
            elif tag["class"] == self.TAG_CLASS_SUBGENRE:
                subgenres.append(tag)
            elif tag["class"] == self.TAG_CLASS_MOOD:
                moods.append(tag)
            else:
                raise ValueError("Invalid class ID!")

        return genres, subgenres, moods



    def GetTagByName(self, tagname, tagclass=TAG_CLASS_GENRE):
        """
        This method returns a tag entry addressed by the tagname and tagclass.

        Args:
            tagname (str): Name of the tag that shall be returned
            tagclass (int): ID of the tagclass - Default is the main genre class.

        Returns:
            The row of the specified tag, or ``None`` if no tag was found

        Raises:
            ValueError: If no name or valid tagclass was given
            TypeError: If *tagname* is not a string
            AssertionError: If more than one tag was found - This should never happen!
        """

        if tagname == None:
            raise TypeError("TagName must be given!")
        if type(tagname) != str:
            raise TypeError("Name must be of type string!")
        if tagclass not in [self.TAG_CLASS_GENRE, self.TAG_CLASS_SUBGENRE, self.TAG_CLASS_MOOD]:
            raise ValueError("Invalid tag class")

        sql = "SELECT * FROM tags WHERE name = ? AND class = ?"
        with MusicDatabaseLock:
            result = self.GetFromDatabase(sql, (tagname, tagclass))

        # check result
        if not result:
            return None
        
        if len(result) > 1:
            raise AssertionError("Multiple Tag entries for one Tag-Name in the database!")

        entry  = result[0]
        retval = self.__TagEntryToDict(entry)
        return retval


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

