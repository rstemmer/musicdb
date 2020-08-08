# MusicDB,  a music manager with web-bases UI that focus on music.
# Copyright (C) 2017-2020  Ralf Stemmer <ralf.stemmer@gmx.net>
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
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.GetArtistsWithVideos`
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
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.AddSongToQueue`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.AddRandomSongToQueue`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.RemoveSongFromQueue`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.MoveSongInQueue`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.GetSongRelationship`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.UpdateSongStatistic`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.CutSongRelationship`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.Find`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.PlayNextSong`

Videos
^^^^^^
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.GetVideos`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.GetVideo`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.AddVideoToQueue`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.RemoveVideoFromQueue`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.MoveVideoInQueue`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.UpdateVideoStatistic`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.PlayNextVideo`

Queue
^^^^^
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.GetSongQueue`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.GetVideoQueue`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.AddSongToQueue`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.AddRandomSongToQueue`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.AddVideoToQueue`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.AddAlbumToQueue`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.RemoveSongFromQueue`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.RemoveVideoFromQueue`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.MoveSongInQueue`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.MoveVideoInQueue`

Tag related
^^^^^^^^^^^
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.GetTags`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.GetSongTags`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.GetAlbumTags`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.GetVideoTags`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.SetAlbumTag`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.RemoveAlbumTag`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.SetSongTag`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.RemoveSongTag`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.SetVideoTag`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.RemoveVideoTag`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.AddSubgenre`

Lyrics
^^^^^^
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.GetSongLyrics`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.GetLyricsCrawlerCache`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.RunLyricsCrawler`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.SetSongLyrics`

