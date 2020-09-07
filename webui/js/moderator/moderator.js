
var currentsongid   = null; // \_ track current album and song
var currentalbumid  = null; // /

// Create Basic MusicDB WebUI Components
let fullscreenmanager   = new FullscreenManager();
let mdbmodemanager      = new MDBModeManager();
let tagmanager          = new TagManager();
let musicdbhud          = new MusicDBHUD();
let genreselectionview  = new GenreSelectionView();
let videostreamplayer   = new VideoStreamPlayer();
let musicdbstatus       = new MusicDBStatus();
let musicdbcontrols     = new MusicDBControls();
let queuetimemanager    = new QueueTimeManager();

let aboutmusicdb        = new AboutMusicDB();
let artistsview         = new ArtistsView();
let videoview           = new VideoView();
let queueview           = new QueueView();

// Create Main Menu
let mainmenu           = new MainMenu("1em", "1em");
mainmenu.CreateSwitch(
    new SVGIcon("EnterFullscreen"), "Enter Fullscreen", ()=>{fullscreenmanager.EnterFullscreen();},
    new SVGIcon("LeaveFullscreen"), "Leave Fullscreen", ()=>{fullscreenmanager.LeaveFullscreen();}
    );
let entryid = mainmenu.CreateSwitch(
    new SVGIcon("Switch2Video"), "Switch to Video Mode", ()=>{mdbmodemanager.SetVideoMode();},
    new SVGIcon("Switch2Audio"), "Switch to Audio Mode", ()=>{mdbmodemanager.SetAudioMode();}
    );
mainmenu.CreateButton(
    new SVGIcon("Reload"), "Reload Artists", ()=>
        {
            if(mdbmodemanager.GetCurrentMode() == "audio")
                MusicDB_Request("GetFilteredArtistsWithAlbums", "ShowArtists");
            else
                MusicDB_Request("GetFilteredArtistsWithVideos", "ShowArtists");
        }
    );
mainmenu.CreateButton(
    new SVGIcon("MusicDB"), "About MusicDB", ()=>
        {
            let mainviewbox = document.getElementById("MiddleContentBox");
            mainviewbox.innerHTML = "";
            mainviewbox.appendChild(aboutmusicdb.GetHTMLElement());
        }
    );
mainmenu.CreateSection("MusicDB Status", musicdbstatus.GetHTMLElement());
mainmenu.UpdateMenuEntryList();
mdbmodemanager.SetMainMenuHandler(mainmenu, entryid); // This allows updating the menu entry on mode switch from remote



window.onload = function ()
{
    // Do some last DOM changes
    let HUDparent   = document.getElementById("HUDBox");
    HUDparent.appendChild(musicdbhud.GetHTMLElement());

    let genrebox    = document.getElementById("GenreBox");
    genrebox.appendChild(genreselectionview.GetHTMLElement());

    let videoplayer = document.getElementById("VideoStreamPlayer");
    videostreamplayer.SetVideoPlayerElement(videoplayer);

    let controlsbox = document.getElementById("ControlBox");
    controlsbox.appendChild(musicdbcontrols.GetHTMLElement());

    let queuetimebar= document.getElementById("MDBQueueTimeBar");
    queuetimebar.appendChild(queuetimemanager.GetHTMLElement());

    let artistviewbox   = document.getElementById("LeftContentBox");
    artistviewbox.appendChild(artistsview.GetHTMLElement());

    document.body.appendChild(mainmenu.GetHTMLElement());
    document.body.appendChild(musicdbstatus.GetReconnectButtonHTMLElement());


    // Connect to MusicDB
    ConnectToMusicDB();

    // Setup the Views
    ShowAlphabetBar("Alphabetbar");
    ShowQueueControls("QueueControl");
    ShowSearchInput("Search");
    CreateIntersectionObserver("detachable_trigger", onDetachableTriggerIntersection);
}

