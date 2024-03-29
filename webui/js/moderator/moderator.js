// MusicDB,  a music manager with web-bases UI that focus on music.
// Copyright (C) 2017 - 2022  Ralf Stemmer <ralf.stemmer@gmx.net>
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
let MusicDB = new BackEndConnection(WEBSOCKET_URL);
let WebUI   = new Application();
let configuration       = null; // Needs to be loaded from the Server

function InitializeWebUI(iconsjson=null)
{
    // Create Basic MusicDB Logic Components
    WebUI.AddManager("WebUI",       new WebUIManager());
    WebUI.AddManager("Icons",       new IconManager(iconsjson));
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

    let layerbackground = WebUI.AddLayer("LayerBackground", new LayerBackground(1));
    WebUI.AddLayer("AlbumImport",               new AlbumImportLayer(layerbackground));
    WebUI.AddLayer("AlbumIntegration",          new AlbumIntegrationLayer(layerbackground));
    WebUI.AddLayer("AlbumUploadProgress",       new AlbumUploadProgress(layerbackground));
    WebUI.AddLayer("AlbumIntegrationProgress",  new AlbumIntegrationProgress(layerbackground));
    WebUI.AddLayer("AlbumImportProgress",       new AlbumImportProgress(layerbackground));
    WebUI.AddLayer("AlbumSettings",             new AlbumSettingsLayer(layerbackground));
    WebUI.AddLayer("SongsSettings",             new SongsSettingsLayer(layerbackground));

    let errorbackground = WebUI.AddLayer("ErrorBackground", new LayerBackground(3));
    WebUI.AddLayer("WebSocketClosed",           new WebSocketClosed(errorbackground));
    WebUI.AddLayer("WebSocketError",            new WebSocketError(errorbackground));

    // Create Basic MusicDB WebUI Components
    WebUI.AddView("MusicDBControls",    new MusicDBControls(),      "ControlBox");
    WebUI.AddView("QueueTime",          new QueueTimeManager(),     "MDBQueueTimeBar");
    WebUI.AddView("QueueControl",       new QueueControlView(),     "QueueControl");
    WebUI.AddView("MusicDBHUD",         new MusicDBHUD(),           "HUDBox");
    WebUI.AddView("GenreSelection",     new GenreSelectionView(),   "GenreBox");
    WebUI.AddView("AlphabetBar",        new AlphabetBar(),          "AlphabetBox");
    WebUI.AddView("SearchInput",        new SearchInput(curtain),   "SearchBox");
    let musicdbstatus =     WebUI.AddView("MusicDBStatus",      new MusicDBStatus());
    let audiostreamplayer = WebUI.AddView("AudioStreamPlayer",  new AudioStreamControl());

    WebUI.AddView("Artists",        new ArtistsView());
    WebUI.AddView("Album",          new AlbumView());
    WebUI.AddView("Lyrics",         new LyricsView());
    WebUI.AddView("SearchResults",  new SearchResultsView());
    WebUI.AddView("SongRelations",  new SongRelationsView());
    WebUI.AddView("Video",          new VideoView());
    WebUI.AddView("Queue",          new QueueView());
    WebUI.AddView("VideoStream",    new StreamView());

    WebUI.AddView("WebUISettings",  new WebUISettings());
    WebUI.AddView("StreamSettings", new StreamSettings());
    WebUI.AddView("RandySettings",  new RandySettings());
    WebUI.AddView("GenreSettings",  new GenreSettings());
    WebUI.AddView("MoodSettings",   new MoodManager());
    WebUI.AddView("HiddenAlbums",   new HiddenAlbums());
    WebUI.AddView("AlbumImport",    new AlbumImport());
    WebUI.AddView("VideoImport",    new VideoImport());
    WebUI.AddView("TaskList",       new TaskListView());
    WebUI.AddView("Repair",         new RepairView());
    WebUI.AddView("SettingsMenu",   new SettingsMenu()); // Accesses references to settings views
    WebUI.AddView("AdvancedGenreSelection",new AdvancedGenreSelectionView());


    // Extend Main Menu
    mainmenu.AddSection("Audio Stream",  audiostreamplayer);
    mainmenu.AddSection("System Status", musicdbstatus);


    // Configure Communication
    MusicDB.ConfigureWatchdog(WATCHDOG_RUN, WATCHDOG_INTERVAL);
    MusicDB.ConfigureReconnects(3);
    MusicDB.ConfigureAPIKey(WEBSOCKET_APIKEY);

    // Map Back-End <-> Front-End interfaces
    MusicDB.SetCallbackForEvent("connect",      ()=>{WebUI.onWebSocketOpen();  });
    MusicDB.SetCallbackForEvent("disconnect",   ()=>{WebUI.onWebSocketClosed();});
    MusicDB.SetCallbackForEvent("error",        ()=>{WebUI.onWebSocketError(); });
    MusicDB.SetCallbackForEvent("watchdog",     ()=>{WebUI.onWatchdogBarks();  });
    MusicDB.SetCallbackForEvent("message",
        (fnc, sig, args, pass)=>{WebUI.onMusicDBMessage(fnc, sig, args, pass);});
    MusicDB.SetCallbackForEvent("notification",
        (fnc, sig, rawdata)=>{WebUI.onMusicDBNotification(fnc, sig, rawdata);});
}



function ExecuteWebUI()
{
    // Do some last DOM changes
    WebUI.onWindowLoad();

    // Add some parts that require an existing DOM
    WebUI.AddManager("LeftView", new LeftViewManager());
    WebUI.AddManager("MainView", new MainViewManager());
    WebUI.AddManager("VideoPanel", new VideoPanelManager());
    let streamview = WebUI.GetView("VideoStream");
    streamview.ShowInVideoPanel();

    // Connect to MusicDB
    MusicDB.Connect();
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

