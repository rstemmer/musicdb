
var currentsongid   = null; // \_ track current album and song
var currentalbumid  = null; // /

function onMusicDBConnectionOpen()
{
    SetMusicDBOnlineState("yes", "yes"); // MDB, MPD
    window.console && console.log("[MDB] Open");

    MusicDB_Request("GetTags",      "UpdateTagsCache");
    MusicDB_Request("GetMPDState",  "UpdateMPDState");
    MusicDB_Request("GetQueue",     "ShowQueue");
    MusicDB_Request("GetMDBState",  "UpdateMDBState");
    MusicDB_Request("GetFilteredArtistsWithAlbums", "ShowArtists");
}
function onMusicDBConnectionError()
{
    SetMusicDBOnlineState("error", "unknown"); // MDB, MPD
    window.console && console.log("[MDB] Error");
}
function onMusicDBWatchdogBarks()
{
    SetMusicDBOnlineState("error", "unknown"); // MDB, MPD
    window.console && console.log("[MDB] WD Barks");
}
function onMusicDBConnectionClosed()
{
    SetMusicDBOnlineState("no", "unknown"); // MDB, MPD
    window.console && console.log("[MDB] Closed");
}

function onMusicDBNotification(fnc, sig, rawdata)
{
    if(fnc == "mpd")
    {
        // Update state indicator.
        // If mpd sends notifications, it must be online
        // And MDP too. 
        SetMusicDBOnlineState("yes", "yes"); // MDB, MPD
        
        // Handle notifications
        if(sig == "onTimeChanged")
        {
            // rawdata is the currently played time of the current song
            // this method gets called every mpd-poll interval
            SetTimePlayed(rawdata);
            // This also updated the Timer-View
        }
        else if(sig == "onQueueChanged")
        {
            MusicDB_Request("GetQueue", "ShowQueue");
        }
        else if(sig == "onSongChanged" || sig == "onStatusChanged")
        {
            MusicDB_Request("GetMPDState", "UpdateMPDState");
        }

    }
}
function onMusicDBMessage(fnc, sig, args, pass)
{
    // Update state-indicators if some indication passes
    if(fnc == "GetMPDState")
    {
        if(args.isconnected)
            SetMusicDBOnlineState("yes", "yes");        // MDB, MPD
        else
            SetMusicDBOnlineState("yes", "no");         // MDB, MPD

        if(args.isplaying)
            SetMusicDBPlayingState("playing", null);    // Stream, Client
        else
            SetMusicDBPlayingState("paused", null);     // Stream, Client
    }
    else
        window.console && console.log(" >> fnc: "+fnc+"; sig: "+sig);


    // Handle Messages form the server
    if(fnc == "GetMPDState" && sig == "UpdateMPDState") {
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
    else if(fnc == "GetMDBState" && sig == "UpdateMDBState") {
        Artistloader_UpdateState(args);
    }
    else if(fnc=="SIGUSR1" && sig == "UpdateCaches") {
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
    }
    else if(fnc == "GetQueue" && sig == "ShowQueue")
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
    ShowMPDControls("Controls");
    ShowQueueControls("QueueControl");
    ShowSearchInput("Search");
    ShowFullscreenButton();
}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

