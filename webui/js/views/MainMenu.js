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

"use strict";



class MainMenu extends Menu
{
    constructor(curtain=null)
    {
        super(["frame", "opaque"], "MainMenu");

        this.curtain     = curtain;
        if(this.curtain)
            this.curtain.AddClickEvent(()=>{this.HideMenu();});

        this._AddFullscreenSwitch();
        this._AddModeSwitch();
        this._AddReloadButton();
        this._AddSettingsButton();
        this._AddAboutButton();
        this._AddDisconnectSwitch();

        // Clicks propagated through Buttons and Switches shall lead to closing the menu
        this.element.onclick = ()=>{this.HideMenu();};
    }



    HideMenu()
    {
        if(this.curtain)
            this.curtain.Hide();
        super.HideMenu();
    }

    ShowMenu()
    {
        if(this.curtain)
            this.curtain.Show();
        super.ShowMenu();
    }



    _AddFullscreenSwitch()
    {
        this.AddSwitch("fullscreen",
            new SVGIcon("EnterFullscreen"),
            "Enter Fullscreen",
            ()=>
            {
                WebUI.GetManager("Fullscreen").EnterFullscreen();
            },
            "Switch browser into fullscreen mode",

            new SVGIcon("LeaveFullscreen"),
            "Leave Fullscreen",
            ()=>
            {
                WebUI.GetManager("Fullscreen").LeaveFullscreen();
            },
            "Switch browser into window mode");
    }
    
    _AddModeSwitch()
    {
        this.AddSwitch("modeswitch",
            new SVGIcon("Switch2Video"),
            "Switch to Video Mode",
            ()=>
            {
                WebUI.GetManager("MusicMode").SetVideoMode();
            },
            "Switch MusicDB WebUI to Video Mode",

            new SVGIcon("Switch2Audio"),
            "Switch to Audio Mode",
            ()=>
            {
                WebUI.GetManager("MusicMode").SetAudioMode();
            },
            "Switch MusicDB WebUI to Audio Mode");
    }

    _AddReloadButton()
    {
        this.AddButton("reload",
            new SVGIcon("Reload"),
            "Reload Artists",
            ()=>
            {
                let musicmode = WebUI.GetManager("MusicMode").GetCurrentMode();
                if(musicmode == "audio")
                    MusicDB_Request("GetFilteredArtistsWithAlbums", "ShowArtists");
                else
                    MusicDB_Request("GetFilteredArtistsWithVideos", "ShowArtists");
            },
            "Reload list with artists and their albums/videos");
    }

    _AddSettingsButton()
    {
        this.AddButton("settings",
            new SVGIcon("Settings"),
            "MusicDB Manager",
            ()=>
            {
                leftviewmanager.ShowSettingsMenu();
                mainviewmanager.ShowAboutMusicDB(); // TODO: Show a different view
            },
            "Show Settings and Management Tools for the WebUI and Music Content");
    }

    _AddAboutButton()
    {
        this.AddButton("about",
            new SVGIcon("MusicDB"),
            "About MusicDB",
            ()=>
            {
                mainviewmanager.ShowAboutMusicDB();
            },
            "Show information about MusicDB including version numbers");
    }

    _AddDisconnectSwitch()
    {
        this.AddSwitch("disconnect",
            new SVGIcon("Disconnect"),
            "Disconnect",
            ()=>
            {
                DisconnectFromMusicDB();
            },
            "Close connection to the MusicDB WebSocket Server",

            new SVGIcon("Reconnect"),
            "Reconnect",
            ()=>
            {
                ConnectToMusicDB();
            },
            "Reconnect to the MusicDB WebSocket Server");
    }


    /* Templates
    _AddReloadButton()
    {
        this.AddButton("",
            new SVGIcon(""),
            "",
            ()=>
            {
            },
            "");
    }

    _AddModeSwitch()
    {
        this.AddSwitch("",
            new SVGIcon(""),
            "",
            ()=>
            {
            },
            "",

            new SVGIcon(""),
            "",
            ()=>
            {
            },
            "");
    }
    */



    onMusicDBMessage(fnc, sig, args, pass)
    {
        if(fnc == "LoadWebUIConfiguration" || sig == "UpdateConfig")
        {
            if(args.WebUI.videomode == "enabled")
                this.ShowEntry("modeswitch");
            else
                this.HideEntry("modeswitch");

            if(args.WebUI.showstreamplayer == true)
                this.ShowSection("Audio Stream");
            else
                this.HideSection("Audio Stream");
        }

        return;
    }
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

