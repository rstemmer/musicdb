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
The *randy* module provides a way to select random songs or videos that can be put into the Song/Video Queue.
The selection of random music follows certain constraints.


Song Selection Algorithm
------------------------

Selecting a random song is done in two stages, the `Database Stage`_ and the `Blacklist Stage`_
The first stage selects a song from a limited set of songs, the second stage checks if the song is on a blacklist.
In each stage, a song can be rejected and the algorithm starts at the beginning.


.. warning::

    The process of trying to get a good song gets repeated until a good song is found.
    If over constraint, this ends in an infinite loop!


Database Stage
^^^^^^^^^^^^^^

In the first stage, a song gets chosen by the database via :meth:`musicdb.lib.db.musicdb.MusicDatabase.GetRandomSong`.
There are 4 parameters that define the constraints applied on set of possible songs:

    - The activated genres as maintained by the :mod:`musicdb.lib.cfg.mdbstate` module.
    - The flag if *disabled* songs shall be excluded
    - The flag if *hated* songs shall be excluded
    - Minimum and maximum length of a song in seconds

Some of them can be configured in the MusicDB configuration file:

    .. code-block:: ini

        [Randy]
        nodisabled=True
        nohated=True
        minsonglen=120

Because the database only takes album tags into account, the song tags gets checked afterwards.
If the song has a confirmed genre tag, and if this tag does not match the filter, the song gets rejected.
Song genres that are automatically set by an algorithm (and not confirmed by the user) will be ignored because the algorithm may be wrong.


Blacklist Stage
^^^^^^^^^^^^^^^

The selected song from the first stage now gets compared to the blacklists via 
:meth:`musicdb.mdbapi.blacklist.BlacklistInterface.CheckAllListsForSong` or
:meth:`musicdb.mdbapi.blacklist.BlacklistInterface.CheckSongList`.
If the song, or its album or artist, is listed in one of blacklist, 
then the song, a song from the same album or from the same artist was played recently.
So, the chosen song gets dropped and the finding-process starts again.

Is the blacklist length set to 0, the specific blacklist is disabled


Video Selection Algorithm
-------------------------

The selection of a video is a slightly simplified way as done for Songs.
For the blacklist stage it does not considers any Artist and Album associations and therefore the corresponding blacklists.

