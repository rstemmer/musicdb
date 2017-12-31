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
This MusicDB component adds a random song under certain constraint into MPDs (Music Playing Daemon) the song-queue

Randy consists of two parts:

* The :meth:`~mdbapi.randy.RandyThread` and its environment :meth:`~mdbapi.randy.StartRandy` and :meth:`mdbapi.randy.StopRandy`.
* The :class:`~mdbapi.randy.RandyInterface` class providing an interface to interact with the :meth:`~mdbapi.randy.RandyThread`. This can happen in several threads simultaneously.

To use Randy, start the :meth:`~mdbapi.randy.RandyThread` by calling :meth:`~mdbapi.randy.StartRandy` once. 
Now it is possible to access the randomizer using the :class:`~mdbapi.randy.RandyInterface` class. This can be done from multiple different threads.
When Randy is not needed anymore, it can be stopped by calling :meth:`~mdbapi.randy.StopRandy`.

.. code-block:: python

    # Dependencies 
    cfg      = MusicDBConfig("./musicdb.ini")

    # Start Randy
    StartRandy(cfg)

    # Use Randy (Can be anywhere in the code)
    randy = RandyInterface()
    randy.AddSong("next")   # add random song after current song
    randy.AddSong("last")   # add random song at the end of the queue

    # Stop Randy
    StopRandy()

