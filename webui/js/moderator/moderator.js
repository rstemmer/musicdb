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

// Create WebUI Application
let WebUI = new Application();

// Create Basic MusicDB Logic Components
WebUI.AddManager("Tags",        new TagManager());
WebUI.AddManager("Artists",     new ArtistsCache());
WebUI.AddManager("Color",       new ColorManager());
WebUI.AddManager("Fullscreen",  new FullscreenManager());
WebUI.AddManager("MusicMode",   new MDBModeManager());
WebUI.AddManager("Upload",      new UploadManager());

// Create some Layers on top of the main layout
let curtain         = WebUI.AddLayer("MenuBackground",  new Curtain());
let mainmenu        = WebUI.AddLayer("MainMenu",        new MainMenu(curtain));
let mainmenubutton  = WebUI.AddLayer("MainMenuButton",  new MenuButton("1rem", "1rem", "Menu", ()=>{mainmenu.ToggleMenu();}, "Show main menu"));

let layerbackground = WebUI.AddLayer("LayerBackground", new LayerBackground());
WebUI.AddLayer("AlbumImport",               new AlbumImportLayer(layerbackground));
WebUI.AddLayer("AlbumIntegration",          new AlbumIntegrationLayer(layerbackground));
WebUI.AddLayer("AlbumUploadProgress",       new AlbumUploadProgress(layerbackground));
WebUI.AddLayer("AlbumIntegrationProgress",  new AlbumIntegrationProgress(layerbackground));
WebUI.AddLayer("AlbumImportProgress",       new AlbumImportProgress(layerbackground));
WebUI.AddLayer("AlbumSettings",             new AlbumSettingsLayer(layerbackground));

// Create Basic MusicDB WebUI Components
WebUI.AddView("MusicDBControls",    new MusicDBControls(),      "ControlBox");
WebUI.AddView("QueueTime",          new QueueTimeManager(),     "MDBQueueTimeBar");
WebUI.AddView("QueueControl",       new QueueControlView(),     "QueueControl");
WebUI.AddView("MusicDBHUD",         new MusicDBHUD(),           "HUDBox");
WebUI.AddView("GenreSelection",     new GenreSelectionView(),   "GenreBox");
WebUI.AddView("AlphabetBar",        new AlphabetBar(),          "AlphabetBox");
WebUI.AddView("SearchInput",        new SearchInput(curtain),   "SearchBox");
let musicdbstatus =     WebUI.AddView("MusicDBStatus",      new MusicDBStatus());
let audiostreamplayer = WebUI.AddView("AudioStreamPlayer",  new AudioStreamPlayer());

WebUI.AddView("Artists",        new ArtistsView());
WebUI.AddView("Album",          new AlbumView());
WebUI.AddView("Lyrics",         new LyricsView());
WebUI.AddView("SearchResults",  new SearchResultsView());
WebUI.AddView("SongRelations",  new SongRelationsView());
WebUI.AddView("Video",          new VideoView());
WebUI.AddView("Queue",          new QueueView());
let streamview = WebUI.AddView("VideoStream", new StreamView());

let webuisettings       = new WebUISettings();
let streamsettings      = new StreamSettings();
let genresettings       = new GenreSettings();
let moodmanager         = new MoodManager();
let hiddenalbums        = new HiddenAlbums();
let albumimport         = new AlbumImport();
let videoimport         = new VideoImport();
let tasklistview        = new TaskListView();
let repairview          = new RepairView();
let settingsmenu        = new SettingsMenu(); // Accesses references to settings views

let leftviewmanager     = null; // \_
let mainviewmanager     = null; // / Can only be created when the document is created
let videopanelmanager   = null;

let configuration       = null; // Needs to be loaded from the Server

// Extend Main Menu
mainmenu.AddSection("Audio Stream",  audiostreamplayer);
mainmenu.AddSection("System Status", musicdbstatus);



window.onload = function ()
{
    // Do some last DOM changes
    WebUI.onWindowLoad();

    let body = new Element(document.body);
    body.AppendChild(musicdbstatus.GetReconnectButtonHTMLElement());

    leftviewmanager     = new LeftViewManager();
    mainviewmanager     = new MainViewManager();
    videopanelmanager   = new VideoPanelManager();
    streamview.ShowInVideoPanel();

    // Connect to MusicDB
    ConnectToMusicDB();
}

function onMusicDBConnectionOpen()
{
    WebUI.onWebSocketOpen();

    musicdbstatus.onMusicDBConnectionOpen();

    MusicDB_Request("LoadWebUIConfiguration", "SetupWebUI");
}
function onMusicDBConnectionError()
{
    WebUI.onWebSocketError();

    musicdbstatus.onMusicDBConnectionError();
    mainviewmanager.ShowWebSocketError();
}
function onMusicDBWatchdogBarks()
{
    WebUI.onWatchdogBarks();

    musicdbstatus.onMusicDBWatchdogBarks();
}
function onMusicDBConnectionClosed()
{
    WebUI.onWebSocketClosed();

    musicdbstatus.onMusicDBConnectionClosed();
}

function onMusicDBNotification(fnc, sig, rawdata)
{
    WebUI.onMusicDBNotification(fnc, sig, rawdata);

    tasklistview.onMusicDBNotification(fnc, sig, rawdata);
    repairview.onMusicDBNotification(fnc, sig, rawdata);

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
    WebUI.onMusicDBMessage(fnc, sig, args, pass);

    // Views
    leftviewmanager.onMusicDBMessage(fnc, sig, args, pass);
    mainviewmanager.onMusicDBMessage(fnc, sig, args, pass);
    // Setting Views
    settingsmenu.onMusicDBMessage(fnc, sig, args, pass);
    webuisettings.onMusicDBMessage(fnc, sig, args, pass);
    streamsettings.onMusicDBMessage(fnc, sig, args, pass);
    genresettings.onMusicDBMessage(fnc, sig, args, pass);
    moodmanager.onMusicDBMessage(fnc, sig, args, pass);
    hiddenalbums.onMusicDBMessage(fnc, sig, args, pass);
    albumimport.onMusicDBMessage(fnc, sig, args, pass);
    videoimport.onMusicDBMessage(fnc, sig, args, pass);
    tasklistview.onMusicDBMessage(fnc, sig, args, pass);
    repairview.onMusicDBMessage(fnc, sig, args, pass);


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