"""

import logging
import datetime
from musicdb.lib.cfg.musicdb    import MusicDBConfig
from musicdb.lib.db.musicdb     import MusicDatabase
from musicdb.lib.cfg.mdbstate   import MDBState
from musicdb.mdbapi.blacklist   import BlacklistInterface



class Randy(object):
    """
    This class provides methods to get a random song or video under certain constraints.

    Args:
        config: :class:`~musicdb.lib.cfg.musicdb.MusicDBConfig` object holding the MusicDB Configuration
        database: A :class:`~musicdb.lib.db.musicdb.MusicDatabase` instance

    Raises:
        TypeError: When the arguments are not of the correct type.
    """

    def __init__(self, config, database):
        if type(config) != MusicDBConfig:
            raise TypeError("config argument not of type MusicDBConfig")
        if type(database) != MusicDatabase:
            raise TypeError("database argument not of type MusicDatabase")

        self.db         = database
        self.cfg        = config
        self.mdbstate   = MDBState(self.cfg.server.statedir, self.db)
        self.blacklist  = BlacklistInterface(self.cfg, self.db)

        # Load most important keys
        self.nodisabled  = self.cfg.randy.nodisabled
        self.nohated     = self.cfg.randy.nohated
        self.minlen      = self.cfg.randy.minsonglen
        self.maxlen      = self.cfg.randy.maxsonglen
        self.maxtries    = self.cfg.randy.maxtries



    def GetSong(self):
        """
        This method chooses a random song in a two-stage process as described in the module description.

        .. warning::

            Due to too hard constraints, it may be possible that it becomes impossible to find a new song.
            If this is the case, the method returns ``None``.
            The amount of tries can be configured in the MusicDB Configuration

        Returns:
            A song from the :class:`~musicdb.lib.db.musicdb.MusicDatabase` or ``None`` if an error occurred.
        """
        global BlacklistLock
        global Blacklist

        logging.debug("Randy starts looking for a random song …")
        t_start = datetime.datetime.now()

        filterlist = self.mdbstate.GetFilterList()
        if not filterlist:
            logging.warning("No Genre selected! \033[1;30m(Selecting random song from the whole collection)")
        else:
            logging.debug("Genre filter: %s", str(filterlist))

        # Get Random Song - this may take several tries 
        song    = None
        tries    = 0
        while not song:
            tries += 1
            if tries > self.maxtries:
                logging.error("There was no valid song found within %i tries! \033[1;30m(Check the constraints)", self.maxtries)
                return None
            # STAGE 1: Get Mathematical random song (under certain constraints)
            try:
                song = self.db.GetRandomSong(filterlist, self.nodisabled, self.nohated, self.minlen)
            except Exception as e:
                logging.error("Getting random song failed with error: \"%s\"!", str(e))
                return None

            if not song:
                logging.error("There is no song fulfilling the constraints! \033[1;30m(Check the stage 1 constraints)")
                return None

            logging.debug("Candidate for next song: \033[0;35m" + song["path"])

            # The MusicDatabase method GetRandomSong only looks for album genres.
            # The song genre may be different and not in the set of the filterlist.
            try:

                songgenres = self.db.GetTargetTags("song", song["id"], MusicDatabase.TAG_CLASS_GENRE)
                # Create a set of tagnames if there are tags for this song.
                # Ignore AI set tags because they may be wrong
                if songgenres:
                    tagnames = { songgenre["name"] for songgenre in songgenres if songgenre["approval"] >= 1 }
                else:
                    tagnames = { }

                # If the tag name set was successfully created, compare it with the selected genres
                if tagnames:
                    logging.debug("Checking for intersection of song-genre and active-genre: %s ∩ %s", str(tagnames), str(filterlist))
                    if not tagnames & set(filterlist):
                        logging.debug("song is of different genre than album and not in activated genres. (Song genres: %s)", str(tagnames))
                        song = None
                        continue
                else:
                    logging.debug("The song candidate has no genre tags. Assuming it matches the album genre.")

            except Exception as e:
                logging.error("Song tag check failed with exception: \"%s\"!", str(e))
                return None


            # STAGE 2: Make randomness feeling random by checking if the song/album/artist was recently played
            if self.blacklist.CheckAllListsForSong(song):
                song = None
                continue

        # New song found \o/
        t_stop = datetime.datetime.now()
        logging.debug("Randy found the following song after %s : \033[0;36m%s", str(t_stop-t_start), song["path"])
        return song



    def GetSongFromAlbum(self, albumid):
        """
        Get a random song from a specific album.

        If the selected song is listed in the blacklist for songs, a new one will be selected.
        Entries in the album and artist blacklist will be ignored because the artist and album is forced by the user.
        But the song gets added to the blacklist for songs, as well as the album and artist gets added.

        The genre of the song gets completely ignored.
        The user wants to have a song from the given album, so it gets one.

        .. warning::

            This is a dangerous method.
            An album only has a very limited set of songs.

            If all the songs are listed in the blacklist, the method would get caught in an infinite loop.
            To avoid this, there are only a limited amount of tries to find a random song.
            If the limit is reached, the method returns ``None``.
            The amount of tries can be configured in the MusicDB Configuration

        Args:
            albumid (int): ID of the album the song shall come from

        Returns:
            A song from the :class:`~musicdb.lib.db.musicdb.MusicDatabase` or ``None`` if an error occurred.
        """
        global BlacklistLock
        global Blacklist

        # Get parameters
        song       = None
        tries      = 0  # there is just a very limited set of possible songs. Avoid infinite loop when all songs are on the blacklist

        while not song and tries <= self.maxtries:
            tries += 1
            # STAGE 1: Get Mathematical random song (under certain constraints)
            try:
                song = self.db.GetRandomSong(None, self.nodisabled, self.nohated, self.minlen, self.maxlen, albumid)
            except Exception as e:
                logging.error("Getting random song failed with error: \"%s\"!", str(e))
                return None
            logging.debug("Candidate for next song: \033[0;35m" + song["path"])
            
            # STAGE 2: Make randomness feeling random by checking if the song was recently played
            # only check, if that song is in the blacklist. Artist and album is forced by the user
            if self.blacklist.CheckSongList(song):
                    song = None
                    continue 

        if not song:
            logging.warning("The loop that should find a new random song did not deliver a song! \033[1;30m(This happens when there are too many songs of the given album are already on the blacklist)")
            return None

        # Add song to queue
        logging.debug("Randy adds the following song after %s tries: \033[0;36m%s", tries, song["path"])
        return song



    def GetVideo(self):
        """
        This method chooses a random video in a simplified two-stage process as described in the module description.
        This method will be refined in future to fully behave like the :meth:`~GetSong` method.

        .. warning::

            Due to too hard constraints, it may be possible that it becomes impossible to find a new song.
            If this is the case, the method returns ``None``.
            The amount of tries can be configured in the MusicDB Configuration

        Returns:
            A video from the :class:`~musicdb.lib.db.musicdb.MusicDatabase` or ``None`` if an error occurred.
        """
        global BlacklistLock
        global Blacklist

        logging.debug("Randy starts looking for a random video …")
        t_start = datetime.datetime.now()

        filterlist = self.mdbstate.GetFilterList()
        if not filterlist:
            logging.warning("No Genre selected! \033[1;30m(Selecting random video from the whole collection)")
        else:
            logging.debug("Genre filter: %s", str(filterlist))

        # Get Random Video - this may take several tries 
        video    = None
        tries    = 0
        while not video:
            tries += 1
            if tries > self.maxtries:
                logging.error("There was no valid video found within %i tries! \033[1;30m(Check the constraints)", self.maxtries)
                return None

            # STAGE 1: Get Mathematical random video (under certain constraints)
            try:
                video = self.db.GetRandomVideo(filterlist, self.nodisabled, self.nohated, self.minlen)
            except Exception as e:
                logging.error("Getting random video failed with error: \"%s\"!", str(e))
                return None

            if not video:
                logging.error("There is no video fulfilling the constraints! \033[1;30m(Check the stage 1 constraints)")
                return None

            logging.debug("Candidate for next video: \033[0;35m" + video["path"])


            # STAGE 2: Make randomness feeling random by checking if the video/artist was recently played
            if self.blacklist.CheckAllListsForVideo(video):
                video = None
                continue

        # New video found \o/
        t_stop = datetime.datetime.now()
        logging.debug("Randy found the following video after %s : \033[0;36m%s", str(t_stop-t_start), video["path"])
        return video

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

