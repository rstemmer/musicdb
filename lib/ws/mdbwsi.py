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
Overview of all WebAPI Methods sorted by category (some methods appear multiple times).

Artists
^^^^^^^
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.GetArtists`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.GetArtistsWithAlbums`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.Find`

Albums
^^^^^^
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.GetAlbums`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.GetSortedAlbumCDs`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.GetAlbum`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.SetAlbumColor`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.AddAlbumToQueue`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.Find`

Songs
^^^^^
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.GetSong`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.PlayNextSong`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.AddSongToQueue`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.AddRandomSongToQueue`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.RemoveSongFromQueue`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.MoveSongInQueue`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.GetSongRelationship`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.UpdateSongStatistic`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.CutSongRelationship`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.Find`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.PlayNextSong`

Queue
^^^^^
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.GetQueue`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.AddSongToQueue`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.AddRandomSongToQueue`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.AddAlbumToQueue`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.RemoveSongFromQueue`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.MoveSongInQueue`

Tag related
^^^^^^^^^^^
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.GetTags`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.GetSongTags`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.GetAlbumTags`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.SetAlbumTag`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.RemoveAlbumTag`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.SetSongTag`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.RemoveSongTag`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.AddSubgenre`

Lyrics
^^^^^^
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.GetSongLyrics`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.GetLyricsCrawlerCache`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.RunLyricsCrawler`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.SetSongLyrics`

