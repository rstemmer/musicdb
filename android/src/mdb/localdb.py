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
        artworkpath TEXT,
        bgcolor     TEXT,
        fgcolor     TEXT,
        hlcolor     TEXT
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
        likes       INTEGER,
        dislikes    INTEGER,
        favorite    INTEGER,
        syncstate   INTEGER
    )
    """
    # SyncState: 0: Up to date; 1: Must be downloaded; 2: Must be deleted

class LocalDatabase(Database):
    """

    Args:
        path (str): absolute path to the database file.

    Raises:
        TypeError: When *path* is not a string
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
    SONG_FAVORITE   = 12
    SONG_SYNCSTATE  = 13
    SYNCSTATE_CURRENT = 0
    SYNCSTATE_NEW     = 1
    SYNCSTATE_OLD     = 2

    def __init__(self, path):
        # check path
        if type(path) != str:
            raise TypeError("A valid database path is necessary")

        Database.__init__(self, path)

        # Create scheme if not exists
        self.Execute(artists_scheme)
        self.Execute(albums_scheme)
        self.Execute(songs_scheme)



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
        song["id"]       = entry[self.SONG_ID]
        song["albumid"]  = entry[self.SONG_ALBUMID]
        song["artistid"] = entry[self.SONG_ARTISTID]
        song["name"]     = entry[self.SONG_NAME]
        song["path"]     = entry[self.SONG_PATH]
        song["number"]   = entry[self.SONG_NUMBER]
        song["cd"]       = entry[self.SONG_CD]
        song["disabled"] = entry[self.SONG_DISABLED]
        song["playtime"] = entry[self.SONG_PLAYTIME]
        song["bitrate"]  = entry[self.SONG_BITRATE]
        song["likes"]    = entry[self.SONG_LIKES]
        song["dislikes"] = entry[self.SONG_DISLIKES]
        song["favorite"] = entry[self.SONG_FAVORITE]
        song["syncstate"]= entry[self.SONG_SYNCSTATE]
        return song



    def DeleteDatabase(self):
        """
        This method removes the following tables from the database:
        songs, albums, artists

        Returns:
            *Nothing*
        """
        self.Execute("DROP TABLE IF EXISTS songs")
        self.Execute("DROP TABLE IF EXISTS albums")
        self.Execute("DROP TABLE IF EXISTS artists")



##############################################################################
# SONGS                                                                      #
##############################################################################



    def SetAllSongsAsOutdated(self):
        """
        Sets the *syncstate* value for all songs to outdated.

        Returns:
            ``None``
        """
        # set all sync-flags to outdated
        sql = "UPDATE songs SET syncstate = 2"
        self.Execute(sql)
        return None



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
        result = self.GetFromDatabase(sql, (songid))

        if not result:
            return None

        if len(result) > 1:
            raise AssertionError("Multiple Song entries for one ID in the database!")

        song   = self.__SongEntryToDict(result[0])
        return song



    def CreateOrUpdateSongEntry(self, mdbsong):
        """
        Updates a song's database entry with the row from the MusicDB Server.
        This includes setting the sync-state to ``0`` (Up to date).
        The path column will not be updated, because path on the local file system will be different than the one on the server.

        If the song does not exist, a new entry will be created with sync-state ``1`` (new entry, download file).
        In this case, the *path* value corresponds to the path on the server, not on the client.
        This information can be used to download the song file.

        The song gets identified by its ID.
        Changed file endings will not be detected!

        Example:
            .. code-block:: python

                # Get a list of all songs on the server
                mdbsongs = # [..]

                # Update each entry
                self.SetAllSongsAsOutdated()
                for mdbsong in mdbsongs:
                    self.CreateOrUpdateSongEntry(mdbsong)

        Args:
            mdbsong (dict): A MusicDB Song Entry that represents the related database entry on server side.

        Returns:
            ``None``

        Raises:
            TypeError: When *mdbsong* is not of type ``dict``
        """
        
        if type(mdbsong) != dict:
            raise TypeError("mdbsong must be a dictionary representing a MusicDB Song Row!")

        entry = self.GetSongById(mdbsong["id"])
        if not entry:
            # When the entry does not exist,
            # create new entry and set sync-flag to 1
            sql = """
            INSERT INTO songs (
                songid, albumid, artistid,
                name, path,
                number, cd,
                disabled,
                playtime, bitrate,
                likes, dislikes, favorite,
                syncstate
                )
            VALUES (
                :id, :albumid, :artistid,
                :name, :path,
                :number, :cd,
                :disabled,
                :playtime, :bitrate,
                :likes, :dislikes, :favorite,
                1
                )
            """
        else:
            # When the entry does exist,
            # set sync-flag to 0 and update values
            sql = """
            UPDATE songs SET 
                disabled = :disabled, 
                likes    = :likes, 
                dislikes = :dislikes,
                favorite = :favorite,
                syncstate= 0
            WHERE 
                songid = :id
            """

        self.Execute(sql, mdbsong)
        return None



    def GetAllOldSongs(self):
        """
        Returns a list of song from the database that are marked as outdated.
        These entries can be used to delete the related files.

        Returns:
            A list of song dictionaries or ``[]`` if there are no song outdated songs
        """

        sql    = "SELECT * FROM songs WHERE syncstate = 2"
        result = self.GetFromDatabase(sql)

        if not result:
            return []

        songs = []
        for entry in result:
            song = self.__SongEntryToDict(entry)
            songs.append(song)

        return songs



    def GetAllNewSongs(self):
        """
        Returns a list of song from the database that are marked as new.
        These entries can be used to download the related files.

        Returns:
            A list of song dictionaries or ``[]`` if there are no song new song entries
        """

        sql    = "SELECT * FROM songs WHERE syncstate = 1"
        result = self.GetFromDatabase(sql)

        if not result:
            return []

        songs = []
        for entry in result:
            song = self.__SongEntryToDict(entry)
            songs.append(song)

        return songs



    def DeleteAllOldSongs(self):
        """
        This method deletes all outdated song entries.

        Returns:
            ``None``
        """
        # Delete entries
        sql = "DELETE FROM songs WHERE syncstate = 2"
        self.Execute(sql)
        return None



    def SetSongAsDownloaded(self, songid, path):
        """
        This method sets a songs path and marks it as updated

        Args:
            songid (int): ID of the song to update
            path (str): Path to the song file on the local file system

        Returns:
            ``None``

        Raises:
            TypeError: When *songid* is not an integer, or *path* is not a string
        """
        if type(songid) != int:
            raise TypeError("songid must be an integer!")
        if type(path) != str:
            raise TypeError("path must be a string, not %s!"%(type(path)))

        sql = "UPDATE songs SET path = ?, syncstate = 0 WHERE songid = ?"
        self.Execute(sql, (path, songid))
        return None




