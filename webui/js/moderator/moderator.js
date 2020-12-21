
var currentsongid   = null; // \_ track current album and song
var currentalbumid  = null; // /

let curtain             = new Curtain();

// Create Basic MusicDB WebUI Components
let fullscreenmanager   = new FullscreenManager();
let mdbmodemanager      = new MDBModeManager();
let colormanager        = new ColorManager();
let tagmanager          = new TagManager();
let musicdbhud          = new MusicDBHUD();
let genreselectionview  = new GenreSelectionView();
let alphabetbar         = new AlphabetBar();
let searchinput         = new SearchInput(curtain);
let musicdbstatus       = new MusicDBStatus();
let musicdbcontrols     = new MusicDBControls();
let queuetimemanager    = new QueueTimeManager();

let mainviewmanager     = null; // Can only be created when the document is created
let videopanelmanager   = null;
let aboutmusicdb        = new AboutMusicDB();
let artistsview         = new ArtistsView();
let albumview           = new AlbumView();
let lyricsview          = new LyricsView();
let streamview          = new StreamView();
let searchresultsview   = new SearchResultsView();
let songrelationsview   = new SongRelationsView();
let videoview           = new VideoView();
let queueview           = new QueueView();
let queuecontrolview    = new QueueControlView();


// Create Main Menu
let mainmenu           = new MainMenu("1em", "1em", curtain);
mainmenu.CreateSwitch(
    new SVGIcon("EnterFullscreen"), "Enter Fullscreen", ()=>{fullscreenmanager.EnterFullscreen();},
    new SVGIcon("LeaveFullscreen"), "Leave Fullscreen", ()=>{fullscreenmanager.LeaveFullscreen();}
    , "Switch browser between window and fullscreen mode");
let entryid = mainmenu.CreateSwitch(
    new SVGIcon("Switch2Video"), "Switch to Video Mode", ()=>{mdbmodemanager.SetVideoMode();},
    new SVGIcon("Switch2Audio"), "Switch to Audio Mode", ()=>{mdbmodemanager.SetAudioMode();}
    , "Switch MusicDB WebUI between audio and video mode");
mainmenu.CreateButton(
    new SVGIcon("Reload"), "Reload Artists", ()=>
        {
            if(mdbmodemanager.GetCurrentMode() == "audio")
                MusicDB_Request("GetFilteredArtistsWithAlbums", "ShowArtists");
            else
                MusicDB_Request("GetFilteredArtistsWithVideos", "ShowArtists");
        }
    , "Reload list with artists and their albums/videos");
mainmenu.CreateButton(
    new SVGIcon("MusicDB"), "About MusicDB", ()=>
        {
            mainviewmanager.ShowAboutMusicDB();
        }
    , "Show information about MusicDB including version numbers");
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

    let alphabetbox    = document.getElementById("AlphabetBox");
    alphabetbox.appendChild(alphabetbar.GetHTMLElement());

    let searchbox    = document.getElementById("SearchBox");
    searchbox.appendChild(searchinput.GetHTMLElement());

    let controlsbox = document.getElementById("ControlBox");
    controlsbox.appendChild(musicdbcontrols.GetHTMLElement());

    let queuetimebar= document.getElementById("MDBQueueTimeBar");
    queuetimebar.appendChild(queuetimemanager.GetHTMLElement());

    let artistviewbox   = document.getElementById("LeftContentBox");
    artistviewbox.appendChild(artistsview.GetHTMLElement());

    let queuecontrolsbox   = document.getElementById("QueueControl");
    queuecontrolsbox.appendChild(queuecontrolview.GetHTMLElement());

    document.body.appendChild(curtain.GetHTMLElement());
    document.body.appendChild(mainmenu.GetHTMLElement());
    document.body.appendChild(musicdbstatus.GetReconnectButtonHTMLElement());

    mainviewmanager     = new MainViewManager();
    videopanelmanager   = new VideoPanelManager();
    streamview.ShowInVideoPanel();


    // Connect to MusicDB
    ConnectToMusicDB();
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
    window.console && console.log("%c >> fnc: "+fnc+"; sig: "+sig, "color:#c87a7a");
    musicdbhud.onMusicDBNotification(fnc, sig, rawdata);
    musicdbstatus.onMusicDBNotification(fnc, sig, rawdata);
    queuetimemanager.onMusicDBNotification(fnc, sig, rawdata);
    streamview.onMusicDBNotification(fnc, sig, rawdata);

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
    window.console && console.log("%c >> fnc: "+fnc+"; sig: "+sig, "color:#7a90c8");

    // Background objects
    tagmanager.onMusicDBMessage(fnc, sig, args, pass);
    mdbmodemanager.onMusicDBMessage(fnc, sig, args, pass);
    colormanager.onMusicDBMessage(fnc, sig, args, pass);
    // Controls
    musicdbcontrols.onMusicDBMessage(fnc, sig, args, pass);
    musicdbstatus.onMusicDBMessage(fnc, sig, args, pass);
    // Views
    mainviewmanager.onMusicDBMessage(fnc, sig, args, pass);
    musicdbhud.onMusicDBMessage(fnc, sig, args, pass);
    genreselectionview.onMusicDBMessage(fnc, sig, args, pass);
    searchinput.onMusicDBMessage(fnc, sig, args, pass);
    searchresultsview.onMusicDBMessage(fnc, sig, args, pass);
    songrelationsview.onMusicDBMessage(fnc, sig, args, pass);
    artistsview.onMusicDBMessage(fnc, sig, args, pass);
    albumview.onMusicDBMessage(fnc, sig, args, pass);
    lyricsview.onMusicDBMessage(fnc, sig, args, pass);
    streamview.onMusicDBMessage(fnc, sig, args, pass);
    videoview.onMusicDBMessage(fnc, sig, args, pass);
    queueview.onMusicDBMessage(fnc, sig, args, pass);


    // Handle Messages form the server
    if(fnc == "GetMDBState" && sig == "InitializeWebUI")
    {
        let uimode = args.uimode;
        MusicDB_Request("GetTags",          "UpdateTagsCache");
        MusicDB_Request("GetMDBState",      "UpdateMDBState");
        if(uimode == "audio")
        {
            MusicDB_Request("GetAudioStreamState",   "UpdateStreamState");
        }
        else if(uimode == "video")
        {
            MusicDB_Request("GetVideoStreamState",   "UpdateStreamState");
        }
    }
    else if(fnc=="sys:refresh" && sig == "UpdateCaches")    // TODO: Update (make uimode conform)
    {
        MusicDB_Request("GetTags", "UpdateTagsCache");                  // Update tag cache
        MusicDB_Request("GetFilteredArtistsWithAlbums", "ShowArtists"); // Update artist view
    }

    return;
}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

