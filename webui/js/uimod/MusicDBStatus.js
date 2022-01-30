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

"use strict";

// All statuses can have the value:
//
// CSS Data-Set | State name
// -------------+-----------------------------------
// "unknown"    | "unknown"
// "good"       | "connected"
// "bad"        | "disconnected"
// "playing"    | "playing"/"streaming"
// "paused"     | "stopped"

class MusicDBStatus extends StatusList
{
    constructor()
    {
        super();
        this.AddState("musicdb",     "MusicDB Server");
        this.AddState("icecast",     "Icecast Server");
        this.AddState("audiostream", "Audio Stream");
        this.AddState("videostream", "Video Stream");

        return;
    }



    SetMusicDBStatus(statename, state)
    {
        if(typeof state !== "string")
            return;

        if(state == "hide")
        {
            this.states[statename].Hide();
            return;
        }
        else if(state == "show")
        {
            this.states[statename].Show();
            return;
        }

        // Translate MusicDB States to css data properties values
        let cssname = "unknown";
        switch(state)
        {
            case "connected":    cssname = "good";    break;
            case "disconnected": cssname = "bad";     break;
            case "playing":      cssname = "playing"; break;
            case "streaming":    cssname = "playing"; break;
            case "stopped":      cssname = "paused";  break;
            case "unknown":      cssname = "unknown"; break;
            default:
                window.console && console.warn("Unknown " + statename + " Status " + state);
        }

        // Show / Hide reconnect button
        if(statename == "musicdb")
        {
            let mainmenu = WebUI.GetLayer("MainMenu");
            if(state == "connected")
            {
                if(typeof mainmenu === "object")
                    mainmenu.SwitchEntry("disconnect", "a"); // Show Disconnect Entry
            }
            else
            {
                if(typeof mainmenu === "object")
                    mainmenu.SwitchEntry("disconnect", "b"); // Show Reconnect Entry
            }
        }

        // Apply status
        super.SetState(statename, cssname);
        return;
    }



    onMusicDBNotification(fnc, sig, rawdata)
    {
        this.SetMusicDBStatus("musicdb", "connected");
        return;
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        this.SetMusicDBStatus("musicdb", "connected");

        if(fnc == "GetAudioStreamState")
        {
            if(args.isconnected)
                this.SetMusicDBStatus("icecast", "connected");
            else
                this.SetMusicDBStatus("icecast", "disconnected");

            if(args.isplaying)
                this.SetMusicDBStatus("audiostream", "playing");
            else
                this.SetMusicDBStatus("audiostream", "stopped");
        }

        else if(fnc == "GetVideoStreamState")
        {
            if(args.isstreaming)
                this.SetMusicDBStatus("videostream", "playing");
            else
                this.SetMusicDBStatus("videostream", "stopped");
        }

        else if(fnc == "LoadWebUIConfiguration" || sig == "UpdateConfig")
        {
            if(args.WebUI.videomode == "enabled")
                this.SetMusicDBStatus("videostream", "show");
            else
                this.SetMusicDBStatus("videostream", "hide");
        }
        return;
    }


    onMusicDBConnectionOpen()
    {
        this.SetMusicDBStatus("musicdb",     "connected");
    }
    onMusicDBConnectionError()
    {
        this.SetMusicDBStatus("musicdb",     "disconnected");
        this.SetMusicDBStatus("icecast",     "unknown");
        this.SetMusicDBStatus("audiostream", "unknown");
        this.SetMusicDBStatus("videostream", "unknown");
    }
    onMusicDBWatchdogBarks()
    {
        this.SetMusicDBStatus("musicdb",     "disconnected");
        this.SetMusicDBStatus("icecast",     "unknown");
        this.SetMusicDBStatus("audiostream", "unknown");
        this.SetMusicDBStatus("videostream", "unknown");
    }
    onMusicDBConnectionClosed()
    {
        this.SetMusicDBStatus("musicdb",     "disconnected");
        this.SetMusicDBStatus("icecast",     "unknown");
        this.SetMusicDBStatus("audiostream", "unknown");
        this.SetMusicDBStatus("videostream", "unknown");
    }
}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

