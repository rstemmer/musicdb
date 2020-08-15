
var currentsongid   = null; // \_ track current album and song
var currentalbumid  = null; // /

function onMusicDBConnectionOpen()
{
    SetMusicDBOnlineState("yes", "yes"); // data, audio, video
    window.console && console.log("[MDB] Open");
    MusicDB_Request("GetMDBState",  "InitializeWebUI");
}
function onMusicDBConnectionError()
{
    SetMusicDBOnlineState("error", "unknown", "error"); // data, audio, video
    window.console && console.log("[MDB] Error");
}
function onMusicDBWatchdogBarks()
{
    SetMusicDBOnlineState("error", "unknown", "unknown"); // data, audio, video
    window.console && console.log("[MDB] WD Barks");
}
function onMusicDBConnectionClosed()
{
    SetMusicDBOnlineState("no", "unknown", "no"); // data, audio, video
    window.console && console.log("[MDB] Closed");
}

function onMusicDBNotification(fnc, sig, rawdata)
{
    window.console && console.log(sig);
    if(fnc == "MusicDB:AudioStream")
    {
        // Update state indicator.
        // Just because the audio stream to Icecast works,
        // it is not sure that the Icecast is actually OK -> null for audio
        SetMusicDBOnlineState("yes", null, null); // data, audio, video
        
        // Handle notifications
        if(sig == "onTimeChanged")
        {
            // rawdata is the currently played time of the current song
            // this method gets called every mpd-poll interval
            SetTimePlayed(rawdata);
            // This also updated the Timer-View
        }
        else if(sig == "onStatusChanged")
        {
            MusicDB_Request("GetAudioStreamState", "UpdateStreamState");
        }
    }
    else if(fnc == "MusicDB:VideoStream")
    {
        window.console && console.log(sig);
        window.console && console.log(rawdata);
        // Update state indicator. If notifications arrive, something must be working :)
        SetMusicDBOnlineState("yes", null, "yes"); // Data, Audio, Video

        if(sig == "onStatusChanged")
        {
            MusicDB_Request("GetVideoStreamState", "UpdateStreamState");
        }
        else if(sig == "onStreamNextVideo")
        {
            // New video and entry is included rawdata
            PlayVideo(rawdata.video, rawdata.queue.entryid, rawdata.streamstate.isplaying); // true: directly start playing video
        }
    }
    else if(fnc == "MusicDB:SongQueue")
    {
        if(sig == "onSongChanged")
        {
            MusicDB_Request("GetAudioStreamState", "UpdateStreamState");
        }
        else if(sig == "onSongQueueChanged")
        {
            MusicDB_Request("GetSongQueue", "ShowSongQueue");
        }
    }
    else if (fnc == "MusicDB:VideoQueue")
    {
        if(sig == "onVideoChanged")
        {
            MusicDB_Request("GetAudioStreamState", "UpdateStreamState");
        }
        else if(sig == "onVideoQueueChanged")
        {
            MusicDB_Request("GetVideoQueue", "ShowVideoQueue");
        }
    }
}
function onMusicDBMessage(fnc, sig, args, pass)
{
    // Update state-indicators if some indication passes
    if(fnc == "GetAudioStreamState")
    {
        if(args.isconnected)
        {
            SetMusicDBOnlineState("yes", "yes", null);  // data, audio, video
            MDB_EnableWatchdog();
        }
        else
        {
            SetMusicDBOnlineState("yes", "no", null);   // data, audio, video
            MDB_DisableWatchdog();                      // Stop watchdog when MPD cannot trigger updates
            // TODO: behavior changed with the new Icecast backend.
        }

        if(args.isplaying)
            SetMusicDBPlayingState("playing", null);    // Stream, Client
        else
            SetMusicDBPlayingState("paused", null);     // Stream, Client
    }
    else if(fnc == "GetVideoStreamState")
    {
        window.console && console.log("GetVideoStreamState");
        window.console && console.log(args);
        if(args.isstreaming)
            SetMusicDBOnlineState("yes", null, "yes");  // data, audio, video
        else
            SetMusicDBOnlineState("yes", null, "no");   // data, audio, video

        // FIXME: JUST FOR DEBUGGING
        PlayVideo(args.video, args.currententry, args.isplaying);

        // TODO: Handle playing state
    }
    else
        window.console && console.log(" >> fnc: "+fnc+"; sig: "+sig);


    // Handle Messages form the server
    if(fnc == "GetMDBState" && sig == "InitializeWebUI") {
        MusicDB_Request("GetTags",          "UpdateTagsCache");
        MusicDB_Request("GetAudioStreamState",   "UpdateStreamState");
        MusicDB_Request("GetVideoStreamState",   "UpdateStreamState");
        MusicDB_Request("GetMDBState",      "UpdateMDBState");

        if(args.MusicDB.uimode == "audio")
        {
            MusicDB_Request("GetSongQueue",                 "ShowSongQueue");
            MusicDB_Request("GetFilteredArtistsWithAlbums", "ShowArtists");
        }
        else if(args.MusicDB.uimode == "video")
        {
            MusicDB_Request("GetVideoQueue",                "ShowVideoQueue");
            MusicDB_Request("GetFilteredArtistsWithVideos", "ShowArtists");
        }
    }

    else if(fnc == "GetAudioStreamState" && sig == "UpdateStreamState") {
        if(!args.hasqueue)
        {
            window.console && console.log("There is no queue and no current song!")
            return
        }

        UpdateMusicDBHUD(args.song, args.album, args.artist);
        Songtags_UpdateMoodControl("MainMoodControl", args.songtags);
        Songproperties_UpdateControl("MainPropertyControl", args.song, true); // reset like/dislike state
        Taginput_Show("GenreHUD",    "MainSongGenreView",    args.song.id, args.songtags, "Genre",    "Song");
        Taginput_Show("SubgenreHUD", "MainSongSubgenreView", args.song.id, args.songtags, "Subgenre", "Song");

        // if the song changes, show the new album (or reload for update)
        if(args.song.id != currentsongid)
        {
            currentsongid = args.song.id;   // update current song id
            MusicDB_Request("GetAlbum", "ShowAlbum", {albumid: args.album.id});
        }
    }
    else if(fnc == "GetMDBState") {
        if(sig == "UpdateMDBState" || sig == "UpdateRelationshipGenreHighlight")
        {
            UpdateMusicDBMode(args);
            Artistloader_UpdateState(args);
            UpdateRelationshipGenreHighlight(args);
        }
    }
    else if(fnc=="sys:refresh" && sig == "UpdateCaches") {
        MusicDB_Request("GetTags", "UpdateTagsCache");                  // Update tag cache
        MusicDB_Request("GetFilteredArtistsWithAlbums", "ShowArtists"); // Update artist view
    }
    else if(fnc == "GetSong"/* && sig == "UpdateSong"*/) {
        // Update album view - in case the song is visible right now…
        Albumview_UpdateSong(args.album, args.song, args.tags);

        // Update HUD
        if(args.song.id == currentsongid)
        {
            Songtags_UpdateMoodControl("MainMoodControl", args.tags);
            Songproperties_UpdateControl("MainPropertyControl", args.song, false); // dont reset like/dislike state
            Taginput_Show("GenreHUD",    "MainSongGenreView",    args.song.id, args.tags, "Genre",    "Song");
            Taginput_Show("SubgenreHUD", "MainSongSubgenreView", args.song.id, args.tags, "Subgenre", "Song");
            UpdateStyle();    // Update new tags
        }

        // Update rest if a tag input element must be updated
        if(sig == "UpdateTagInput")
        {
            UpdateRelationshipTileTags(pass.taginputid, args.tags);
        }
    }
    else if(fnc == "GetVideo") {
        if(sig == "ShowVideo")
        {
            ShowVideo("MiddleContentBox", args.artist, args.album, args.song, args.video, args.tags);
        }
        else if(sig == "UpdateVideo" || sig == "UpdateTagInput")
        {
            //if(args.video.id == currentvideoid)
            //{
                UpdateVideoSettings(args.video, args.tags, false);
                UpdateStyle();    // Update new tags
            //}
        }
    }
    else if(fnc == "GetSongQueue" && sig == "ShowSongQueue")
        ShowQueue("RightContentBox", args);

    else if(fnc == "GetVideoQueue" && sig == "ShowVideoQueue")
        ShowQueue("RightContentBox", args);

    else if(fnc == "GetAlbum" && sig == "ShowAlbum") {
        ShowAlbum("MiddleContentBox", args.artist, args.album, args.cds, args.tags, currentsongid);
        currentalbumid = args.album.id;
    }
    else if(fnc == "GetAlbum" && sig == "UpdateTagInput") {
        if(args.album.id == currentalbumid)
        {
            Albumview_UpdateAlbum(args.album, args.tags);
        }
    }
    else if(fnc == "Find" && sig == "ShowSearchResults")
        ShowSearchResults(args.artists, args.albums, args.songs);

    else if(fnc == "GetFilteredArtistsWithAlbums" && sig == "ShowArtists")
        ShowArtists("LeftContentBox", args);

    else if(fnc == "GetFilteredArtistsWithVideos" && sig == "ShowArtists")
        ShowArtists("LeftContentBox", args);

    else if(fnc == "GetSongRelationship" && sig == "ShowSongRelationship")
        ShowSongRelationship("MiddleContentBox", args.songid, args.songs);

    else if(fnc == "GetSongLyrics" && sig == "ShowLyrics") {
        parentid = pass.parentid || "MiddleContentBox";
        mode     = pass.mode     || "view";
        ShowLyrics(parentid, args, mode);
    }
    else if(fnc == "GetTags")
    {
        Tagmanager_onGetTags(args);
        Artistloader_UpdateControl();
        MusicDB_Request("GetMDBState", "UpdateMDBState"); // Update cached MDB state (Selected Genre)
        Songtags_ShowMoodControl("MoodHUD", "MainMoodControl");
    }
}


window.onload = function ()
{
    ConnectToMusicDB();
    ShowAlphabetBar("Alphabetbar");
    ShowMusicDBHUD("HUD");
    Songproperties_ShowControl("PropertyHUD", "MainPropertyControl");
    ShowMusicDBStateView("State");
    Artistloader_Show("Artistloader");
    ShowQueueControls("QueueControl");
    ShowSearchInput("Search");
    ShowFullscreenButton();
    CreateIntersectionObserver("detachable_trigger", onDetachableTriggerIntersection);
}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

