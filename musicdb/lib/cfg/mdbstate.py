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
This module takes care that the state of MusicDB will persist over several sessions.
This is *not done automatically* by the :class:`~MDBState` class.
Each read or write process to the files that hold the state will be triggered by the classes who manage the related information.

The state is stored in several files in a sub-directory ``state`` inside the MusicDB data directory.
More details can be found in :doc:`/basics/data`.

All files inside the state directory are managed by the :class:`~MDBState` class.
The content of those files should not be changed by any user because its content gets not validated.
"""

from musicdb.lib.cfg.config import Config
from musicdb.lib.cfg.csv    import CSVFile
from musicdb.lib.db.musicdb import MusicDatabase
import time
import logging
import os

class META:
    pass
class QUEUE:
    pass

class MDBState(Config, object):
    """
    This class holds the MusicDB internal state.

    The following table shows which method is responsible for which file in the MusicDB State Directory.

        +------------------------+-------------------------+-------------------------+
        | File Name              | Read Method             | Write Method            |
        +========================+=========================+=========================+
        | songqueue.csv          | :meth:`~LoadSongQueue`  | :meth:`~SaveSongQueue`  |
        +------------------------+-------------------------+-------------------------+
        | videoqueue.csv         | :meth:`~LoadVideoQueue` | :meth:`~SaveVideoQueue` |
        +------------------------+-------------------------+-------------------------+
        | artistblacklist.csv    | :meth:`~LoadBlacklists` | :meth:`~SaveBlacklists` |
        +------------------------+-------------------------+-------------------------+
        | albumblacklist.csv     | :meth:`~LoadBlacklists` | :meth:`~SaveBlacklists` |
        +------------------------+-------------------------+-------------------------+
        | songblacklist.csv      | :meth:`~LoadBlacklists` | :meth:`~SaveBlacklists` |
        +------------------------+-------------------------+-------------------------+
        | videoblacklist.csv     | :meth:`~LoadBlacklists` | :meth:`~SaveBlacklists` |
        +------------------------+-------------------------+-------------------------+

    Additional this class allows to access the file ``state.ini`` in the MusicDB State Directory.
    The file can be accessed via :meth:`~musicdb.lib.cfg.config.Config.Set` and :meth:`~musicdb.lib.cfg.config.Config.Get`.
    The section ``meta`` is reserved for this ``MDBState`` class.

    Another section is ``MusicDB`` that represents the state of the MusicDB WebUI (and possibly backend in future).
    One key is ``uimode`` that can be set via :meth:`~SetUIMode` and read via :meth:`~GetUIMode`.
    The value for this key is a string and can be ``"audio"`` or ``"video"``.
    The value represents if the user interface is in audio-mode to manage an audio stream or video-mode to present music videos.

    The method :meth:`~GetGenreFilterList` accesses a section ``albumfiler``.
    Each key in this section represents a main genre (all characters lower case) tag and can have the value ``True`` or ``False``.
    If a genre is not listed in this section, it is assumed to have the value ``False``.
    As soon as the genre gets activated via the WebUIs genre selection interface, it appears in the albumfiler-list.

    The method :meth:`~GetSubgenreFilterList` returns a list of selected sub genres for a certain genre,
    similar to the :meth:`~GetGenreFilterList`.
    It accesses a section ``SubgenreFilter:$genre`` where ``$genre`` is the main genre name.
    The sections are created and updated via :meth:`~UpdateSubgenreFilterList`.

    Args:
        path: Absolute path to the MusicDB state directory
        musicdb: Instance of the MusicDB Database (can be None)
    """

    def __init__(self, path, musicdb=None):

        Config.__init__(self, os.path.join(path, "state.ini"))
        self.musicdb = musicdb
        self.path    = path
        self.meta    = META

        self.meta.version = self.Get(int, "meta", "version", 0) # 0 = inf
        if self.meta.version < 2:
            logging.info("Updating %s/state.ini to version 2", path)
            self.Set("meta", "version", 2)
        if self.meta.version < 3:
            logging.info("Updating %s/state.ini to version 3", path)
            self.Set("meta", "version", 3)
            self.Set("MusicDB", "uimode", "audio")
        if self.meta.version < 4:
            logging.info("Updating %s/state.ini to version 4", path)
            self.Set("meta", "version", 4)
            self.RemoveSection("albumfilter")


    def ReadList(self, listname):
        """
        Reads a list from the mdbstate directory.
        The ``listname`` argument defines which file gets read: ``config.directories.state + "/listname.csv"``.

        This method should only be used by class internal methods.
        When a file can not be accessed, an empty list gets returned.
        So deleting a file is an option to reset an internal state of MusicDB.

        Args:
            listname (str): Name of the list to read without trailing .csv

        Returns:
            A list of rows from the file. When reading the list fails, an empty list gets returned.
        """
        path = os.path.join(self.path, listname + ".csv")

        try:
            csv  = CSVFile(path)
            rows = csv.Read()
        except Exception as e:
            logging.warning("Accessing file \"%s\" failed with error %s", str(path), str(e))
            return []

        return rows


    def WriteList(self, listname, rows, header=None):
        """
        This method write a list of rows into the related file.
        The ``listname`` argument defines which file gets written: ``config.directories.state + "/listname.csv"``.

        When there is no header given (list of column names), the keys of the rows-dictionaries are used.

        This method should only be used by class internal methods.

        Args:
            listname (str): Name of the list to read without trailing .csv
            rows(list): The list that shall be stored
            header (list): Optional list with column names as string.

        Returns:
            ``True`` on success, otherwise ``False``
        """
        path = os.path.join(self.path, listname + ".csv")

        if type(rows) != list:
            logging.warning("Expected a list to write into the csv file at \"%s\". Got type \"$s\" instead. \033[1;30m(Will not change the file)", path, str(type(rows)))
            return False

        try:
            csv  = CSVFile(path)
            csv.Write(rows, header)
        except Exception as e:
            logging.warning("Accessing file \"%s\" failed with error %s", str(path), str(e))
            logging.debug("Header: %s", str(header))
            logging.debug("Data: %s", str(rows))
            return False
        return True


    def LoadSongQueue(self):
        """
        This method reads the song queue from the state directory.

        The method returns the queue as needed inside :meth:`musicdb.mdbapi.songqueue.SongQueue`:
        A list of dictionaries, each containing the ``entryid`` and ``songid`` as integers and ``israndom`` as boolean.

        The UUIDs of the queue entries remain.

        Returns:
            A stored song queue
        """
        rows  = self.ReadList("songqueue")
        queue = []
        for row in rows:
            try:
                entry = {}
                entry["entryid"]  = int( row["EntryID"])
                entry["songid"]   = int( row["SongID"])
                entry["israndom"] = (row["IsRandom"] == "True")

                queue.append(entry)
            except Exception as e:
                logging.warning("Invalid entry in stored Song Queue: \"%s\"! \033[1;30m(Entry will be ignored)", str(row))

        return queue


    def SaveSongQueue(self, queue):
        """
        This method saves a song queue.
        The data structure of the queue must be exact as the one expected when the queue shall be loaded.

        Args:
            queue (dictionary): The song queue to save.

        Returns:
            *Nothing*
        """
        # transform data to a structure that can be handled by the csv module
        # save entry ID as string, csv cannot handle 128bit integer
        rows = []
        for entry in queue:
            row = {}
            row["EntryID"]  = str(entry["entryid"])
            row["SongID"]   = int(entry["songid"])
            row["IsRandom"] = str(entry["israndom"])

            rows.append(row)

        self.WriteList("songqueue", rows)
        return


    def LoadVideoQueue(self):
        """
        This method reads the video queue from the state directory.

        The method returns the queue as needed inside :meth:`musicdb.mdbapi.videoqueue.VideoQueue`:
        A list of dictionaries, each containing the ``entryid`` and ``videoid`` as integers and ``israndom`` as boolean.

        The UUIDs of the queue entries remain.

        Returns:
            A stored video queue
        """
        rows  = self.ReadList("videoqueue")
        queue = []
        for row in rows:
            try:
                entry = {}
                entry["entryid"]  = int( row["EntryID"])
                entry["videoid"]  = int( row["VideoID"])
                entry["israndom"] = (row["IsRandom"] == "True")

                queue.append(entry)
            except Exception as e:
                logging.warning("Invalid entry in stored Video Queue: \"%s\"! \033[1;30m(Entry will be ignored)", str(row))

        return queue


    def SaveVideoQueue(self, queue):
        """
        This method saves a video queue.
        The data structure of the queue must be exact as the one expected when the queue shall be loaded.

        Args:
            queue (dictionary): The video queue to save.

        Returns:
            *Nothing*
        """
        # transform data to a structure that can be handled by the csv module
        # save entry ID as string, csv cannot handle 128bit integer
        rows = []
        for entry in queue:
            row = {}
            row["EntryID"]  = str(entry["entryid"])
            row["VideoID"]   = int(entry["videoid"])
            row["IsRandom"] = str(entry["israndom"])

            rows.append(row)

        self.WriteList("videoqueue", rows)
        return


    def __LoadBlacklist(self, filename, idname, length):
        # filename: artistblacklist
        # idname:   ArtistID
        if filename not in ["artistblacklist","albumblacklist","songblacklist","videoblacklist"]:
            raise ValueError("filename must be \"artistblacklist\", \"albumblacklist\" or \"songblacklist\", \"videoblacklist\"")
        if idname not in ["ArtistID","AlbumID","SongID","VideoID"]:
            raise ValueError("idname must be \"ArtistID\", \"AlbumID\" or \"SongID\". \"VideoID\"")

        rows      = self.ReadList(filename)
        rows      = rows[:length]   # Do not process more entries than necessary
        blacklist = []
        for row in rows:
            try:
                entry = {}
                if row[idname] == "":
                    entry["id"] = None
                else:
                    entry["id"] = int(row[idname])

                if row["TimeStamp"] == "":
                    entry["timestamp"] = None
                else:
                    entry["timestamp"] = int(row["TimeStamp"])

                blacklist.append(entry)
            except Exception as e:
                logging.warning("Invalid entry in stored blacklist %s: \"%s\"! - Error: \"%s\" \033[1;30m(Entry will be ignored)",
                        filename+".csv", str(row), str(e))

        # Fill the rest of the blacklist, that was not stored in a file
        diff = length - len(rows)
        if diff > 0:
            for _ in range(diff):
                entry = {}
                entry["id"]        = None
                entry["timestamp"] = None
                blacklist.append(entry)
    
        return blacklist

    def LoadBlacklists(self, songbllen, albumbllen, artistbllen, videobllen):
        """
        This method returns a dictionary with the blacklist used by :class:`musicdb.mdbapi.randy.Randy`.
        The blacklists are managed by the :class:`~musicdb.mdbapi.blacklist.BlacklistInterface` class.
        This method also handles the blacklist length by adding empty entries or cutting off exceeding ones.

        Args:
            songbllen (int): Number of entries the blacklist shall have
            albumbllen (int): Number of entries the blacklist shall have
            artistbllen (int): Number of entries the blacklist shall have
            videobllen (int): Number of entries the blacklist shall have

        Returns:
            A dictionary with the blacklists as expected by :class:`musicdb.mdbapi.randy.Randy`
        """

        blacklists = {}
        blacklists["artists"] = self.__LoadBlacklist("artistblacklist", "ArtistID", artistbllen)
        blacklists["albums"]  = self.__LoadBlacklist("albumblacklist",  "AlbumID",  albumbllen)
        blacklists["songs"]   = self.__LoadBlacklist("songblacklist",   "SongID",   songbllen)
        blacklists["videos"]  = self.__LoadBlacklist("videoblacklist",  "VideoID",  videobllen)
        return blacklists



    def __SaveBlacklist(self, blacklist, filename, idname):
        if filename not in ["artistblacklist","albumblacklist","songblacklist","videoblacklist"]:
            raise ValueError("filename must be \"artistblacklist\", \"albumblacklist\" or \"songblacklist\", \"videoblacklist\"")
        if idname not in ["ArtistID","AlbumID","SongID","VideoID"]:
            raise ValueError("idname must be \"ArtistID\", \"AlbumID\" or \"SongID\", \"VideoID\"")

        rows = []
        for entry in blacklist:
            if entry["id"] == None:
                continue
            row = {}
            row[idname]      = int(entry["id"])
            row["TimeStamp"] = int(entry["timestamp"])

            rows.append(row)

        self.WriteList(filename, rows, [idname, "TimeStamp"])
        return

    def SaveBlacklists(self, blacklists):
        """
        This method stores the blacklist in the related CSV files.
        The data structure of the dictionary is expected to be the same, :class:`musicdb.mdbapi.blacklist.BlacklistInterface` uses.

        Args:
            blacklist (dict): A dictionary of blacklists.

        Returns:
            *Nothing*
        """
        self.__SaveBlacklist(blacklists["songs"],   "songblacklist",   "SongID")
        self.__SaveBlacklist(blacklists["albums"],  "albumblacklist",  "AlbumID")
        self.__SaveBlacklist(blacklists["artists"], "artistblacklist", "ArtistID")
        self.__SaveBlacklist(blacklists["videos"],  "videoblacklist",  "VideoID")
        return


    def UpdateGenreFilterList(self, genre, enable):
        """
        Sets the enable-state of a genre to the value of the parameter ``enable``.

        The value is stored in the state.ini file under the category ``"GenreFilter"``.
        See :meth:`~GetGenreFilterList` for reading out the information.

        Args:
            genre (str): Name of a genre to enable or disable
            enable (bool): Enable or disable genre

        Returns:
            *Nothing*
        """
        if type(enable) != bool:
            raise ValueError("Value of the genre %s must be a boolean. Given was a %s."%(name, type(value)))

        self.Reload()
        self.Set("GenreFilter", genre, enable)
        logging.debug("Filter list updated for genre %s -> %s. New list: %s", genre, str(enable), str(self.GetGenreFilterList()))
        return


    def GetGenreFilterList(self):
        """
        This method returns a list of the activated genre
        The list consists of the names of the genres as configured by the user.
        That are the names returned by :meth:`musicdb.lib.db.musicdb.MusicDatabase.GetAllTags`.

        The available genres get compared to the ones set in the state.ini file inside the MusicDB State directory.
        If a genre is not defined in the configuration file, its default value is ``False`` and so it is not active.
        Before the comparison, the state file gets reloaded so that external changes get applied directly.

        See :meth:`~UpdateGenreFilterList` for changing the state of the genres.

        Example:

            .. code-block:: python

                filter = mdbstate.GetGenreFilterList()
                print(filter) # ['Metal','NDH']
                # Metal and NDH are active, other available genres are not enabled.

        Returns:
            A list of main genre names that are activated
        """
        if not self.musicdb:
            raise ValueError("Music Database object required but it is None.")
        filterlist = []
        genretags   = self.musicdb.GetAllTags(MusicDatabase.TAG_CLASS_GENRE)
        
        self.Reload()
        for tag in genretags:
            state = self.Get(bool, "GenreFilter", tag["name"], False)
            if state:
                filterlist.append(tag["name"])

        return filterlist



    def UpdateSubgenreFilterList(self, genre, subgenre, enable):
        """
        Sets the enable-state of a genre to the value of the parameter ``enable``.

        The value is stored in the state.ini file under the category ``SubgenreFilter:$genre``.
        See :meth:`~GetSubgenreFilterList` for reading out the information.

        Args:
            genre (str): Name of a main genre
            subgenre (str): Name of a sub genre to enable or disable
            enable (bool): Enable or disable sub genre

        Returns:
            *Nothing*
        """
        if type(enable) != bool:
            raise ValueError("Value of the genre %s must be a boolean. Given was a %s."%(name, type(value)))

        self.Reload()
        self.Set("SubgenreFilter:" + genre, subgenre, enable)
        logging.debug("Filter list updated for sub genre %s:%s -> %s. New list: %s",
                genre, subgenre, str(enable), str(self.GetSubgenreFilterList(genre)))
        return



    def GetSubgenreFilterList(self, genre):
        """
        This method returns a list of the activated sub genre for a certain genre.
        The list consists of the names of the genres as configured by the user.
        That are the names returned by :meth:`musicdb.lib.db.musicdb.MusicDatabase.GetAllTags`.

        The available sub genres get compared to the ones set in the state.ini file inside the MusicDB State directory.
        If a sub genre is not defined in the configuration file, its default value is ``True`` and so it is active.
        Before the comparison, the state file gets reloaded so that external changes get applied directly.

        The output is independent from the state of the main genre.

        See :meth:`~UpdateSubgenreFilterList` for changing the state of the sub genres.

        Example:

            .. code-block:: python

                filter = mdbstate.GetSubgenreFilterList("Metal")
                print(filter) # ['Death Metal','Black Metal']

        Args:
            genre (str): Name of a genre for that the sub genres will be checked

        Returns:
            A list of sub genre names that are activated
        """
        if not self.musicdb:
            raise ValueError("Music Database object required but it is None.")
        filterlist = []

        genretag     = self.musicdb.GetTagByName(genre)
        genreid      = genretag["id"]
        genrename    = genretag["name"]
        sectionname  = "SubgenreFilter:" + genrename
        subgenretags = self.musicdb.GetAllTags(MusicDatabase.TAG_CLASS_SUBGENRE)

        self.Reload()
        for tag in subgenretags:
            # Only consider sub genres of the given genre
            if tag["parentid"] != genreid:
                continue

            state = self.Get(bool, sectionname, tag["name"], True)
            if state:
                filterlist.append(tag["name"])
        return filterlist


    def GetAllSubgenreFilterLists(self):
        """
        Returns a dictionary with lists of selected sub genres.
        Each key in the dictionary is a main genre name as returned by :meth:`musicdb.lib.db.MusicDatabase.GetAllTags`.
        Behind each key, a list of selected sub genres is stored.
        If no sub genre is selected, the list is empty.
        The lists come from :meth:`~GetSubgenreFilterList`.

        Each main genre is considered, not only the selected ones that would have been returned by :meth:`~GetGenreFilterList`.

        Example:

            .. code-block:: python

                filter = mdbstate.GetAllSubgenreFilterLists()
                print(filter["Metal"]) # ['Death Metal','Black Metal']

        Returns:
            A dict with lists of selected sub genres for each main genre
        """
        genretags = self.musicdb.GetAllTags(MusicDatabase.TAG_CLASS_GENRE)
        subgenrefilter = {}
        for genre in genretags:
            genrename = genre["name"]
            subgenres = self.GetSubgenreFilterList(genrename)
            subgenrefilter[genrename] = subgenres

        return subgenrefilter



    def GetActiveTagIDs(self):
        """
        Returns a list of tag IDs of active genres and their active sub genres.
        Only sub genres of active genres are considered.
        If no sub genre is active, but the main genre is, then the main genre ID is included.
        This can be the case when there is no sub genre existing for a main genre.
        Then the main genre ID is included.
        In all other cases, only the sub genre IDs are included.

        Example:

            .. code-block:: python

                filter = mdbstate.GetActiveTagIDs()
                print(filter) # [1, 13, 42]

        Returns:
            A list of genre and sub genre tag IDs
        """
        genrenames = self.GetGenreFilterList()

        tagids = []
        for genrename in genrenames:
            genre = self.musicdb.GetTagByName(genrename, MusicDatabase.TAG_CLASS_GENRE)

            subgenrenames = self.GetSubgenreFilterList(genrename)

            if subgenrenames:
                for subgenrename in subgenrenames:
                    subgenre = self.musicdb.GetTagByName(subgenrename, MusicDatabase.TAG_CLASS_SUBGENRE)
                    tagids.append(subgenre["id"])
            else:
                # Only include genre ID when there is no sub genre active or existing
                tagids.append(genre["id"])

        return tagids



    def GetUIMode(self):
        """
        This method simply returns the content of ``[MusicDB]->uimode`` in the state.ini file.
        In case the value is invalid or not set, ``"audio"`` gets returned.

        Valid strings are ``"audio"`` or ``"video"``

        Returns:
            A string ``"audio"`` or ``"video"``
        """
        mode = self.Get(str, "MusicDB", "uimode", "audio")
        if mode not in ["audio", "video"]:
            mode = "audio"
        return mode

    def SetUIMode(self, mode):
        """
        Sets the UI mode in the state.ini file.
        Before writing the data ``mode`` gets checked if it contains a valid value.
        If mode is an invalid argument, an exception gets raised.

        Args:
            mode (str): ``"audio"`` or ``"video"`` mode

        Returns:
            ``None``

        Raises:
            TypeError: When mode is not of type string
            ValueError: When mode contains an invalid string
        """
        if type(mode) is not str:
            raise TypeError("Mode must be a string")
        if not mode in ["audio", "video"]:
            raise ValueError("Mode must be \"audio\" or \"video\"")

        self.Set("MusicDB", "uimode", mode) 
        return None

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