##############################################################################
# ALBUMS                                                                     #
##############################################################################



    def GetAllAlbumIDs(self):
        """
        Returns:
            Returns a list of all album IDs
        """

        sql    = "SELECT albumid FROM albums"
        result = self.GetFromDatabase(sql)

        if not result:
            return []

        return result



    def GetAlbumById(self, albumid):
        if type(albumid) != str and type(albumid) != int:
            raise TypeError("Album ID must be a decimal number of type integer or string!")

        sql    = "SELECT * FROM albums WHERE albumid = ?"
        result = self.GetFromDatabase(sql, albumid)

        if not result:
            return None

        if len(result) > 1:
            raise AssertionError("Multiple Album entries for one ID in the database!")

        album = self.__AlbumEntryToDict(result[0])
        return album



    def CreateAlbumEntry(self, mdbalbum):
        """
        Creates a new album entry.

        Args:
            mdbalbum (dict): A MusicDB Album Entry that represents the related database entry on server side.

        Returns:
            ``True`` on success, ``False`` when there is already an entry for that album id

        Raises:
            TypeError: When *mdbalbum* is not of type ``dict``
        """
        
        if type(mdbalbum) != dict:
            raise TypeError("mdbalbum must be a dictionary representing a MusicDB Album Row!")

        entry = self.GetAlbumById(mdbalbum["id"])
        if entry:
            # Entry already exists!
            return False

        sql = """
        INSERT INTO albums (
            albumid, artistid,
            name, path,
            numofsongs, numofcds,
            origin, release,
            artworkpath,
            bgcolor, fgcolor, hlcolor
            )
        VALUES (
            :id, :artistid,
            :name, :path,
            :numofsongs, :numofcds,
            :origin, :release,
            :artworkpath,
            :bgcolor, :fgcolor, :hlcolor
            )
        """
        self.Execute(sql, mdbalbum)
        return True



##############################################################################
# ARTISTS                                                                    #
##############################################################################



    def GetAllArtistIDs(self):
        """
        Returns:
            Returns a list of all artist IDs
        """

        sql    = "SELECT artistid FROM artists"
        result = self.GetFromDatabase(sql)

        if not result:
            return []

        return result



    def GetArtistById(self, artistid):
        if type(artistid) != str and type(artistid) != int:
            raise TypeError("SongID must be a decimal number of type integer or string!")

        sql    = "SELECT * FROM artists WHERE artistid = ?"
        result = self.GetFromDatabase(sql, (artistid))

        if not result:
            return None

        if len(result) > 1:
            raise AssertionError("Multiple Artist entries for one ID in the database!")

        artist   = self.__ArtistEntryToDict(result[0])
        return artist



    def CreateArtistEntry(self, mdbartist):
        """
        Creates a new artist entry.

        Args:
            mdbartist (dict): A MusicDB Song Entry that represents the related database entry on server side.

        Returns:
            ``True`` on success, ``False`` when there is already an entry for that artist id

        Raises:
            TypeError: When *mdbartist* is not of type ``dict``
        """
        
        if type(mdbartist) != dict:
            raise TypeError("mdbartist must be a dictionary representing a MusicDB Artist Row!")

        entry = self.GetArtistById(mdbartist["id"])
        if entry:
            # Entry already exists!
            return False

        sql = "INSERT INTO artists ( artistid, name, path ) VALUES ( :id, :name, :path )"
        self.Execute(sql, mdbartist)
        return True



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