Other
^^^^^
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.GetStreamState`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.GetAudioStreamState`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.GetVideoStreamState`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.SetStreamState`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.PlayNextSong`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.PlayNextVideo`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.SetMDBState`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.GetMDBState`
* :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.GetTables`

"""
import random
from lib.db.musicdb     import *
from lib.db.trackerdb   import TrackerDatabase
from lib.db.musicdb     import MusicDatabase
from lib.cfg.musicdb    import MusicDBConfig
from lib.cfg.mdbstate   import MDBState
from lib.filesystem     import Filesystem
import os
from mdbapi.lycra       import Lycra
from mdbapi.database    import MusicDBDatabase
from mdbapi.mise        import MusicDBMicroSearchEngine
from mdbapi.tags        import MusicDBTags
from mdbapi.audiostream import AudioStreamManager
from mdbapi.videostream import VideoStreamManager
from mdbapi.songqueue   import SongQueue
from mdbapi.videoqueue  import VideoQueue
import logging
from threading          import Thread
import traceback

class MusicDBWebSocketInterface(object):

    def __init__(self):
        # Import global variables from the server
        from mdbapi.server import database, mise, cfg
        self.database   = database
        self.mise       = mise
        self.cfg        = cfg

        # The autobahn framework silently hides all exceptions - that sucks
        # So all possible exceptions must be caught here, so that they can be made visible.
        try:
            self.fs         = Filesystem(self.cfg.music.path)
            self.tags       = MusicDBTags(self.cfg, self.database)
            self.mdbstate   = MDBState(self.cfg.server.statedir, self.database)
            self.audiostream= AudioStreamManager(self.cfg, self.database)
            self.videostream= VideoStreamManager(self.cfg, self.database)
            self.songqueue  = SongQueue(self.cfg, self.database)
            self.videoqueue = VideoQueue(self.cfg, self.database)
        except Exception as e:
            logging.exception(e)
            raise e


    def onWSConnect(self):
        self.audiostream.RegisterCallback(self.onAudioStreamEvent)
        self.videostream.RegisterCallback(self.onVideoStreamEvent)
        self.songqueue.RegisterCallback(self.onSongQueueEvent)
        self.videoqueue.RegisterCallback(self.onVideoQueueEvent)
        return None
        

    def onWSDisconnect(self, wasClean, code, reason):
        self.audiostream.RemoveCallback(self.onAudioStreamEvent)
        self.videostream.RemoveCallback(self.onVideoStreamEvent)
        self.songqueue.RemoveCallback(self.onSongQueueEvent)
        self.videoqueue.RemoveCallback(self.onVideoQueueEvent)
        return None


    def onAudioStreamEvent(self, event, data):
        # This function is called from a different thread. Therefore NO sqlite3-access is allowed.
        # So there will be just a notification so that the clients can request GetAudioStreamState.
        response    = {}
        response["method"]      = "notification"
        response["fncname"]     = "MusicDB:AudioStream"
        response["fncsig"]      = "on"+event
        response["arguments"]   = data
        response["pass"]        = None
        success = self.SendPacket(response)
        return success

    def onVideoStreamEvent(self, event, data):
        # This function is called from a different thread. Therefore NO sqlite3-access is allowed.
        # So there will be just a notification so that the clients can request GetVideoStreamState.
        response    = {}
        response["method"]      = "notification"
        response["fncname"]     = "MusicDB:VideoStream"
        response["fncsig"]      = "on"+event
        response["arguments"]   = data
        response["pass"]        = None
        success = self.SendPacket(response)
        return success

    def onSongQueueEvent(self, event, data):
        # This function is called from a different thread. Therefore NO sqlite3-access is allowed.
        # So there will be just a notification so that the clients can request related functions.
        response    = {}
        response["method"]      = "notification"
        response["fncname"]     = "MusicDB:SongQueue"
        response["fncsig"]      = "on"+event
        response["arguments"]   = data
        response["pass"]        = None
        success = self.SendPacket(response)
        return success

    def onVideoQueueEvent(self, event, data):
        # This function is called from a different thread. Therefore NO sqlite3-access is allowed.
        # So there will be just a notification so that the clients can request related functions.
        response    = {}
        response["method"]      = "notification"
        response["fncname"]     = "MusicDB:VideoQueue"
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
        elif fncname == "GetFilteredArtistsWithVideos":
            retval = self.GetFilteredArtistsWithVideos()
        elif fncname == "GetAlbums":
            retval = self.GetAlbums(args["artistid"], args["applyfilter"])
        elif fncname == "GetAlbum":
            retval = self.GetAlbum(args["albumid"])
        elif fncname == "GetVideos":
            retval = self.GetVideos(args["artistid"])
        elif fncname == "GetVideo":
            retval = self.GetVideo(args["videoid"])
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
        elif fncname == "GetTables":
            retval = self.GetTables(args["tables"])
        elif fncname == "GetMDBState":
            retval = self.GetMDBState()
        elif fncname == "GetStreamState":
            logging.warning("GetStreamState is deprecated! Use GetAudioStreamState instead. \033[1;30m(Calling GetAudioStreamState)")
            retval = self.GetAudioStreamState()
        elif fncname == "GetAudioStreamState":
            retval = self.GetAudioStreamState()
        elif fncname == "GetVideoStreamState":
            retval = self.GetVideoStreamState()
        elif fncname == "GetSongQueue":
            retval = self.GetSongQueue()
        elif fncname == "GetVideoQueue":
            retval = self.GetVideoQueue()
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
        elif fncname == "SetVideoTag":
            retval = self.SetVideoTag(args["videoid"], args["tagid"])
            retval = self.GetVideo(args["videoid"])
            method = "broadcast"
            fncname= "GetVideo"
        elif fncname == "RemoveVideoTag":
            retval = self.RemoveVideoTag(args["videoid"], args["tagid"])
            retval = self.GetVideo(args["videoid"])
            method = "broadcast"
            fncname= "GetVideo"
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
        elif fncname == "UpdateVideoStatistic":
            retval = self.UpdateVideoStatistic(args["videoid"], args["statistic"], args["modifier"])
            retval = self.GetVideo(args["videoid"])
            method = "broadcast"
            fncname= "GetVideo"
        elif fncname == "AddSongToQueue":
            retval = self.AddSongToQueue(args["songid"], args["position"])
        elif fncname == "AddVideoToQueue":
            retval = self.AddVideoToQueue(args["videoid"], args["position"])
        elif fncname == "AddAlbumToQueue":
            retval = self.AddAlbumToQueue(args["albumid"])
        elif fncname == "AddRandomSongToQueue":
            if "albumid" in args:
                retval = self.AddRandomSongToQueue(args["position"], args["albumid"])
            else:
                retval = self.AddRandomSongToQueue(args["position"])
        elif fncname == "MoveSongInQueue":
            retval = self.MoveSongInQueue(args["entryid"], args["afterid"])
        elif fncname == "MoveVideoInQueue":
            retval = self.MoveVideoInQueue(args["entryid"], args["afterid"])
        elif fncname == "RemoveSongFromQueue":
            retval = self.RemoveSongFromQueue(args["entryid"])
        elif fncname == "RemoveVideoFromQueue":
            retval = self.RemoveVideoFromQueue(args["entryid"])
        elif fncname == "CutSongRelationship":
            retval = self.CutSongRelationship(args["songid"], args["relatedsongid"])
            if method == "request":
                retval = self.GetSongRelationship(args["songid"])
                fncname= "GetSongRelationship"
        elif fncname == "SetStreamState":
            retval = self.SetStreamState(args["state"])
        elif fncname == "PlayNextSong":
            retval = self.PlayNextSong()
        elif fncname == "PlayNextVideo":
            retval = self.PlayNextVideo()
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
            apikey      = packet["key"]
        except:
            logging.warning("Malformed request packet received! \033[0;33m(Call will be ignored)")
            logging.debug("Packet: %s", str(packet))
            return False

        logging.debug("method: %s, fncname: \033[1;37m%s\033[1;30m, fncsig: %s, arguments: %s, pass: %s", 
                str(method),str(fncname),str(fncsig),str(arguments),str(passthrough))

        if apikey != self.cfg.websocket.apikey:
            logging.error("Invalid WebSocket API Key! \033[1;30m(Check your configuration. If they are correct check your HTTP servers security!)\033[0m\nreceived: %s\nexpected: %s", str(apikey), str(self.cfg.websocket.apikey))
            return False

        if not method in ["call", "request", "broadcast"]:
            logging.warning("Unknown call-method: %s! \033[0;33m(Call will be ignored)", str(method))
            return False

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


    def GetFilteredArtistsWithVideos(self):
        """
        This method returns a list of artists and their videos.
        The genre-filter gets applied to the videos.
        Each entry in this list contains the following two elements:

            * **artist:** An entry like the list entries of :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.GetArtists`
            * **videos:** A list of videos

        Artists without videos or videos that got filters out will not appear in the list.

            
        Returns:
            A list of artists and their videos

        Example:
            .. code-block:: javascript

                MusicDB_Request("GetFilteredArtistsWithVideos", "ShowArtists");

                // …

                function onMusicDBMessage(fnc, sig, args, pass)
                {
                    if(fnc == "GetFilteredArtistsWithVideos" && sig == "ShowArtists")
                    {
                        for(let artist of args)
                        {
                            console.log("Artist: " + artist.name);
                            for(let video of artist.videos)
                                console.log(" -> " + video.name);
                        }
                    }
                }
        """
        # Get artist-list
        artists = self.GetArtists()

        # Get videos for each artist
        artistlist = []
        for artist in artists:
            videos = self.GetVideos(artist["id"], applyfilter=True)

            # filter artists with no relevant videos
            if videos == []:
                continue

            entry = {}
            entry["artist"] = artist
            entry["videos"] = videos
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


    def GetVideos(self, artistid, applyfilter=False):
        """
        GetVideos returns a list of videos of an artist.
        The list is sorted by release date of the video, starting with the earliest one.
        Each entry in the list has the following two elements:

            * **video:** A video entry from the database.
            * **tags:** The returned tag entry by :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.GetVideoTags`

        The filter gets applied to only the *genre* tags.

        Args:
            artistid (int): ID of the artist whose videos shall be returned
            applyfilter (bool): Default value is ``False``

        Returns:
            A list of videos and their tags

        Example:
            .. code-block:: javascript

                MusicDB_Request("GetVideos", "ShowVideos", {artistid:artistid, applyfilter:false});

                // …

                function onMusicDBMessage(fnc, sig, args, pass)
                {
                    if(fnc == "GetVideos" && sig == "ShowVideos")
                    {
                        for(let listentry of args)
                        {
                            let video, tags;
                            video = listentry.video;
                            tags  = listentry.tags;

                            console.log("Tags of " + video.name + ":");
                            console.log(tags);
                        }
                    }
                }
        """
        # Get videos by this artist
        videos = self.database.GetVideosByArtistId(artistid)

        # sort videos for release year
        videos = sorted(videos, key = lambda k: k["release"])

        if applyfilter:
            filterset = set(self.mdbstate.GetFilterList())

        # assign tags to videos
        videolist = []
        for video in videos:
            tags   = self.GetVideoTags(video["id"])
            genres = tags["genres"]

            # if no tags are available, show the album!
            if applyfilter and genres:
                genreset = { genre["name"] for genre in genres }

                # do not continue with this album,
                # if there is no unionset of genres
                if not filterset & genreset:
                    continue

            entry = {}
            entry["video"]   = video
            entry["tags"]    = tags
            videolist.append(entry)

        return videolist


    def GetVideo(self, videoid):
        """
        This method returns a video entry from the Music Database.

        GetVideo returns a dictionary with the following keys:

            * **artist:** A Database entry of the artist of the video
            * **album:** The database entry of the album of the video, if known. Can be ``None``.
            * **song:** The database entry of the song related to the video, if known. Can be ``None``.
            * **video:** The video with the ``videoid`` of the request
            * **tags:** A list of tags as returned by :meth:`~GetVideoTags`

        Args:
            videoid (int): The ID of that video that shall be returned

        Returns:
            A dictionary with information of the requested video

        Example:
            .. code-block:: javascript

                MusicDB_Request("GetVideo", "ShowVideo", {videoid:1000});

                // …

                function onMusicDBMessage(fnc, sig, args, pass)
                {
                    if(fnc == "GetVideo" && sig == "ShowVideo")
                    {
                        console.log("Artist: " + args.artist.name);
                        console.log("Video:  " + args.video.name);
                    }
                }
        """
        video   = self.database.GetVideoById(videoid)
        artist  = self.database.GetArtistById(video["artistid"])
        tags    = self.GetVideoTags(videoid)

        if video["albumid"]:
            album = self.database.GetAlbumById(video["albumid"])
        else:
            album = None

        if video["songid"]:
            song = self.database.GetSongById(video["songid"])
        else:
            song = None

        # send the data to the client
        retval = {}
        retval["artist"]  = artist
        retval["album"]   = album
        retval["song"]    = song
        retval["video"]   = video
        retval["tags"]    = tags
        return retval


    def UpdateVideoStatistic(self, videoid, statistic, modifier):
        """
        This video allows setting some statistics and properties for a video.
        When this method got called direct via the JavaScript API, the MusicDB server broadcasts the result of :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.GetVideo`. (``method = "broadcast", fncname = "GetSong"``)
        So each client gets informed about the changes made and can synchronize itself.

        This method is a direct interface to :meth:`lib.db.musicdb.MusicDatabase.UpdateVideoStatistic`. See the related documentation for more details.
        """
        if self.cfg.debug.disablestats:
            logging.info("Updating video statistics disabled. \033[1;33m!!")
            return None

        try:
            self.database.UpdateVideoStatistic(videoid, statistic, modifier)
        except ValueError as e:
            logging.warning("Updating video statistics failed with error: %s!", str(e))
        except Exception as e:
            logging.exception("Updating video statistics failed with error: %s!", str(e))

        return None


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
        Similar to :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.GetSongTags`.
        This method returns the tags for an Album.
        """
        tags = self.database.GetTargetTags("album", albumid)
        genres, subgenres, moods = self.database.SplitTagsByClass(tags)
        tags = {}
        tags["albumid"]   = albumid  # this is necessary to not loose context
        tags["genres"]    = genres
        tags["subgenres"] = subgenres
        tags["moods"]     = moods
        return tags


    def GetVideoTags(self, videoid):
        """
        Similar to :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.GetSongTags`.
        This method returns the tags for a Video.
        """
        tags = self.database.GetTargetTags("video", videoid)
        genres, subgenres, moods = self.database.SplitTagsByClass(tags)
        tags = {}
        tags["videoid"]   = videoid  # this is necessary to not loose context
        tags["genres"]    = genres
        tags["subgenres"] = subgenres
        tags["moods"]     = moods
        return tags


    def GetTables(self, tablenames):
        """
        Returns a dictionary that contains for each requested table a key.
        Behind this key is a list of dictionaries representing the rows of the requested table.

        If ``tablenames`` is ``None``, the result is an empty dictionary.

        The following list shows all valid names and links to the database calls that returned lists will be returned by this method.:

            * ``"songs"``: :meth:`lib.db.musicdb.MusicDatabase.GetAllSongs`
            * ``"albums"``: :meth:`lib.db.musicdb.MusicDatabase.GetAllAlbums`
            * ``"artists"``: :meth:`lib.db.musicdb.MusicDatabase.GetAllArtists`
            * ``"tags"``: :meth:`lib.db.musicdb.MusicDatabase.GetAllTags`

        Args:
            tablenames (list of strings): A list of table names.

        Returns:
            A dict of lists of database entries

        Example:
            .. code-block:: javascript

                MusicDB_Request("GetTables", "ShowTables", {position:["songs", "albums"]});

                // …

                function onMusicDBMessage(fnc, sig, args, pass)
                {
                    if(fnc == "GetTables" && sig == "ShowTables")
                    {
                        console.log("Tags of the song with the ID " + args.songid);
                        for(let song of args.songs)
                            console.log(song.name);
                        for(let album of args.albumss)
                            console.log(album.name);
                    }
                }
        """
        retval = {}
        if "songs" in tablenames:
            retval["songs"] = self.database.GetAllSongs()
        if "albums" in tablenames:
            retval["albums"] = self.database.GetAllAlbums()
        if "artists" in tablenames:
            retval["artists"] = self.database.GetAllArtists()
        if "tags" in tablenames:
            retval["tags"] = self.database.GetAllTags()
        return retval


    def SetMDBState(self, category, name, value):
        """
        This method sets the global state of MDB clients

        If the state is not available in the global state settings, it will be created.

        When the *category* is ``"albumfilter"``,
        then *name* must be a Genre-Name and *value* is ``True`` or ``False``.
        If a genre gets set to true, all albums for that genre are included in the list of returned albums by methods that use the filter.

        After executing this method, the MusicDB server broadcasts the result of :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.GetMDBState`. (``method = "broadcast", fncname = "GetMDBState"``)
        So each client gets informed about the new state.

        The category must be ``"albumfilter"`` or ``"MusicDB"`` with name ``"uimode"``!
        To set the album filter, :meth:`~lib.cfg.config.Config.Set` is used.
        For setting the UI mode, :meth:`~lib.cfg.mdbstate.MDBState.SetUIMode` is called. Details of valid modes are listed there as well.

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
        if category == "albumfilter":
            self.mdbstate.Set(category, name, value)
        elif category == "MusicDB" and name == "uimode":
            try:
                self.mdbstate.SetUIMode(value)
            except Exception as e:
                logging.warning("Setting MusicDB UI Mode failed with errror \"%s\"", str(e))
                pass

        return None


    def GetMDBState(self):
        """
        This method returns the current global state of the MusicDB WebUIs

        Currently, the only state existing is the list of selected genres.

        The state is a dictionary with the following information:

            * **albumfilter:** a list of tag-names of class Genre
            * **MusicDB:**
                * *uimode*: Defines if UI is in ``"audio"`` or ``"video"`` mode

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
                        console.log(args.MusicDB.uimode);

                        let activetags;
                        activetags = args.albumfilter;
                        for(let genrename of activetags)
                            console.log(genrename);
                    }
                }
        """
        albumfilter = self.mdbstate.GetFilterList()

        state = {}
        state["albumfilter"] = albumfilter
        state["MusicDB"] = {}
        state["MusicDB"]["uimode"] = self.mdbstate.GetUIMode()
        return state


    def GetAudioStreamState(self):
        """
        This method returns the state of the Streaming Thread. (See :doc:`/mdbapi/audiostream`)

        The state is a dictionary that has always the following information:

            * **isconnected:** ``True`` if MusicDB is connected to Icecast, otherwise ``False``
            * **isplaying:** ``True`` if the Streaming Thread is in *playing*-mode, otherwise ``False``
            * **hasqueue:** ``True`` when there is at least one song in the queue. When ``False``, the following song information are *not* included!

        In case there is a at least one song in the queue, this current streamed song gets returned with the following information:

            * **song:** The song entry from the database for the song that is currently playing
            * **album:** The related album entry from the database
            * **artist:** The related artist entry from the database
            * **songtags:** a list of tags as returned by :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.GetSongTags`
            * **albumtags:** a list of tags as returned by :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.GetAlbumTags`

        Returns:
            The current state of the streaming thread

        Example:
            .. code-block:: javascript

                MusicDB_Request("GetAudioStreamState", "ShowStreamState");

                // …

                function onMusicDBMessage(fnc, sig, args, pass)
                {
                    if(fnc == "GetAudioStreamState" && sig == "ShowStreamtate")
                    {
                        if(args.isconnected == true)
                        {
                            console.log("Connection to Icecast established");
                        }
                        if(args.hasqueue == true)
                        {
                            console.log("Current playing song: " + args.song.name);
                        }
                    }
                }
        """
        state = {}

        streamstate = self.audiostream.GetStreamState()
        queueentry  = self.songqueue.CurrentSong()
        if queueentry:
            songid  = queueentry["songid"]
        else:
            songid  = None

        state["isconnected"] = streamstate["isconnected"]
        state["isplaying"]   = streamstate["isplaying"]

        # if no file is given, the queue is empty - or "there is no queue"
        if songid:
            song      = self.database.GetSongById(songid)
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

        return state


    def GetVideoStreamState(self):
        """
        This method returns the state of the Video Streaming Thread. (See :doc:`/mdbapi/videostream`)

        The state is a dictionary that has always the following information:

            * **isstreaming:** ``True`` if MusicDB manages the video stream
            * **isplaying:** ``True`` if the Streaming Thread is in *playing*-mode, otherwise ``False``
            * **hasqueue:** ``True`` when there is at least one song in the queue. When ``False``, the following song information are *not* included!
            * **currententry:** (string) UUID of the current entry in the queue - the video that gets streamed, or ``null``.

        In case there is a at least one song in the queue, this current streamed song gets returned with the following information:

            * **video:** The video entry from the database for the video that is currently playing
            * **videotags:** a list of tags as returned by :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.GetVideoTags`

        Returns:
            The current state of the streaming thread

        Example:
            .. code-block:: javascript

                MusicDB_Request("GetVideoStreamState", "ShowStreamState");

                // …

                function onMusicDBMessage(fnc, sig, args, pass)
                {
                    if(fnc == "GetVideoStreamState" && sig == "ShowStreamtate")
                    {
                        if(args.hasqueue == true)
                        {
                            console.log("Current playing video: " + args.video.name);
                        }
                    }
                }
        """
        state = {}

        streamstate = self.videostream.GetStreamState()
        queueentry  = self.videoqueue.CurrentVideo()
        if queueentry:
            videoid  = queueentry["videoid"]
        else:
            videoid  = None

        state["isstreaming"]  = streamstate["isstreaming"]
        state["isplaying"]    = streamstate["isplaying"]
        if streamstate["currententry"]:
            state["currententry"] = str(streamstate["currententry"])
        else:
            state["currententry"] = None

        # if no file is given, the queue is empty - or "there is no queue"
        if videoid:
            video     = self.database.GetVideoById(videoid)
            videotags = self.GetVideoTags(video["id"])

            state["video"]      = video
            state["vudeitags"]  = videotags
            state["hasqueue"]   = True
        else:
            state["hasqueue"]   = False

        return state


    def GetSongQueue(self):
        """
        This method returns a list of songs, albums and artists for each song in the song queue.
        If there are no songs in the queue, an empty list gets returned.

        Each entry of the list contains the following information:

            * **entryid:** A unique ID to identify the entry in the queue (as string because it is a 128 integer that blows JavaScripts mind)
            * **israndom:** A boolean value set to ``true`` when the song got added randomly and not explicitly by the user
            * **song:** The song entry from the database
            * **album:** The related album entry from the database
            * **artist:** The related artist entry from the database

        Returns:
            A list of song, album and artist information for each song in the song queue

        Example:
            .. code-block:: javascript

                MusicDB_Request("GetSongQueue", "ShowSongQueue");

                // …

                function onMusicDBMessage(fnc, sig, args, pass)
                {
                    if(fnc == "GetSongQueue" && sig == "ShowSongQueue")
                    {
                        for(let entry of args)
                        {
                            console.log(entry.song.name + " by " + entry.artist.name);
                        }
                    }
                }
        """
        entries = self.songqueue.GetQueue()

        # return empty list if there is no queue
        if not entries:
            return []

        queue = []
        for queueentry in entries:
            song    = self.database.GetSongById(queueentry["songid"])
            album   = self.database.GetAlbumById(song["albumid"])
            artist  = self.database.GetArtistById(song["artistid"])

            entry = {}
            entry["entryid"]  = str(queueentry["entryid"])
            entry["israndom"] = bool(queueentry["israndom"])
            entry["song"]     = song
            entry["album"]    = album
            entry["artist"]   = artist

            queue.append(entry)

        return queue


    def GetVideoQueue(self):
        """
        This method returns a list of videos, albums and artists for each video in the video queue.
        If there are no videos in the queue, an empty list gets returned.
        The album or artist can be ``null`` if there is no associated to the video.

        Each entry of the list contains the following information:

            * **entryid:** A unique ID to identify the entry in the queue (as string because it is a 128 integer that blows JavaScripts mind)
            * **israndom:** A boolean value set to ``true`` when the video got added randomly and not explicitly by the user
            * **video:** The video entry from the database
            * **album:** The related album entry from the database or ``null``.
            * **artist:** The related artist entry from the database or ``null``.

        Returns:
            A list of video, album and artist information for each video in the video queue

        Example:
            .. code-block:: javascript

                MusicDB_Request("GetVideoQueue", "ShowVideoQueue");

                // …

                function onMusicDBMessage(fnc, sig, args, pass)
                {
                    if(fnc == "GetVideoQueue" && sig == "ShowVideoQueue")
                    {
                        for(let entry of args)
                        {
                            console.log(entry.video.name + " by " + entry.artist.name);
                        }
                    }
                }
        """
        entries = self.videoqueue.GetQueue()

        # return empty list if there is no queue
        if not entries:
            return []

        queue = []
        for queueentry in entries:

            video = self.database.GetVideoById(queueentry["videoid"])

            if video["albumid"] != None:
                album  = self.database.GetAlbumById(video["albumid"])
            else:
                album  = None

            if video["artistid"] != None:
                artist = self.database.GetArtistById(video["artistid"])
            else:
                artist = None

            entry = {}
            entry["entryid"]  = str(queueentry["entryid"])
            entry["israndom"] = bool(queueentry["israndom"])
            entry["video"]    = video
            entry["album"]    = album
            entry["artist"]   = artist

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
                * **albums:** A list of all albums by this artist, ordered by release year

        The search does not look for exact matching.
        It looks for most likeliness.
        So, typos or all lowercase input are no problem.

        The list of songs will not contain any hated or disabled songs.

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


        # process found artists
        artists     = []
        artistcount = min(limit, len(foundartists))
        for i in range(artistcount):
            artistid = foundartists[i][0]
            artist   = self.database.GetArtistById(artistid)

            # Get albums by this artist and sort for release year
            albums = self.database.GetAlbumsByArtistId(artistid)
            albums = sorted(albums, key = lambda k: k["release"])

            entry = {}
            entry["artist"] = artist
            entry["albums"] = albums
            artists.append(entry)

        # process found albums
        albums     = []
        albumcount = min(limit, len(foundalbums))
        for i in range(albumcount):
            albumid = foundalbums[i][0]
            album   = self.database.GetAlbumById(albumid)
            artist  = self.database.GetArtistById(album["artistid"])

            entry = {}
            entry["artist"] = artist
            entry["album"]  = album
            albums.append(entry)

        # process found songs
        songs     = []
        songcount = len(foundsongs) # Do not limit the songlist length at this point. There may be songs removed
        for i in range(songcount):
            songid  = foundsongs[i][0]
            song    = self.database.GetSongById(songid)
            if song["disabled"] or song["favorite"] == -1:
                continue    # Skip hated and disabled songs
            album   = self.database.GetAlbumById(song["albumid"])
            artist  = self.database.GetArtistById(song["artistid"])

            entry = {}
            entry["artist"] = artist
            entry["album"]  = album
            entry["song"]   = song
            songs.append(entry)
            if len(songs) >= limit:
                break

        results = {}
        results["artists"] = artists
        results["albums"]  = albums
        results["songs"]   = songs
        return results


    def SetStreamState(self, state):
        """
        This method can be used to set the  *playing*-state of the audio stream (see :doc:`/mdbapi/audiostream`)
        and the video stream (see :doc:`/mdbapi/videostream`)

        The following arguments are possible:

            * ``"play"``: Set state to *playing*. If there are songs in the queue, MusicDB starts streaming.
            * ``"pause"``: Set state to *pause*.
            * ``"playpause"``: Toggle between *playing* and *pause*

        Args:
            state (str): New playing-state for the audio streaming thread. *state* must be one of the following strings: ``"playpause"``, ``"play"`` or ``"pause"``.

        Returns:
            ``None``

        Example:
            .. code-block:: javascript

                MusicDB_Call("SetStreamState", {state:"playpause"});

        """
        currentstate = self.audiostream.GetStreamState()
        isplaying    = currentstate["isplaying"]

        if state == "playpause":
            if isplaying:
                self.audiostream.Play(False)
            else:
                self.audiostream.Play(True)
        elif state == "pause":
            self.audiostream.Play(False)
        elif state == "play":
            self.audiostream.Play(True)
        else:
            logging.warning("Unexpected state \"%s\" will not be set! \033[1;30m(State must be play, pause or playpause)", str(state))

        return None


    def PlayNextSong(self):
        """
        This method skips the current playing song.
        If there is no song that can be skipped, the Song Queue or Streaming Thread will handle this properly.

        Returns:
            ``None``

        Example:
            .. code-block:: javascript

                MusicDB_Call("PlayNextSong");

        """
        self.audiostream.PlayNextSong()
        return None


    def PlayNextVideo(self):
        """
        This method skips the current playing video.
        If there is no video that can be skipped, the Video Queue or Streaming Thread will handle this properly.

        Returns:
            ``None``

        Example:
            .. code-block:: javascript

                MusicDB_Call("PlayNextVideo");

        """
        self.videostream.PlayNextSong()
        return None


    def AddSongToQueue(self, songid, position):
        """
        This method adds a new song to the queue of songs that will be streamed.

        The song gets address by its ID.
        The position can be ``"next"`` if the song shall be places behind the current playing song.
        So, the new added song will be played next.
        Alternative ``"last"`` can be used to place the song at the end of the queue.

        Args:
            songid (int): ID of the song that shall be added
            position (str): ``"next"`` or ``"last"`` - Determines where the song gets added

        Returns:
            ``None``

        Example:
            .. code-block:: javascript

                MusicDB_Call("AddSongToQueue", {songid:1000, position:"next"});

        """
        # Check if the song ID is valid
        song = self.database.GetSongById(songid)
        if not song:
            logging.warning("Invalid song ID: %s! \033[1;30m(ignoring AddSongToQueue command)", str(songid))
            return None

        if position not in ["next", "last"]:
            logging.warning("Position must have the value \"next\" or \"last\". Given was \"%s\". \033[1;30m(Doing nothing)", str(position))
            return None

        # Add song to the queue and update statistics
        self.songqueue.AddSong(songid, position)
        return None


    def AddRandomSongToQueue(self, position, albumid=None):
        """
        Similar to :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.AddSongToQueue`.
        Instead of a specific song, a random song gets chosen by the random-song manager *Randy* (See :doc:`/mdbapi/randy`).
        This is done using the :meth:`mdbapi.randy.Randy.GetSong` method.

        If an album ID is given, the new song will be added from that album
        using :meth:`mdbapi.randy.Randy.GetSongFromAlbum`.

        Args:
            position (str): ``"next"`` or ``"last"`` - Determines where the song gets added
            albumid (int): Optional album ID from that the song shall be

        Returns:
            ``None``

        Example:
            .. code-block:: javascript

                MusicDB_Call("AddRandomSongToQueue", {position:"last"});
                MusicDB_Call("AddRandomSongToQueue", {albumid:"42", position:"next"});

        """
        if position not in ["next", "last"]:
            logging.warning("Position must have the value \"next\" or \"last\". Given was \"%s\". \033[1;30m(Doing nothing)", str(position))
            return None

        if albumid != None:
            albumid = int(albumid)
        self.songqueue.AddRandomSong(position, albumid)
        return None


    def AddVideoToQueue(self, videoid, position):
        """
        This method adds a new video to the queue of videos that will be played.

        The video gets address by its ID.
        The position can be ``"next"`` if the video shall be places behind the current playing video.
        So, the new added video will be played next.
        Alternative ``"last"`` can be used to place the video at the end of the queue.

        Args:
            videoid (int): ID of the video that shall be added
            position (str): ``"next"`` or ``"last"`` - Determines where the video gets added

        Returns:
            ``None``

        Example:
            .. code-block:: javascript

                MusicDB_Call("AddVideoToQueue", {videoid:1000, position:"last"});

        """
        # Check if the video ID is valid
        video = self.database.GetVideoById(videoid)
        if not video:
            logging.warning("Invalid video ID: %s! \033[1;30m(ignoring AddVideoToQueue command)", str(videoid))
            return None

        if position not in ["next", "last"]:
            logging.warning("Position must have the value \"next\" or \"last\". Given was \"%s\". \033[1;30m(Doing nothing)", str(position))
            return None

        # Add video to the queue and update statistics
        self.videoqueue.AddVideo(videoid, position)
        return None


    def AddAlbumToQueue(self, albumid):
        """
        This method adds all songs of an album (from all CDs) at the end of the queue.

        The *adds*-statistic gets **not** incremented when a whole album gets add to the queue.

        If a song is flagged as "hated" or disabled, than it gets discarded.

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
                if song["disabled"] == 1 or song["favorite"] == -1:
                    continue
                self.songqueue.AddSong(song["id"])
        return None
    
        
    def RemoveSongFromQueue(self, entryid):
        """
        This method removes a song from song queue.
        The song gets identified by the entry ID of the queue entry.

        Args:
            entryid (str) Queue entry ID of the song

        Returns:
            ``None``

        Example:
            .. code-block:: javascript

                MusicDB_Call("RemoveSongFromQueue", {entryid:"82390194629402649"});

        """
        if type(entryid) != str:
            logging.warning("entryid must be of type string! Actual type was %s. \033[1;30m(RemoveSongFromQueue will be ignored)", str(type(entryid)))
            return None

        self.songqueue.RemoveSong(int(entryid))
        return None


    def RemoveVideoFromQueue(self, entryid):
        """
        This method removes a video from the video queue.
        The video gets identified by the entry ID of the queue entry.

        Args:
            entryid (str) Queue entry ID of the video

        Returns:
            ``None``

        Example:
            .. code-block:: javascript

                MusicDB_Call("RemoveVideoFromQueue", {entryid:"82390194629402649"});

        """
        if type(entryid) != str:
            logging.warning("entryid must be of type string! Actual type was %s. \033[1;30m(RemoveVideoFromQueue will be ignored)", str(type(entryid)))
            return None

        self.videoqueue.RemoveVideo(int(entryid))
        return None
    
    
    def MoveSongInQueue(self, entryid, afterid):
        """
        This is a direct interface to :meth:`mdbapi.songqueue.SongQueue.MoveSong`.
        It moves a song from one position in the queue to another one.

        It is not allowed to move the current playing song (index 0).
        When this is tried, nothing happens.

        Args:
            entryid (str): Position of the song
            afterid (str): The position the song shall be moved to

        Return:
            ``None``

        Example:

            Assuming the following queue:

            +----------+---------+
            | entry ID | song ID |
            +==========+=========+
            | 1337     | 1       |
            +----------+---------+
            | 7357     | 2       |
            +----------+---------+
            | 2323     | 3       |
            +----------+---------+
            | 4242     | 4       |
            +----------+---------+

            Then the two calls will be applied.
            The first one is invalid, because entry ID ``"1337"`` addresses the current playing song at the top of the queue.
            So that one will be ignored.
            The next one moves song 2 to the end of the queue.

            .. code-block:: javascript

                MusicDB_Call("MoveSongInQueue", {entryid:"1337", afterid:"2323"});
                MusicDB_Call("MoveSongInQueue", {entryid:"7357", afterid:"4242"});

            So after processing the two calls, the queue looks like this:

            +----------+---------+
            | entry ID | song ID |
            +==========+=========+
            | 1337     | 1       |
            +----------+---------+
            | 2323     | 3       |
            +----------+---------+
            | 4242     | 4       |
            +----------+---------+
            | 7357     | 2       |
            +----------+---------+

        """
        if type(entryid) != str:
            logging.warning("entryid must be of type string! Actual type was %s. \033[1;30m(MoveSongInQueue will be ignored)", str(type(entryid)))
            return None
        if type(afterid) != str:
            logging.warning("afterid must be of type string! Actual type was %s. \033[1;30m(MoveSongInQueue will be ignored)", str(type(afterid)))
            return None

        self.songqueue.MoveSong(int(entryid), int(afterid))
        return None


    def MoveVideoInQueue(self, entryid, afterid):
        """
        This is a direct interface to :meth:`mdbapi.videoqueue.VideoQueue.MoveVideo`.
        It moves a video from one position in the queue to another one.

        It is not allowed to move the current playing video (index 0).
        When this is tried, nothing happens.

        Args:
            entryid (str): Position of the video
            afterid (str): The position the video shall be moved to

        Return:
            ``None``

        """
        if type(entryid) != str:
            logging.warning("entryid must be of type string! Actual type was %s. \033[1;30m(MoveVideoInQueue will be ignored)", str(type(entryid)))
            return None
        if type(afterid) != str:
            logging.warning("afterid must be of type string! Actual type was %s. \033[1;30m(MoveVideoInQueue will be ignored)", str(type(afterid)))
            return None

        self.videoqueue.MoveVideo(int(entryid), int(afterid))
        return None


    def GetSongRelationship(self, songid):
        """
        This method returns the relationship of a song.
        It is a list of songs that were played before or after the song with song ID *songid*.

        The returned dictionary contains the same song ID given as argument to this method, and list of related songs.
        Each lists entry is a dictionary with the related ``song``, ``album`` and ``artist`` album from the database.
        Furthermore the ``weight`` is given.
        The weight indicates how often the two songs were played together.
        Hated and disabled songs will not appear in the list.

        The list of songs gets sorted by the keys in the following list: (sorted by priority)

            * Artist Name
            * Album Release
            * Album Name
            * Song CD
            * Song Number

        The ``tags`` of that song will also be returned separated into ``genre``, ``subgenre`` and ``mood``.
        See :meth:`~GetSongTags` for details how they are returned.

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
                            console.log(entry.tags.genres)
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

            # Ignore hated and disabled songs
            if song["favorite"] == -1 or song["disabled"]:
                continue

            tags   = self.GetSongTags(songid)
            entry["song"]    = song
            entry["tags"]    = tags
            entry["weight"]  = weight
            entry["album"]   = self.database.GetAlbumById(song["albumid"])
            entry["artist"]  = self.database.GetArtistById(song["artistid"])

            entries.append(entry)

        # Sort by Artist-ID and Album-ID
        entries.sort(key = lambda k:( 
            k["artist"]["name"], 
            k["album"]["release"], 
            k["album"]["name"], 
            k["song"]["cd"],
            k["song"]["number"]
            ))

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
        """
        Sets a color scheme for an album.
        Valid color names are the following and must be given as string to the *colorname* parameter.
        The color itself must be in HTML-Format: ``#RRGGBB``.
        
        The following color-names exist:

            * ``"bgcolor"`` -  Background color
            * ``"fgcolor"`` -  Primary foreground color
            * ``"hlcolor"`` -  Secondary foreground color

        Args:
            albumid (int): ID of the album
            colorname (str): Name of the color to set (``"fgcolor"``, ``"hlcolor"``, ``"bgcolor"``)
            color (str): Color code in HTML notation: #RRGGBB

        Return:
            ``None``

        Example:
            .. code-block:: javascript

                MusicDB_Call("SetAlbumColor", {albumid:1000, colorname:"bgcolor", color:"#42AB23"});
        """
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
        
        After setting the new tag for the song, 
        the album tags get updated using :meth:`mdbapi.tags.MusicDBTags.DeriveAlbumTags`.
        So when changing a genre or sub genre, then they get suggested as album genre or sub genre

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
        albumid = self.database.GetSongById(songid)["albumid"]
        self.tags.DeriveAlbumTags(albumid)
        return None


    def RemoveSongTag(self, songid, tagid):
        """
        Removes a tag from a song

        If tagging is disabled nothing will be done. 

        After executing this method, the MusicDB server broadcasts the result of :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.GetSong`. (``method = "broadcast", fncname = "GetSong"``)
        So each client gets informed about the changes made.
        This is important to update the HUD if the song is currently playing.
        
        After setting the new tag for the song, 
        the album tags get updated using :meth:`mdbapi.tags.MusicDBTags.DeriveAlbumTags`.
        So when changing a genre or sub genre, then they get suggested as album genre or sub genre

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
        albumid = self.database.GetSongById(songid)["albumid"]
        self.tags.DeriveAlbumTags(albumid)
        return None


    def SetVideoTag(self, videoid, tagid):
        """
        Sets a tag for a video.
        This method sets the approval-level to 1 (Set by User) and confidence to 1.0 for this tag.
        So, this method can also be used to approve an AI set tag.

        If tagging is disabled nothing will be done. 

        After executing this method, the MusicDB server broadcasts the result of :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.GetVideo`. (``method = "broadcast", fncname = "GetVideo"``)
        So each client gets informed about the changes made.
        This is important to update the HUD if the video is currently playing.
        
        Args:
            videoid (int): ID of the video
            tagid (int): ID of the tag

        Return:
            ``None``

        Examples:
            .. code-block:: javascript

                MusicDB_Call("SetVideoTag", {videoid:videoid, tagid:tagid});

            .. code-block:: javascript

                MusicDB_Request("SetVideoTag", "UpdateTagInput", {videoid:videoid, tagid:tagid}, {taginputid:taginputid});

                // …

                function onMusicDBMessage(fnc, sig, args, pass)
                {
                    if(fnc == "GetVideo" && sig == "UpdateTagInput")
                    {
                        console.log("Updating " + pass.taginputid + " for video " + args.video.name);
                        Taginput_Update(pass.taginputid, args.tags);
                    }
                }
        """
        if self.cfg.debug.disabletagging:
            logging.info("Changing tags disabled. \033[1;33m!!")
            return None

        self.database.SetTargetTag("video", videoid, tagid)
        return None


    def RemoveVideoTag(self, videoid, tagid):
        """
        Removes a tag from a video.

        If tagging is disabled nothing will be done. 

        After executing this method, the MusicDB server broadcasts the result of :meth:`~lib.ws.mdbwsi.MusicDBWebSocketInterface.GetVideo`. (``method = "broadcast", fncname = "GetVideo"``)
        So each client gets informed about the changes made.
        This is important to update the HUD if the video is currently playing.
        
        Args:
            videoid (int): ID of the video
            tagid (int): ID of the tag

        Return:
            ``None``

        Example:
            .. code-block:: javascript

                MusicDB_Call("RemoveVideoTag", {videoid:videoid, tagid:tagid});
        """
        if self.cfg.debug.disabletagging:
            logging.info("Changing tags disabled. \033[1;33m!!")
            return None

        self.database.RemoveTargetTag("video", videoid, tagid)
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