"""

import logging
from threading          import Thread
import time
import datetime
from lib.cfg.musicdb    import MusicDBConfig
from lib.db.musicdb     import MusicDatabase
from lib.cfg.mdbstate   import MDBState
import mdbapi.mpd as mpd

RUN    = False
THREAD = None
CMDQUEUE = []
CMD_ADDSONG         = 1
CMD_PRINTBLACKLIST  = 2

def StartRandy(config):
    """
    Starts the randy thread.
    You should use this function instead of calling the RandyThread directly.

    Args:
        config: a MusicDB config object

    Returns:
        ``None`` if something went wrong, otherwise the thread-handler will be returned
    """
    global THREAD
    if THREAD != None:
        logging.warning("Randy already running")
        return None

    global RUN
    RUN    = True
    THREAD = Thread(target=RandyThread, args=(config, ))
    THREAD.start()

    return THREAD


def StopRandy():
    """
    Stops the Randy thread.
    This function is blocking and waits until the thread is closed.

    Returns:
        ``None``
    """
    global RUN
    global THREAD
    RUN    = False
    if THREAD:
        THREAD.join()
    else:
        logging.debug("There is no Thread to stop!")
    THREAD = None
    return None


def RandyThread(config):
    """
    .. warning::

        This function should not be called directly. Use :meth:`~mdbapi.randy.StartRandy` to execute the Thread!

    This Thread chooses a random song in a two-stage process.
    The first stage selects a song from a limited set of songs, the second stage checks if the song is on a blacklist.
    
    .. warning::

        The process of trying to get a good song gets repeated until a good song is found.
        If over constraint, this ends in an infinite loop!
        

    **Database-Stage**

    The Song gets chosen by the :meth:`lib.db.musicdb.MusicDatabase.GetRandomSong` datebase access call.
    There are 4 parameters that define the set on of possible songs.
    Some of them can be configured in the MusicDB configuration file.

        - The activated genres
        - Flag if *disabled* songs shall be excluded
        - Flag if *hated* songs shall be excluded
        - Minimum length of a song in seconds

    Because the database only takes album tags into account, the song tags gets checked afterwards.
    If the song has a genre tag, and if this tag does not match the filter, the song gets rejected.
    Song genres set by the AI will be ignored because the AI may be wrong.

    **Blacklist-Stage**

    The selected song gets compared to three blacklists of configurable length: Artist, Album, Song.
    If the song is listed in a blacklist, the song, a song from the same album or from the same artist was played in near past.
    So: the chosen song gets dropped and the finding-process starts again.

    Is the blacklist length set to 0, the specific blacklist is disabled

    If a song is found. The oldest entries of the blacklist get dropped, and the new song, album, artist get pushed on top of the list.
    Then the song gets added to the *MPD-Queue* and the ``qrndadds`` statistic gets incremented.

    Args:
        config: :class:`lib.cfg.musicdb.MusicDBConfig` object
    """
    musicdb     = MusicDatabase(config.database.path)
    mdbstate    = MDBState(config.server.statefile, musicdb)
    interval    = config.randy.interval
    nodisabled  = config.randy.nodisabled
    nohated     = config.randy.nohated
    minlen      = config.randy.minsonglen
    songbllen   = config.randy.songbllen
    albumbllen  = config.randy.albumbllen
    artistbllen = config.randy.artistbllen
    global RUN
    global CMDQUEUE

    songblacklist   = [None] * songbllen
    albumblacklist  = [None] * albumbllen
    artistblacklist = [None] * artistbllen

    while RUN:
        # Get next command if one is available
        if len(CMDQUEUE) > 0:
            (cmd, args) = CMDQUEUE.pop(0)
        else: 
            time.sleep(interval)
            continue

        # execute commands
        if cmd == CMD_PRINTBLACKLIST:
            print("\033[1;36mRandy's Blacklists:")
            print("\033[1;34m\tSongs:")
            for entry in songblacklist:
                print("\033[1;31m\t - \033[0;36m%s"%(str(entry)))
            print("\033[1;34m\tAlbums:")
            for entry in albumblacklist:
                print("\033[1;31m\t - \033[0;36m%s"%(str(entry)))
            print("\033[1;34m\tArtists:")
            for entry in artistblacklist:
                print("\033[1;31m\t - \033[0;36m%s"%(str(entry)))


        elif cmd == CMD_ADDSONG:
            # Get parameters
            position   = args[0]

            filterlist = mdbstate.GetFilterList()
            if not filterlist:
                logging.warning("No Genre selected")
                continue

            # Get Random Song
            logging.debug("Randy starts looking for a random song …")
            t_start = datetime.datetime.now()
            song    = None
            while not song and RUN:
                # STAGE 1: Get Mathematical random song (under certain constraints)
                try:
                    song = musicdb.GetRandomSong(filterlist, nodisabled, nohated, minlen) # returns None if there is no song
                except Exception as e:
                    logging.error("Getting random song failed with error: \"%s\"!", str(e))
                    song = None
                    continue

                if not song:
                    continue
                logging.debug("Candidate for next song: \033[0;35m" + song["path"])

                # GetRandomSong only looks for album genres.
                # The song genre may be diffrent and not in the set of the filerlist.
                try:

                    songgenres = musicdb.GetTargetTags("song", song["id"], MusicDatabase.TAG_CLASS_GENRE)
                    # Create a set of tagnames if there are tags for this song.
                    # Ignore AI set tags because they may be wrong
                    if songgenres:
                        tagnames = { songgenre["name"] for songgenre in songgenres if songgenre["approval"] >= 1 }
                    else:
                        tagnames = { }

                    # If the tagname set was successfully created, compare it with the selected genres
                    if tagnames:
                        if not tagnames & set(filterlist):
                            logging.debug("song of different genre than album and not in activated genres. (Song genres: %s)", str(tagnames))
                            song = None
                            continue

                except Exception as e:
                    logging.error("Song tag check failed with exception: \"%s\"!", str(e))
                    song = None
                    continue


                # STAGE 1: Make Randomnes feeling random
                if artistbllen > 0 and song["artistid"] in artistblacklist:
                    logging.debug("artist on blacklist")
                    song = None
                    continue
                if albumbllen > 0 and song["albumid"] in albumblacklist:
                    logging.debug("album on blacklist")
                    song = None
                    continue
                if songbllen > 0 and song["id"] in songblacklist:
                    logging.debug("song on blacklist")
                    song = None
                    continue 

            if not song:
                logging.warning("The loop that should find a new random song did not deliver a song! \033[1;30m(This can happen if the server got shut down before)")
                continue

            # maintain blacklists
            artistblacklist.pop(0)
            artistblacklist.append(song["artistid"])
            albumblacklist.pop(0)
            albumblacklist.append(song["albumid"])
            songblacklist.pop(0)
            songblacklist.append(song["id"])

            # Add song to queue
            t_stop = datetime.datetime.now()
            logging.debug("Randy found the following song after %s : \033[0;36m" + song["path"], str(t_stop-t_start))
            success = mpd.AddSong(song["path"], position)

            # Update statistics
            if success:
                if config.debug.disablestats:
                    logging.info("Updating song statistics disabled. \033[1;33m!!")
                    continue
                musicdb.UpdateSongStatistic(song["id"], "qrndadds", "inc")



class RandyInterface(object):
    """
    Interface to the :meth:`~mdbapi.randy.RandyThread`. 
    This class is made to access the thread form all over the code simultaneously.
    """
    def __init__(self):
        pass


    def AddSong(self, position="last"):
        """
        Triggers Randy to add a random song into the song-queue

        Args:
            position (str): Determines where the song gets added. ``"next"``: after the current playing song, or ``"last"`` at the end of the queue.

        Returns:
            ``None``
        """
        CMDQUEUE.append((CMD_ADDSONG, [position]))
        return None


    def PrintBlacklist(self):
        """
        Triggers Randy to print the blacklists to *stdout*.
        This can be useful for debugging. 

        Returns:
            ``None``
        """
        CMDQUEUE.append((CMD_PRINTBLACKLIST, []))
        return None


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

