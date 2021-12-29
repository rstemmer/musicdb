// MusicDB,  a music manager with web-bases UI that focus on music.
// Copyright (C) 2017-2020  Ralf Stemmer <ralf.stemmer@gmx.net>
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

"use strict";

// Whenever a view gets removed from the Main View Box,
// its method "onViewRemoved();" gets called if it exists
class ViewManager
{
    constructor(containerid)
    {
        this.container   = document.getElementById(containerid);
        this.currentview = null;
    }



    MountView(view)
    {
        // Check if View is locked.
        // If it is locked, do not replace it with a different view
        if(this.currentview != null
            && typeof this.currentview.GetLockState === "function"
            && this.currentview.GetLockState() == true)
            return;

        // Mount View
        let element = view.GetHTMLElement();
        this.container.innerHTML = "";
        this.container.appendChild(element);

        // Call "onViewRemoved" if it is an existing method
        if(this.currentview != null)
        {
            if(typeof this.currentview.onViewUnmounted === "function")
                this.currentview.onViewUnmounted();
        }

        this.currentview = view;

        if(this.currentview != null)
        {
            if(typeof this.currentview.onViewMounted === "function")
                this.currentview.onViewMounted();
        }
        return;
    }
}



class LeftViewManager extends ViewManager
{
    constructor()
    {
        super("LeftContentBox");
    }



    ShowArtistsView()
    {
        this.MountView(WebUI.GetView("Artists"));
    }
    ShowSettingsMenu()
    {
        WebUI.GetView("SettingsMenu").LockView()
        this.MountView(WebUI.GetView("SettingsMenu"));
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        if(sig == "ShowArtists")
        {
            this.ShowArtistsView();
        }
        return;
    }
}



class MainViewManager extends ViewManager
{
    constructor()
    {
        super("MiddleContentBox");
    }



    ShowAboutMusicDB()
    {
        this.MountView(new AboutMusicDB());
    }
    ShowWelcome()
    {
        this.MountView(new Welcome());
    }
    ShowWebSocketError()
    {
        this.MountView(new WebSocketError());
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        if(fnc == "GetAlbum" && sig == "ShowAlbum")
        {
            this.MountView(WebUI.GetView("Album"));
        }
        else if(fnc == "GetVideo" && sig == "ShowVideo")
        {
            this.MountView(WebUI.GetView("Video"));
        }
        else if(fnc == "GetSongLyrics" && sig == "ShowLyrics")
        {
            this.MountView(WebUI.GetView("Lyrics"));
        }
        else if(fnc == "Find" && sig == "ShowResults")
        {
            this.MountView(WebUI.GetView("SearchResults"));
        }
        else if(fnc == "GetSongRelationship" && sig == "ShowSongRelationship")
        {
            this.MountView(WebUI.GetView("SongRelations"));
        }

        // Settings
        else if(fnc == "LoadWebUIConfiguration" && sig == "ShowWebUISettings")
        {
            this.MountView(WebUI.GetView("WebUISettings"));
        }
        else if(fnc == "LoadWebUIConfiguration" && sig == "ShowStreamSettings")
        {
            this.MountView(WebUI.GetView("StreamSettings"));
        }
        else if(fnc == "GetTags" && sig == "ShowGenreSettings")
        {
            this.MountView(WebUI.GetView("GenreSettings"));
        }
        else if(fnc == "GetTags" && sig == "ShowMoodManager")
        {
            this.MountView(WebUI.GetView("MoodSettings"));
        }
        else if(fnc == "GetHiddenAlbums" && sig == "ShowHiddenAlbums")
        {
            this.MountView(WebUI.GetView("HiddenAlbums"));
        }
        else if(fnc == "FindNewContent" && sig == "ShowAlbumImport")
        {
            this.MountView(WebUI.GetView("AlbumImport"));
        }
        else if(fnc == "FindNewContent" && sig == "ShowVideoImport")
        {
            this.MountView(WebUI.GetView("VideoImport"));
        }
        else if(fnc == "InitiateFilesystemScan" && sig == "ShowRepairView")
        {
            this.MountView(WebUI.GetView("Repair"));
        }
        else if(fnc == "GetCurrentTasks" && sig == "ShowCurrentTasks")
        {
            this.MountView(WebUI.GetView("TaskList"));
        }
        return;
    }


}



class VideoPanelManager extends ViewManager
{
    constructor()
    {
        super("VideoPanel");
    }
}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