Other
^^^^^
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.GetMPDState`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.SetMPDState`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.PlayNextSong`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.SetMDBState`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.GetMDBState`

"""
import random
from lib.db.musicdb     import *
from lib.db.trackerdb   import TrackerDatabase
from lib.db.musicdb     import MusicDatabase
from lib.cfg.musicdb    import MusicDBConfig
from lib.filesystem     import Filesystem
import os
from mdbapi.lycra       import Lycra
from mdbapi.database    import MusicDBDatabase
from mdbapi.randy       import RandyInterface
from mdbapi.mise        import MusicDBMicroSearchEngine
import mdbapi.mpd as mpd
import logging
from threading          import Thread
import traceback

class MusicDBWebSocketInterface(object):

    def __init__(self):
        # Import global variables from the server
        from mdbapi.server import database, mise, cfg, mdbstate
        self.database   = database
        self.mise       = mise
        self.cfg        = cfg
        self.fs         = Filesystem(self.cfg.music.path)
        self.mdbstate   = mdbstate
        self.randy      = None  # RandyInterface will be created onWSConnect

        self.MaxCallThreads     = self.cfg.server.maxcallthreads
        self.CallThreadList     = [None] * self.MaxCallThreads



    def onWSConnect(self):
        self.randy = RandyInterface()
        mpd.RegisterCallback(self.onMPDEvent)
        return None
        

    def onWSDisconnect(self, wasClean, code, reason):
        mpd.RemoveCallback(self.onMPDEvent)
        return None


    def onMPDEvent(self, event, data):
        # This function is called from a different thread. Therefore NO sqlite3-access is allowed.
        # So there will be just a notification so that the clients can request an MPDStateUpdate.
        response    = {}
        response["method"]      = "notification"
        response["fncname"]     = "mpd"
        response["fncsig"]      = "on"+event
        response["arguments"]   = data
        response["pass"]        = None
        success = self.SendPacket(response)
        return success


    def HandleCall(self, fncname, method, fncsig, args, passthrough):
        retval = None

        # Request-Methods
        if fncname == "GetArtists":
            retval = self.GetArtists()
        elif fncname == "GetArtistsWithAlbums":
            retval = self.GetArtistsWithAlbums()
        elif fncname == "GetFilteredArtistsWithAlbums":
            retval = self.GetArtistsWithAlbums(applyfilter=True)
        elif fncname == "GetAlbums":
            retval = self.GetAlbums(args["artistid"], args["applyfilter"])
        elif fncname == "GetAlbum":
            retval = self.GetAlbum(args["albumid"])
        elif fncname == "GetSortedAlbumCDs":
            retval = self.GetSortedAlbumCDs(args["albumid"])
        elif fncname == "GetSong":
            retval = self.GetSong(args["songid"])
        elif fncname == "GetTags":
            retval = self.GetTags()
        elif fncname == "GetSongTags":
            retval = self.GetSongTags(args["songid"])
        elif fncname == "GetAlbumTags":
            retval = self.GetAlbumTags(args["albumid"])
        elif fncname == "GetMDBState":
            retval = self.GetMDBState()
        elif fncname == "GetMPDState":
            retval = self.GetMPDState()
        elif fncname == "GetQueue":
            retval = self.GetQueue()
        elif fncname == "Find":
            retval = self.Find(args["searchstring"], args["limit"])
        elif fncname == "GetSongRelationship":
            retval = self.GetSongRelationship(args["songid"])
        elif fncname == "GetSongLyrics":
            retval = self.GetSongLyrics(args["songid"])
        elif fncname == "GetLyricsCrawlerCache":
            retval = self.GetLyricsCrawlerCache(args["songid"])
        elif fncname == "RunLyricsCrawler":
            retval = self.RunLyricsCrawler(args["songid"])
        # Call-Methods (retval will be ignored unless method gets not changed)
        elif fncname == "SetMDBState":
            retval = self.SetMDBState(args["category"], args["name"], args["value"])
            retval = self.GetMDBState()
            method = "broadcast"
            fncname= "GetMDBState"
        elif fncname == "SetSongTag":
            retval = self.SetSongTag(args["songid"], args["tagid"])
            retval = self.GetSong(args["songid"])
            method = "broadcast"
            fncname= "GetSong"
        elif fncname == "RemoveSongTag":
            retval = self.RemoveSongTag(args["songid"], args["tagid"])
            retval = self.GetSong(args["songid"])
            method = "broadcast"
            fncname= "GetSong"
        elif fncname == "AddSubgenre":
            retval = self.AddSubgenre(args["name"], args["parentname"])
        elif fncname == "SetAlbumTag":
            retval = self.SetAlbumTag(args["albumid"], args["tagid"])
            retval = self.GetAlbum(args["albumid"])
            method = "broadcast"
            fncname= "GetAlbum"
        elif fncname == "RemoveAlbumTag":
            retval = self.RemoveAlbumTag(args["albumid"], args["tagid"])
            retval = self.GetAlbum(args["albumid"])
            method = "broadcast"
            fncname= "GetAlbum"
        elif fncname == "SetSongLyrics":
            retval = self.SetSongLyrics(args["songid"], args["lyrics"], args["lyricsstate"])
        elif fncname == "SetAlbumColor":
            retval = self.SetAlbumColor(args["albumid"], args["colorname"], args["color"])
        elif fncname == "UpdateSongStatistic":
            retval = self.UpdateSongStatistic(args["songid"], args["statistic"], args["modifier"])
            retval = self.GetSong(args["songid"])
            method = "broadcast"
            fncname= "GetSong"
        elif fncname == "AddSongToQueue":
            retval = self.AddSongToQueue(args["songid"], args["position"])
        elif fncname == "AddAlbumToQueue":
            retval = self.AddAlbumToQueue(args["albumid"])
        elif fncname == "AddRandomSongToQueue":
            retval = self.AddRandomSongToQueue(args["position"])
        elif fncname == "MoveSongInQueue":
            retval = self.MoveSongInQueue(args["songid"], args["srcpos"], args["dstpos"])
        elif fncname == "RemoveSongFromQueue":
            retval = self.RemoveSongFromQueue(args["songid"], args["position"])
        elif fncname == "CutSongRelationship":
            retval = self.CutSongRelationship(args["songid"], args["relatedsongid"])
            if method == "request":
                retval = self.GetSongRelationship(args["songid"])
                fncname= "GetSongRelationship"
        elif fncname == "SetMPDState":
            retval = self.SetMPDState(args["mpdstate"])
        elif fncname == "PlayNextSong":
            retval = self.PlayNextSong()
        else:
            logging.warning("Unknown function: %s! \033[0;33m(will be ignored)", str(fncname))
            return None

        # prepare return behaviour
        response    = {}
        response["fncname"]     = fncname
        response["fncsig"]      = fncsig
        response["arguments"]   = retval
        response["pass"]        = passthrough

        if method == "request":
            response["method"]  = "response"
            self.SendPacket(response)
        elif method == "broadcast":
            response["method"]  = "broadcast"
            self.BroadcastPacket(response)
        return None


    def onCall(self, packet):
        try:
            method      = packet["method"]
            fncname     = packet["fncname"]
            fncsig      = packet["fncsig"]
            arguments   = packet["arguments"]
            passthrough = packet["pass"]
        except:
            logging.warning("Malformed request packet received! \033[0;33m(Call will be ignored)")
            logging.debug("Packet: %s", str(packet))
            return False

        logging.debug("method: %s, fncname: \033[1;37m%s\033[1;30m, fncsig: %s, arguments: %s, pass: %s", 
                str(method),str(fncname),str(fncsig),str(arguments),str(passthrough))

        if not method in ["call", "request", "broadcast"]:
            logging.warning("Unknown call-method: %s! \033[0;33m(Call will be ignored)", str(method))
            return False

        # In some cases a call shall be handles asynchronously to avoid blocking.
        # In Theads there is no access to the musicdb because self.database cannot be used in different threads.
        # So this are just special cases.
        asyncfunctions = [
                "RunLyricsCrawler"
                ]
        if fncname in asyncfunctions:
            try:
                for i in range(self.MaxCallThreads):
                    if self.CallThreadList[i] and self.CallThreadList[i].is_alive():
                        continue
                    self.CallThreadList[i] = Thread(
                            target = MusicDBWebSocketInterface.HandleCall, 
                            args   = (self, fncname, method, fncsig, arguments, passthrough))
                    self.CallThreadList[i].start()
                    break
                else:
                    logging.warning("There are too many asynchronous call-threads running. This request (call for %s) will be ignored!", str(fncname))
                    return False

            except Exception as e:
                logging.error("Unexpected error for async. call-function: %s!", str(fncname))
                logging.error(e)
                traceback.print_exc()
                return False
        else:
            # Handle the Call synchronously
            try:
                self.HandleCall(fncname, method, fncsig, arguments, passthrough)
            except Exception as e:
                logging.error("Unexpected error for async. call-function: %s!", str(fncname))
                logging.error(e)
                traceback.print_exc()
                return False

        return True



    def GetArtists(self):
        """
        Returns a list of artists.
        This list is sorted by the name of the artist.

        A list entry contains the following values:

            * **id:** Artist ID
            * **name:** Artist name
            * **path:** Relative path to the artist directory

        Returns:
            A list of artists

        """
        artists = self.database.GetAllArtists()                     # Get artists from the database
        artists = sorted(artists, key = lambda k: k["name"].lower())# Sort the artists for their name
        return artists


    def GetArtistsWithAlbums(self, applyfilter=False):
        """
        This method returns a list of artists and their albums.
        Each entry in this list contains the following two elements:

            * **artist:** An entry like the list entries of :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.GetArtists`
            * **albums:** A list of albums that was returned by :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.GetAlbums` for the related artist.

        Artists without albums or albums that got filters out will not appear in the list.

        .. attention::
        
            The JavaScript API uses the following aliases: 
            
            * ``GetArtistsWithAlbums``: Without arguments, and so without applying the filter.
            * ``GetFilteredArtistsWithAlbums``: With applying the filter option.

            So, from JavaScripts point of view this method does not have any parameters.
            
        Args:
            applyfilter (bool): Default value is ``False``

        Returns:
            A list of artists and their albums

        Example:
            .. code-block:: javascript

                MusicDB_Request("GetFilteredArtistsWithAlbums", "ShowArtists");

                // …

                function onMusicDBMessage(fnc, sig, args, pass)
                {
                    if(fnc == "GetFilteredArtistsWithAlbums" && sig == "ShowArtists")
                    {
                        for(let artist of args)
                        {
                            console.log("Artist: " + artist.name);
                            for(let album of artist.albums)
                                console.log(" -> " + album.name);
                        }
                    }
                }
        """
        # Get artist-list
        artists = self.GetArtists()

        # Get album for each artist
        artistlist = []
        for artist in artists:
            albums = self.GetAlbums(artist["id"], applyfilter)

            # filter artists with no relevant albums
            if applyfilter and albums == []:
                continue

            entry = {}
            entry["artist"] = artist
            entry["albums"] = albums
            artistlist.append(entry)
        return artistlist 


    def GetAlbums(self, artistid, applyfilter=False):
        """
        GetAlbums returns a list of albums of an artist.
        The list is sorted by release date of the album, starting with the earliest one.
        Each entry in the list has the following two elements:

            * **album:** An album entry from the database.
            * **tags:** The returned tag entry by :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.GetAlbumTags`

        The filter gets applied to only the *genre* tags.

        Args:
            artistid (int): ID of the artist whose albums shall be returned
            applyfilter (bool): Default value is ``False``

        Returns:
            A list of albums and their tags

        Example:
            .. code-block:: javascript

                MusicDB_Request("GetAlbums", "ShowAlbums", {artistid:artistid, applyfilter:false});

                // …

                function onMusicDBMessage(fnc, sig, args, pass)
                {
                    if(fnc == "GetAlbums" && sig == "ShowAlbums")
                    {
                        for(let listentry of args)
                        {
                            let album, tags;
                            album = listentry.album;
                            tags  = listentry.tags;

                            console.log("Tags of " + album.name + ":");
                            console.log(tags);
                        }
                    }
                }
        """
        # Get albums by this artist
        albums = self.database.GetAlbumsByArtistId(artistid)

        # sort albums for release year
        albums = sorted(albums, key = lambda k: k["release"])

        if applyfilter:
            filterset = set(self.mdbstate.GetFilterList())

        # assign tags to albums
        albumlist = []
        for album in albums:
            tags   = self.GetAlbumTags(album["id"])
            genres = tags["genres"]

            # if no tags are available, show the album!
            if applyfilter and genres:
                genreset = { genre["name"] for genre in genres }

                # do not continue with this album,
                # if there is no unionset of genres
                if not filterset & genreset:
                    continue

            entry = {}
            entry["album"]   = album
            entry["tags"]    = tags
            albumlist.append(entry)

        return albumlist


    def GetSortedAlbumCDs(self, albumid):
        """
        This method returns a sorted list of CDs of an album.
        Each CD entry is a further sorted list of songs.
        Each song-entry is a dictionary with the following keys:

            * **song:** The database entry of the song
            * **tags:** a list of tags as returned by :meth:`~lib.ws.mdbwsi.MusicDBWebsScketInterface.GetSongTags`

        Args:
            albumid (int): ID of the album that CD and songs shall be returned

        Returns:
            A sorted list of CDs, its songs and their tags

        """
        # Get the data
        album = self.database.GetAlbumById(albumid)
        songs = self.database.GetSongsByAlbumId(albumid)

        if not album or not songs:
            logging.warning("No or empty album behind ID %s!", str(albumid))
            return []

        # annotate all songs with additional infos like genre-tags
        songlist = []
        for song in songs:
            tags = self.GetSongTags(song["id"])
            songentry = {}
            songentry["song"]      = song
            songentry["tags"]      = tags
            songlist.append(songentry)
            

        # sort the albums songs - if there is no CD, skip for name
        sortedcds = []
        if album["numofcds"] != 0:
            #  1.: separate into CDs
            unsortedcds = []
            for i in range(0, album["numofcds"]):
                cdnum = i + 1   # index 0 is cd 1
                cd = [songentry for songentry in songlist if songentry["song"]["cd"] == cdnum]
                unsortedcds.append(cd)

            #  2.: sort songs of each CD for tracknumber
            sortedcds = []
            for cd in unsortedcds:
                cd = sorted(cd, key = lambda k: k["song"]["number"])
                sortedcds.append(cd)

        else:
            sortedsongs = sorted(songlist, key = lambda k: k["song"]["name"])
            sortedcds.append(sortedsongs)   # make a "virtual" cd

        return sortedcds


    def GetAlbum(self, albumid):
        """
        This method returns an album and its songs, separated by CDs.

        GetAlbum returns a dictionary with the following keys:

            * **artist:** database entry of the artist of the album
            * **album:** the database entry of the album itself
            * **tags:** a list of tags as returned by :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.GetAlbumTags`
            * **cds:** a list of CDs that contains a list of songs for each CD. See :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.GetSortedAlbumCDs` for details.

        Args:
            albumid (int): The ID of that album that shall be returned

        Returns:
            A dictionary with information of the requested album, its tags and songs

        Example:
            .. code-block:: javascript

                MusicDB_Request("GetAlbum", "ShowAlbum", {albumid:albumid});

                // …

                function onMusicDBMessage(fnc, sig, args, pass)
                {
                    if(fnc == "GetAlbum" && sig == "ShowAlbum")
                    {
                        console.log("Artist: " + args.artist.name);
                        console.log("Album:  " + args.album.name);
                        for(let cd of args.cds)
                        {
                            for(let track of cd)
                            {
                                let song, songtags
                                song     = track.song;
                                songtags = track.tags;
                                console.log(" -> " + song.name);
                            }
                        }
                    }
                }
        """
        album   = self.database.GetAlbumById(albumid)
        artist  = self.database.GetArtistById(album["artistid"])
        tags    = self.GetAlbumTags(albumid)

        sortedcds = self.GetSortedAlbumCDs(albumid)

        # send the data to the client
        retval = {}
        retval["artist"]  = artist
        retval["album"]   = album
        retval["tags"]    = tags
        retval["cds"]     = sortedcds 
        return retval


    def GetSong(self, songid):
        """
        This method returns the information of a song, its album and artist, and its tags.

        The returned dictionary has the following keys:

            * **song:** the database entry of the song itself.
            * **artist:** database entry of the artist of the song
            * **album:** the database entry of the album in that the song is listed
            * **tags:** a list of tags as returned by :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.GetSongTags`

        Args:
            songid (int): ID of the song

        Returns:
            A dictionary with information of the song

        Example:
            .. code-block:: javascript

                MusicDB_Request("GetSong", "ShowSong", {songid:songid});

                // …

                function onMusicDBMessage(fnc, sig, args, pass)
                {
                    if(fnc == "GetSong" && sig == "ShowSong")
                    {
                        console.log("Artist: " + args.artist.name);
                        console.log("Album:  " + args.album.name);
                        console.log("Song:   " + args.song.name);
                        for(let mood of args.tags.moods)
                        {
                            console.log("Mood: " + mood.name);
                        }
                    }
                }
        """
        song    = self.database.GetSongById(songid)
        album   = self.database.GetAlbumById(song["albumid"])
        artist  = self.database.GetArtistById(song["artistid"])
        tags    = self.GetSongTags(songid)

        retval = {}
        retval["song"]      = song
        retval["artist"]    = artist
        retval["album"]     = album
        retval["tags"]      = tags
        return retval


    def GetTags(self):
        """
        This method returns all tags that are available, separated by the tag classes.

        Returns:
            A dictionary of all classes with lists of all available tags

        Example:
            .. code-block:: javascript

                MusicDB_Request("GetTags", "ShowTags");

                // …

                function onMusicDBMessage(fnc, sig, args, pass)
                {
                    if(fnc == "GetTags" && sig == "ShowTags")
                    {
                        let genres, subgenres, moods;
                        genres    = args.genres;
                        subgenres = args.subgenres;
                        moods     = args.moods;

                        for(let tag of genres)
                            console.log(tag.name);
                        for(let tag of subgenres)
                            console.log(tag.name);
                        for(let tag of moods)
                            console.log(tag.name);
                    }
                }
        """
        tags = self.database.GetAllTags()
        genres, subgenres, moods = self.database.SplitTagsByClass(tags)
        tags = {}
        tags["genres"]    = genres
        tags["subgenres"] = subgenres
        tags["moods"]     = moods
        return tags


    def GetSongTags(self, songid):
        """
        Returns a dictionary with the following keys:

          * **songid:** The same ID as given as argument
          * **genres:** A list of tags of class *Genre*
          * **subgenres:** A list of tags of class *Subgenre*
          * **moods:** A list of tags of class *Mood*

        Each entry of the dict is a list with tags.
        Each tag is a dictionary as returned by :meth:`lib.db.musicdb.MusicDatabase.GetTargetTags`.

        Args:
            songid (int): ID of the song for which the tags are requested

        Returns:
            A dict of tags sorted by classes

        Example:
            .. code-block:: javascript

                MusicDB_Request("GetSongTags", "ShowSongTags");

                // …

                function onMusicDBMessage(fnc, sig, args, pass)
                {
                    if(fnc == "GetSongTags" && sig == "ShowSongTags")
                    {
                        let genres, subgenres, moods;
                        genres    = args.genres;
                        subgenres = args.subgenres;
                        moods     = args.moods;

                        console.log("Tags of the song with the ID " + args.songid);
                        for(let tag of genres)
                            console.log(tag.name);
                        for(let tag of subgenres)
                            console.log(tag.name);
                        for(let tag of moods)
                            console.log(tag.name);
                    }
                }
        """
        tags = self.database.GetTargetTags("song", songid)
        genres, subgenres, moods = self.database.SplitTagsByClass(tags)
        tags = {}
        tags["songid"]    = songid  # this is necessary to not loose context
        tags["genres"]    = genres
        tags["subgenres"] = subgenres
        tags["moods"]     = moods
        return tags


    def GetAlbumTags(self, albumid):
        """
        Same as :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.GetSongTags` just for an Album
        """
        tags = self.database.GetTargetTags("album", albumid)
        genres, subgenres, moods = self.database.SplitTagsByClass(tags)
        tags = {}
        tags["albumid"]   = albumid  # this is necessary to not loose context
        tags["genres"]    = genres
        tags["subgenres"] = subgenres
        tags["moods"]     = moods
        return tags


    # THIS METHOD IS THREADSAFE
    def SetMDBState(self, category, name, value):
        """
        This method sets the global state of MDB clients

        If the state is not available in the global state settings, it will be created.

        Currently, *category* must always be ``"albumfilter"``. 
        Then, *name* is a Genre-Name and *value* is ``True`` or ``False``.
        If a genre gets set to true, all albums for that genre are included in the list of returned albums by methods that use the filter.

        After executing this method, the MusicDB server broadcasts the result of :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.GetMDBState`. (``method = "broadcast", fncname = "GetMDBState"``)
        So each client gets informed about the new state.

        Args:
            category (str): Category of the state
            name (str): Name of the sate
            value: Value of the state

        Returns:
            ``None``

        Example:
            .. code-block:: javascript

                MusicDB_Call("SetMDBState", {category:"albumfilter", name:"Metal", value:true});
        """
        if not self.mdbstate.OptionAvailable(category, name):
            logging.warning("Unknown state-settings " + str(category) + ">" + str(name) + "! \033[1;30m(Will be created)")

        self.mdbstate.Set(category, name, value)
        return None


    # THIS METHOD IS THREADSAFE
    def GetMDBState(self):
        """
        This method returns the current global state of the MusicDB WebUIs

        This includes the *End of Queue Event* and the selected Genres.

        The state is a dictionary with the following information:

            * **albumfilter:** a list of tag-names of class Genre
            * **queue:** a further dictionary related to the music-queue. Currently, only the *eoqevent* entry exists.

        Returns:
            Current global MusicDB WebUI state

        Example:
            .. code-block:: javascript

                MusicDB_Request("GetMDBState", "ShowMDBState");

                // …

                function onMusicDBMessage(fnc, sig, args, pass)
                {
                    if(fnc == "GetMDBState" && sig == "ShowMDBState")
                    {
                        let activetags;
                        activetags = args.albumfilter;
                        for(let genrename of activetags)
                            console.log(genrename);
                    }
                }
        """
        albumfilter = self.mdbstate.GetFilterList()

        queue = {}
        queue["eoqevent"] = self.mdbstate.queue.eoqevent

        state = {}
        state["albumfilter"] = albumfilter
        state["queue"]       = queue
        return state


    def GetMPDState(self):
        """
        This method returns the state of MPD (Music Playing Daemon).

        The state is a dictionary that has always the following information:

            * **isconnected:** ``True`` if MusicDB is connected to MPD, otherwise ``False``
            * **isplaying:** ``True`` if MPD is in *playing*-mode, otherwise ``False``

        If MusicDB is connected, there are further information about MPDs state:

            * **mpdstatus:** as returned by :meth:`mdbapi.mpd.GetStatus`
            * **hasqueue:** ``True`` If there are songs in MPDs playing-Queue, otherwise ``False``

        In case there is a at least one song in the queue, that song gets played by MPD if ``isplaying`` is ``True``.
        In this case, there are also information about the current song:

            * **song:** The song entry from the database for the song that is currently playing
            * **album:** The related album entry from the database
            * **artist:** The related artist entry from the database
            * **songtags:** a list of tags as returned by :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.GetSongTags`
            * **albumtags:** a list of tags as returned by :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.GetAlbumTags`

        Returns:
            The current state of MPD

        Example:
            .. code-block:: javascript

                MusicDB_Request("GetMPDState", "ShowMPDState");

                // …

                function onMusicDBMessage(fnc, sig, args, pass)
                {
                    if(fnc == "GetMPDState" && sig == "ShowMPDState")
                    {
                        if(args.isconnected == true)
                        {
                            if(args.hasqueue == true)
                            {
                                console.log("Current playing song: " + args.song.name);
                            }
                        }
                    }
                }
        """
        state = {}
        state["isconnected"] = mpd.GetConnectionState()
        state["isplaying"]   = mpd.GetPlayingState()

        # if not connected, there will be no more information
        if state["isconnected"] == True:
            # BE CAREFUL! The structure of mpds song-infos are different from the one used in the database
            mpdsong = mpd.GetCurrentSong()

            # if no file is given, the queue is empty - or "there is no queue"
            if mpdsong and "file" in mpdsong:
                song      = self.database.GetSongByPath(mpdsong["file"])
                album     = self.database.GetAlbumById(song["albumid"])
                artist    = self.database.GetArtistById(song["artistid"])
                songtags  = self.GetSongTags(song["id"])
                albumtags = self.GetAlbumTags(album["id"])

                state["song"]       = song
                state["album"]      = album
                state["artist"]     = artist
                state["songtags"]   = songtags
                state["albumtags"]  = albumtags
                state["hasqueue"]   = True
            else:
                state["hasqueue"]   = False

            state["mpdstatus"] = mpd.GetStatus()

        return state


    def GetQueue(self):
        """
        This method returns a list of songs, albums and artists for each song in the MPD queue.
        If there are not songs in the queue, an empty list gets returned.

        Each entry of the list contains the following information:

            * **song:** The song entry from the database
            * **album:** The related album entry from the database
            * **artist:** The related artist entry from the database

        Returns:
            A list of song, album and artist information for each song in the MPD queue

        Example:
            .. code-block:: javascript

                MusicDB_Request("GetQueue", "ShowQueue");

                // …

                function onMusicDBMessage(fnc, sig, args, pass)
                {
                    if(fnc == "GetQueue" && sig == "ShowQueue")
                    {
                        for(let entry of args)
                        {
                            console.log(entry.song.name + " by " + entry.artist.name);
                        }
                    }
                }
        """
        paths = mpd.GetQueue()

        # return empty list if there is no queue
        if type(paths) != list:
            return []

        queue = []
        for path in paths:
            song = self.database.GetSongByPath(path)

            # it may happen that other tools add songs to mpd that are not handled by the database
            if not song:
                logging.warning("The song behind the path \"%s\" does not exist in the MusicDB database!", str(path))
                continue

            album   = self.database.GetAlbumById(song["albumid"])
            artist  = self.database.GetArtistById(song["artistid"])

            entry = {}
            entry["song"]    = song
            entry["album"]   = album
            entry["artist"]  = artist

            queue.append(entry)

        return queue


    def Find(self, searchstring, limit):
        """
        This method starts a search for *searchstring* on songnames, albumnames and artistnames.
        The returned value is a dictionary with the following entries:

            * **songs:** A list of songs, each entry is a dictionary with the following information:
                * **song:** The song entry from the database
                * **album:** The related album entry from the database
                * **artist:** The related artist entry from the database
            * **albums:** A list of albums, each entry is a dictionary with the following information:
                * **album:** The related album entry from the database
                * **artist:** The related artist entry from the database
            * **artists:** A list of artists, each entry is a dictionary with the following information:
                * **artist:** The related artist entry from the database

        The search does not look for exact matching.
        It looks for most likeliness.
        So, typos or all lowercase input are no problem.

        Args:
            searchstring (str): The string to search for
            limit (int): max number entries that will be returned for each category

        Returns:
            A dictionary with the search-results

        Example:
            .. code-block:: javascript

                MusicDB_Request("Find", "ShowResults", {searchstring:"cake", limit:5});

                // …

                function onMusicDBMessage(fnc, sig, args, pass)
                {
                    if(fnc == "Find" && sig == "ShowResults")
                    {
                        for(let entry of args.songs)
                            console.log(entry.name);
                        for(let entry of args.albums)
                            console.log(entry.name);
                        for(let entry of args.artists)
                            console.log(entry.name);
                    }
                }
        """
        (foundartists, foundalbums, foundsongs) = self.mise.Find(searchstring)

        # prepare result processing
        artists = []
        albums  = []
        songs   = []
        artistcount = min(limit, len(foundartists))
        albumcount  = min(limit, len(foundalbums))
        songcount   = min(limit, len(foundsongs))

        # process foundartists
        for i in range(artistcount):
            artistid = foundartists[i][0]
            artist   = self.database.GetArtistById(artistid)

            entry = {}
            entry["artist"] = artist
            artists.append(entry)

        # process found albums
        for i in range(albumcount):
            albumid = foundalbums[i][0]
            album   = self.database.GetAlbumById(albumid)
            artist  = self.database.GetArtistById(album["artistid"])

            entry = {}
            entry["artist"] = artist
            entry["album"]  = album
            albums.append(entry)

        # process found songs
        for i in range(songcount):
            songid  = foundsongs[i][0]
            song    = self.database.GetSongById(songid)
            album   = self.database.GetAlbumById(song["albumid"])
            artist  = self.database.GetArtistById(song["artistid"])

            entry = {}
            entry["artist"] = artist
            entry["album"]  = album
            entry["song"]   = song
            songs.append(entry)

        results = {}
        results["artists"] = artists
        results["albums"]  = albums
        results["songs"]   = songs
        return results


    # THIS METHOD IS THREADSAFE
    def SetMPDState(self, mpdstate):
        """
        This Method can be used to set the  *playing*-state of MPD (Music Playing Daemon)

        The following arguments are possible:

            * ``"play"``: Set state to *playing*. If there are songs in the queue, MPD start streaming.
            * ``"pause"``: Set state to *pause*.
            * ``"playpause"``: Toggle between *playing* and *pause*

        Args:
            mpdstate (str): New playing-state for MPD. *mpdstate* must be one of the following strings: playpause, play or pause.

        Returns:
            ``None``

        Example:
            .. code-block:: javascript

                MusicDB_Call("SetMPDState", {mpdstate:"playpause"});

        """
        isplaying = mpd.GetPlayingState()

        if mpdstate == "playpause":
            if isplaying:
                mpd.Play(False)
                logging.debug("Setting Play-State to False")
            else:
                mpd.Play(True)
                logging.debug("Setting Play-State to True")
        elif mpdstate == "pause":
            mpd.Play(False)
        elif mpdstate == "play":
            mpd.Play(True)
        else:
            logging.warning("Unexpected mpdstate  \"%s\" will not be set!" % str(mpdstate))

        return None


    def PlayNextSong(self):
        """
        This method skips the current playing song.
        If there is no song that can be skipped, nothing will be done.

        When a song got skipped, its statistics for being skipped gets incremented.

        Returns:
            ``None``

        Example:
            .. code-block:: javascript

                MusicDB_Call("PlayNextSong");

        """
        # First, get the current song
        # BE CAREFUL! The structure of mpds song-infos are different from the one used in the database
        mpdsong = mpd.GetCurrentSong()
        if mpdsong and "file" in mpdsong:
            song    = self.database.GetSongByPath(mpdsong["file"])
            songid  = song["id"]
        else:
            logging.warning("Unexpected Behaviour: There is no current song in the MPD-Queue to skip. \033[1;30m(ignoring PlayNextSong command)")
            return None

        # Give MPD the command to play the next song
        success = mpd.PlayNextSong()

        # if skipping was successfull, update stats
        if success:
            self.UpdateSongStatistic(songid, "qskips", "inc")

        return None


    def AddSongToQueue(self, songid, position):
        """
        This method adds a new song to the queue of songs MPD (Music Playing Daemon) will play.

        The song gets address by its ID.
        The position can be ``"next"`` if the song shall be places behind the current playing song.
        So, the new added song will be played next.
        Alternative ``"last"`` can be used to place the song at the end of the queue.

        If a song got add, the *adds*-statistic value gets incremented.

        Args:
            songid (int): ID of the song that shall be added
            position (str): ``"next"`` or ``"last"`` - Determines where the song gets added

        Returns:
            ``None``

        Example:
            .. code-block:: javascript

                MusicDB_Call("AddSongToQueue", {songid:1000, position:"next"});

        """
        song = self.database.GetSongById(songid)
        if not song:
            return None

        success = mpd.AddSong(song["path"], position) # position: "last" or "next"
        if success:
            self.UpdateSongStatistic(songid, "qadds", "inc")
        return None


    def AddRandomSongToQueue(self, position):
        """
        Similar to :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.AddSongToQueue`.
        Instead of a specific song, a random song gets chosen by the randomizer.
        This is done using :meth:`mdbapi.randy.Randy.AddSong`.

        The randomizer also increments the *rndadds* statistics for the song that gets added to the queue.

        Args:
            position (str): ``"next"`` or ``"last"`` - Determines where the song gets added

        Returns:
            ``None``

        Example:
            .. code-block:: javascript

                MusicDB_Call("AddRandomSongToQueue", {position:"last"});

        """
        # Check if the Randy Interface was created. This is not done in the constructor!
        # The interface to Randy gets instatioated in the onWSConnect callback funktion.
        # This is save as long as this (AddRandomSongToQueue) method gets only called by the websocket interface!
        if self.randy:
            self.randy.AddSong(position)
        else:
            logging.warning("No Randy interface created. \033[0:33m(This may not be intentional!) \033[1;30m(Doing nothing)")
        return None


    def AddAlbumToQueue(self, albumid):
        """
        This method adds all songs of an album (from all CDs) at the end of the MPD queue.

        The *adds*-statistic gets **not** incremented when a whole album gets add to the queue.

        Args:
            albumid (int): ID of the album that shall be added

        Returns:
            ``None``

        Example:
            .. code-block:: javascript

                MusicDB_Call("AddAlbumToQueue", {albumid:23});

        """
        sortedcds = self.GetSortedAlbumCDs(albumid)
        for cd in sortedcds:
            for entry in cd:
                song = entry["song"]
                mpd.AddSong(song["path"], "last")
        return None
    
        
    def RemoveSongFromQueue(self, songid, position):
        """
        This method removes a song from MPDs queue.
        The position is the index of the song in the queue and must be an integer.

        The *removes*-statistic of this song gets incremented.

        Args:
            songid (int): The ID of the song that shall be removed
            position (int): Position of the song in the MPD queue

        Returns:
            ``None``

        Example:
            .. code-block:: javascript

                MusicDB_Call("RemoveSongFromQueue", {songid:1337, position:3});

        """
        success = mpd.RemoveSong(position)
        if success:
            self.UpdateSongStatistic(songid, "qremoves", "inc")
        return None
    
    
    def MoveSongInQueue(self, songid, srcpos, dstpos):
        """
        This is a direct interface to :meth:`mdbapi.mpd.MoveSong`.
        It moves a song from one position in the queue to another one.

        Args:
            songid (int): ID of the song that shall be removed.
            srcpos (int): Position of the song
            dstpos (int): The position the song shall be moved to

        Return:
            ``None``
        """
        mpd.MoveSong(srcpos, dstpos)
        return None


    def GetSongRelationship(self, songid):
        """
        This method returns the relationship of a song.
        It is a list of songs that were played before or after the song with song ID *songid*.

        The returned dictionary contains the same song ID given as argument to this method, and list of related songs.
        Each lists entry is a dictionary with the related song, album and artist album from the database.
        Furthermore the weight is given.
        The weight indicates how often the two songs were played together.

        Args:
            songid (int): ID so a song

        Returns:
            A list of related songs

        Example:
            
            .. code-block:: javascript

                MusicDB_Request("GetSongRelationship", "ShowRelations", {songid:songid});

                // …

                function onMusicDBMessage(fnc, sig, args, pass)
                {
                    if(fnc == "GetSongRelationship" && sig == "ShowRelations")
                    {
                        console.log("Songs related to the one with ID " + args.songid)
                        for(let entry of args.songs)
                            console.log("Song " + entry.song.name + " with weight " + entry.weight);
                    }
                }
        """
        # get raw relationship
        trackerdb = TrackerDatabase(self.cfg.tracker.dbpath)
        results   = trackerdb.GetRelations("song", songid)
        parentsid = songid  # store for return value

        # get all songs
        entries = []
        #for songid in songids:
        for result in results:
            entry = {}
            songid = result["id"]
            weight = result["weight"]
            song   = self.database.GetSongById(songid)
            entry["song"]    = song
            entry["weight"]  = weight
            entry["album"]   = self.database.GetAlbumById(song["albumid"])
            entry["artist"]  = self.database.GetArtistById(song["artistid"])

            entries.append(entry)

        packet = {}
        packet["songid"]  = parentsid
        packet["songs"]   = entries
        return packet 


    def GetSongLyrics(self, songid):
        lyrics = self.database.GetLyrics(songid)
        state  = self.database.GetSongById(songid)["lyricsstate"]
        result = {}
        result["songid"]        = songid
        result["lyrics"]        = lyrics
        result["lyricsstate"]   = state
        return result
    
    
    def GetLyricsCrawlerCache(self, songid):
        """
        This method returns all cached lyrics for a song.

        A dictionary with two entries gets returned, the *songid* is the same the argument is.
        The second key is *lyricscache* that holds the values from the lyrics cache.
        It is a list of dictionaries representing a lyric cache database entry. (See :doc:`/mdbapi/lycra` for details)
        If there are no cached lyrics, the *lyricscache* entry is ``None``.

        Args:
            songid (int): ID of the song that lyrics cache shall be returned

        Returns:
            The songid and a list of cached lyrics.
        """
        lycra = Lycra(self.cfg)
        cache = lycra.GetLyrics(songid)
        result = {}
        result["songid"]        = songid
        result["lyricscache"]   = cache
        return result


    # THIS METHOD MUST BE THREADSAFE!
    def RunLyricsCrawler(self, songid):
        """
        This method starts the process of crawling for lyrics. (See :doc:`/mdbapi/lycra` for details)

        After all available crawler run, the method returns the current lyrics cache.
        This is identical to :meth:`~lib.ws.mdbapi.MusicDBWebSocketInterface.GetLyricsCrawlerCache`.

        Args:
            songid (int): ID of the song that lyrics cache shall be returned

        Returns:
            The songid and a list of cached lyrics.
        """
        # Get names from separate database to be threadsafe
        musicdb = MusicDatabase(self.cfg.database.path)
        song   = musicdb.GetSongById(songid)
        album  = musicdb.GetAlbumById(song["albumid"])
        artist = musicdb.GetArtistById(song["artistid"])

        lycra = Lycra(self.cfg)
        retval= lycra.CrawlForLyrics(artist["name"], album["name"], song["name"], songid)
        cache = lycra.GetLyrics(songid)
        result = {}
        result["songid"]        = songid
        result["lyricscache"]   = cache
        return result


    def SetSongLyrics(self, songid, lyrics, state):
        try:
            self.database.SetLyrics(songid, lyrics, state)
        except ValueError as e:
            logging.warning("Setting Lyrics failed with error: %s", str(e))
        except Exception as e:
            logging.exception("Setting Lyrics failed with error: %s", str(e))
        return None 


    def SetAlbumColor(self, albumid, colorname, color):
        if not colorname in ["bgcolor", "fgcolor", "hlcolor"]:
            logging.warning("colorname must be bgcolor, fgcolor or hlcolor");
            return False

        try:
            self.database.SetArtworkColorByAlbumId(albumid, colorname, color)
        except ValueError as e:
            logging.warning("Update Album Color failed: %s", str(e))
            logging.warning(" For AlbumID %s, Colorname %s and Color %s", 
                    str(albumid),
                    str(colorname),
                    str(color))
        except Exception as e:
            logging.exception("Update Album Color failed: %s", str(e))
            logging.error(" For AlbumID %s, Colorname %s and Color %s", 
                    str(albumid),
                    str(colorname),
                    str(color))
            return False

        return True


    def SetAlbumTag(self, albumid, tagid):
        """
        Sets a tag for an album.
        This method sets the approval-level to 1 (Set by User) and confidence to 1.0 for this tag.
        So, this method can also be used to approve an AI set tag.

        If tagging is disabled nothing will be done. 

        Args:
            albumid (int): ID of the album
            tagid (int): ID of the tag

        Return:
            ``None``

        Example:
            .. code-block:: javascript

                MusicDB_Call("SetAlbumTag", {albumid:albumid, tagid:tagid});
        """
        if self.cfg.debug.disabletagging:
            logging.info("Changing tags disabled. \033[1;33m!!")
            return None

        self.database.SetTargetTag("album", albumid, tagid)
        return None


    def RemoveAlbumTag(self, albumid, tagid):
        """
        Removes a tag from an album

        If tagging is disabled nothing will be done. 

        Args:
            albumid (int): ID of the album
            tagid (int): ID of the tag

        Return:
            ``None``

        Example:
            .. code-block:: javascript

                MusicDB_Call("RemoveAlbumTag", {albumid:albumid, tagid:tagid});
        """
        if self.cfg.debug.disabletagging:
            logging.info("Changing tags disabled. \033[1;33m!!")
            return None

        self.database.RemoveTargetTag("album", albumid, tagid)
        return None


    def SetSongTag(self, songid, tagid):
        """
        Sets a tag for a song.
        This method sets the approval-level to 1 (Set by User) and confidence to 1.0 for this tag.
        So, this method can also be used to approve an AI set tag.

        If tagging is disabled nothing will be done. 

        After executing this method, the MusicDB server broadcasts the result of :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.GetSong`. (``method = "broadcast", fncname = "GetSong"``)
        So each client gets informed about the changes made.
        This is important to update the HUD if the song is currently playing.

        Args:
            songid (int): ID of the song
            tagid (int): ID of the tag

        Return:
            ``None``

        Examples:
            .. code-block:: javascript

                MusicDB_Call("SetSongTag", {songid:songid, tagid:tagid});

            .. code-block:: javascript

                MusicDB_Request("SetSongTag", "UpdateTagInput", {songid:songid, tagid:tagid}, {taginputid:taginputid});

                // …

                function onMusicDBMessage(fnc, sig, args, pass)
                {
                    if(fnc == "GetSong" && sig == "UpdateTagInput")
                    {
                        console.log("Updating " + pass.taginputid + " for song " + args.song.name);
                        Taginput_Update(pass.taginputid, args.tags);
                    }
                }
        """
        if self.cfg.debug.disabletagging:
            logging.info("Changing tags disabled. \033[1;33m!!")
            return None

        self.database.SetTargetTag("song", songid, tagid)
        return None


    def RemoveSongTag(self, songid, tagid):
        """
        Removes a tag from a song

        If tagging is disabled nothing will be done. 

        After executing this method, the MusicDB server broadcasts the result of :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.GetSong`. (``method = "broadcast", fncname = "GetSong"``)
        So each client gets informed about the changes made.
        This is important to update the HUD if the song is currently playing.

        Args:
            songid (int): ID of the song
            tagid (int): ID of the tag

        Return:
            ``None``

        Example:
            .. code-block:: javascript

                MusicDB_Call("RemoveSongTag", {songid:songid, tagid:tagid});
        """
        if self.cfg.debug.disabletagging:
            logging.info("Changing tags disabled. \033[1;33m!!")
            return None

        self.database.RemoveTargetTag("song", songid, tagid)
        return None


    def AddSubgenre(self, name, parentname):
        """
        This method creates a new subgenre.

        If tagging is disabled nothing will be done. 

        Args:
            name (str): Name of the new subgenre
            parentname (str): Name of the main genre
        """
        if self.cfg.debug.disabletagging:
            logging.info("Changing tags disabled. \033[1;33m!!")
            return None

        parenttag = self.database.GetTagByName(parentname, MusicDatabase.TAG_CLASS_GENRE)
        if not parenttag:
            logging.warning("There is no maingenre called \"%s\"! \033[1;30m(Adding subgenre \"%s\" canceld)", parentname, name)
            return None

        self.database.CreateTag(name, MusicDatabase.TAG_CLASS_SUBGENRE, parenttag["id"])
        return None


    def UpdateSongStatistic(self, songid, statistic, modifier):
        """
        When this method got called direct via the JavaScript API, the MusicDB server broadcasts the result of :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.GetSong`. (``method = "broadcast", fncname = "GetSong"``)
        So each client gets informed about the changes made.
        This is important to update the HUD if the song is currently playing.

        This method is a direct interface to :meth:`lib.db.musicdb.MusicDatabase.UpdateSongStatistic`. See the related documentation for more details.
        """
        if self.cfg.debug.disablestats:
            logging.info("Updating song statistics disabled. \033[1;33m!!")
            return None

        try:
            self.database.UpdateSongStatistic(songid, statistic, modifier)
        except ValueError as e:
            logging.warning("Updating song statistics failed with error: %s!", str(e))
        except Exception as e:
            logging.exception("Updating song statistics failed with error: %s!", str(e))

        return None


    def CutSongRelationship(self, songid, relatedsongid):
        """
        This method removes the relation between two songs.

        After executing this method, the MusicDB server broadcasts the result of :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.GetSongRelationship`. (``method = "broadcast", fncname = "GetSongRelationship"``)
        So each client gets informed about the changes made.

        Args:
            songid (int): ID of one song
            relatedsongid (int): ID of the related song
        """
        if self.cfg.debug.disabletracker:
            logging.info("Updating tracker disabled. \033[1;33m!!")
            return None

        try:
            trackerdb = TrackerDatabase(self.cfg.tracker.dbpath)
            trackerdb.RemoveSongRelations(self.database, songid, relatedsongid)
        except Exception as e:
            logging.warning("Removing song relations failed with error: %s", str(e))
        return None



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