function onMusicDBConnectionOpen()
{
    window.console && console.log("[MDB] Open");
    musicdbstatus.onMusicDBConnectionOpen();

    MusicDB_Request("GetMDBState",  "InitializeWebUI");
}
function onMusicDBConnectionError()
{
    window.console && console.log("[MDB] Error");
    musicdbstatus.onMusicDBConnectionError();
}
function onMusicDBWatchdogBarks()
{
    window.console && console.log("[MDB] WD Barks");
    musicdbstatus.onMusicDBWatchdogBarks();
}
function onMusicDBConnectionClosed()
{
    window.console && console.log("[MDB] Closed");
    musicdbstatus.onMusicDBConnectionClosed();
}

function onMusicDBNotification(fnc, sig, rawdata)
{
    musicdbhud.onMusicDBNotification(fnc, sig, rawdata);
    musicdbstatus.onMusicDBNotification(fnc, sig, rawdata);
    queuetimemanager.onMusicDBNotification(fnc, sig, rawdata);
    videostreamplayer.onMusicDBNotification(fnc, sig, rawdata);

    window.console && console.log(sig);
    if(fnc == "MusicDB:AudioStream")
    {
        // Handle notifications
        if(sig == "onStatusChanged")
        {
            MusicDB_Request("GetAudioStreamState", "UpdateStreamState");
        }
    }
    else if(fnc == "MusicDB:VideoStream")
    {
        if(sig == "onStatusChanged")
        {
            MusicDB_Request("GetVideoStreamState", "UpdateStreamState");
        }
        else if(sig == "onStreamNextVideo")
        {
            MusicDB_Request("GetVideoStreamState", "UpdateHUD");
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
    // Background objects
    tagmanager.onMusicDBMessage(fnc, sig, args, pass);
    mdbmodemanager.onMusicDBMessage(fnc, sig, args, pass);
    // Controls
    musicdbcontrols.onMusicDBMessage(fnc, sig, args, pass);
    musicdbstatus.onMusicDBMessage(fnc, sig, args, pass);
    // Views
    musicdbhud.onMusicDBMessage(fnc, sig, args, pass);
    videostreamplayer.onMusicDBMessage(fnc, sig, args, pass);
    genreselectionview.onMusicDBMessage(fnc, sig, args, pass);
    artistsview.onMusicDBMessage(fnc, sig, args, pass);
    videoview.onMusicDBMessage(fnc, sig, args, pass);
    queueview.onMusicDBMessage(fnc, sig, args, pass);

    window.console && console.log("%c >> fnc: "+fnc+"; sig: "+sig, "color:#7a90c8");


    // Handle Messages form the server
    if(fnc == "GetMDBState" && sig == "InitializeWebUI") {
        MusicDB_Request("GetTags",          "UpdateTagsCache");
        MusicDB_Request("GetAudioStreamState",   "UpdateStreamState");
        MusicDB_Request("GetMDBState",      "UpdateMDBState");
    }

    else if(fnc == "GetAudioStreamState" && sig == "UpdateStreamState") {
        if(!args.hasqueue)
        {
            window.console && console.log("There is no queue and no current song!")
            return
        }

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
            UpdateRelationshipGenreHighlight(args);
        }
    }
    else if(fnc=="sys:refresh" && sig == "UpdateCaches") {
        MusicDB_Request("GetTags", "UpdateTagsCache");                  // Update tag cache
        MusicDB_Request("GetFilteredArtistsWithAlbums", "ShowArtists"); // Update artist view
    }
    else if(fnc == "GetSong") {
        // Update album view - in case the song is visible right now…
        Albumview_UpdateSong(args.album, args.song, args.tags);

        // Update rest if a tag input element must be updated
        if(sig == "UpdateTagInput")
        {
            UpdateRelationshipTileTags(pass.taginputid, args.tags);
        }
    }
    else if(fnc == "GetVideo") {
        if(sig == "ShowVideo")
        {
            UpdateStyle(args.video.bgcolor, args.video.fgcolor, args.video.hlcolor)
        }
        else if(sig == "UpdateVideo" || sig == "UpdateTagInput")
        {
            UpdateStyle();    // Update new tags
        }
    }
    else if(fnc == "GetSongQueue" && sig == "ShowSongQueue")
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
        Songtags_ShowMoodControl("MoodHUD", "MainMoodControl");
    }

}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

