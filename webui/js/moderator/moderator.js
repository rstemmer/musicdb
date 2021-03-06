// MusicDB,  a music manager with web-bases UI that focus on music.
// Copyright (C) 2017-2021  Ralf Stemmer <ralf.stemmer@gmx.net>
// 
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
// 
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
// 
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.

let curtain             = new Curtain();

// Create Basic MusicDB WebUI Components
let fullscreenmanager   = new FullscreenManager();
let mdbmodemanager      = new MDBModeManager();
let uploadmanager       = new UploadManager();
let colormanager        = new ColorManager();
let tagmanager          = new TagManager();
let artistscache        = new ArtistsCache();
let musicdbhud          = new MusicDBHUD();
let genreselectionview  = new GenreSelectionView();
let alphabetbar         = new AlphabetBar();
let searchinput         = new SearchInput(curtain);
let musicdbstatus       = new MusicDBStatus();
let musicdbcontrols     = new MusicDBControls();
let queuetimemanager    = new QueueTimeManager();

let leftviewmanager     = null; // \_
let mainviewmanager     = null; // / Can only be created when the document is created
let videopanelmanager   = null;
let artistsview         = new ArtistsView();
let albumview           = new AlbumView();
let lyricsview          = new LyricsView();
let streamview          = new StreamView();
let searchresultsview   = new SearchResultsView();
let songrelationsview   = new SongRelationsView();
let videoview           = new VideoView();
let queueview           = new QueueView();
let queuecontrolview    = new QueueControlView();

let webuisettings       = new WebUISettings();
let genresettings       = new GenreSettings();
let moodmanager         = new MoodManager();
let hiddenalbums        = new HiddenAlbums();
let videoimport         = new VideoImport();
let settingsmenu        = new SettingsMenu(); // Accesses references to settings views

let configuration       = null; // Needs to be loaded from the Server

// Create Main Menu
let mainmenu           = new MainMenu(curtain);
mainmenu.AddSection("MusicDB Status", musicdbstatus.GetHTMLElement()); // FIXME



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

    let queuecontrolsbox   = document.getElementById("QueueControl");
    queuecontrolsbox.appendChild(queuecontrolview.GetHTMLElement());

    let mainmenubutton = new MenuButton("1rem", "1rem", "Menu", ()=>{mainmenu.ToggleMenu();}, "Show main menu");
    document.body.appendChild(curtain.GetHTMLElement());
    document.body.appendChild(mainmenubutton.GetHTMLElement());
    document.body.appendChild(mainmenu.GetHTMLElement());
    document.body.appendChild(musicdbstatus.GetReconnectButtonHTMLElement());

    leftviewmanager     = new LeftViewManager();
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

    MusicDB_Request("LoadWebUIConfiguration", "SetupWebUI");
}
function onMusicDBConnectionError()
{
    window.console && console.log("[MDB] Error");
    musicdbstatus.onMusicDBConnectionError();
    mainviewmanager.ShowWebSocketError();
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
    uploadmanager.onMusicDBNotification(fnc, sig, rawdata);
    albumview.onMusicDBNotification(fnc, sig, rawdata);

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
    artistscache.onMusicDBMessage(fnc, sig, args, pass);
    mdbmodemanager.onMusicDBMessage(fnc, sig, args, pass);
    colormanager.onMusicDBMessage(fnc, sig, args, pass);
    uploadmanager.onMusicDBMessage(fnc, sig, args, pass);
    // Controls
    musicdbcontrols.onMusicDBMessage(fnc, sig, args, pass);
    musicdbstatus.onMusicDBMessage(fnc, sig, args, pass);
    mainmenu.onMusicDBMessage(fnc, sig, args, pass);
    // Views
    leftviewmanager.onMusicDBMessage(fnc, sig, args, pass);
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
    // Setting Views
    settingsmenu.onMusicDBMessage(fnc, sig, args, pass);
    webuisettings.onMusicDBMessage(fnc, sig, args, pass);
    genresettings.onMusicDBMessage(fnc, sig, args, pass);
    moodmanager.onMusicDBMessage(fnc, sig, args, pass);
    hiddenalbums.onMusicDBMessage(fnc, sig, args, pass);
    videoimport.onMusicDBMessage(fnc, sig, args, pass);


    // Handle Messages form the server
    if(fnc == "LoadWebUIConfiguration" && sig == "SetupWebUI")
    {
        configuration = args;

        if(configuration.debug.blurartwork == true)
            document.documentElement.style.setProperty("--artworkfilter", "blur(5px)");

        MusicDB_Request("GetMDBState", "InitializeWebUI");
    }
    else if(sig == "UpdateConfig")
    {
        configuration = args;
    }
    else if(fnc == "GetMDBState" && sig == "InitializeWebUI")
    {
        if(args.audiostream.currentsong == null && args.videostream.currentvideo == null)
        {
            // All queues empty -> fresh install
            mainviewmanager.ShowWelcome();
        }

        let uimode = args.uimode;
        MusicDB_Request("GetArtists",  "UpdateArtistsCache");
        MusicDB_Request("GetTags",     "UpdateTagsCache");
        MusicDB_Request("GetMDBState", "UpdateMDBState");
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
        MusicDB_Request("GetTags",    "UpdateTagsCache");
        MusicDB_Request("GetArtists", "UpdateArtistsCache");
        MusicDB_Request("GetFilteredArtistsWithAlbums", "ShowArtists"); // Update artist view
    }

    return;
}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

