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

// All statuses can have the value:
//
// CSS Data-Set | State name
// -------------+-----------------------------------
// "unknown"    | "unknown"
// "good"       | "connected"
// "bad"        | "disconnected"
// "playing"    | "playing"/"streaming"
// "paused"     | "stopped"

class MusicDBStatus
{
    constructor()
    {
        this.musicdbstatus = new Object();
        this.CreateStatus("musicdb",     "MusicDB Server");
        this.CreateStatus("icecast",     "Icecast Server");
        this.CreateStatus("audiostream", "Audio Stream");
        this.CreateStatus("videostream", "Video Stream");

        this.element = document.createElement("div");
        for(let statuskey in this.musicdbstatus)
        {
            let statusentry = this.musicdbstatus[statuskey];
            this.element.appendChild(statusentry.element);
        }

        // Create reconnect button
        this.reconnectbutton  = new SVGButton("Reconnect", ()=>{ConnectToMusicDB();});
        this.reconnectbutton.SetTooltip("Reconnect to MusicDB server");
        this.reconnectelement = this.reconnectbutton.GetHTMLElement();
        this.reconnectelement.id = "MDBReconnectButton";
        this.reconnectelement.dataset.visible = false;


        return;
    }



    GetHTMLElement()
    {
        return this.element;
    }

    GetReconnectButtonHTMLElement()
    {
        return this.reconnectelement;
    }



    CreateStatus(key, name)
    {
        this.musicdbstatus[key] = new Object();
        this.musicdbstatus[key].name    = name;
        this.musicdbstatus[key].state   = "unknown";
        this.musicdbstatus[key].element = document.createElement("div");
        this.musicdbstatus[key].element.innerText     = name;
        this.musicdbstatus[key].element.dataset.state = "unknown";
        return;
    }


    SetStatus(key, state)
    {
        if(typeof state !== "string")
            return;

        if(state == "hide")
        {
            this.musicdbstatus[key].element.style.display = "none";
            return;
        }
        else if(state == "show")
        {
            this.musicdbstatus[key].element.style.display = "block";
            return;
        }

        let cssstatename = "unknown";

        if(state == "connected")
        {
            cssstatename = "good";
        }
        else if(state == "playing"
             || state == "streaming")
        {
            cssstatename = "playing";
        }
        else if(state == "disconnected")
        {
            cssstatename = "bad";
        }
        else if(state == "stopped")
        {
            cssstatename = "paused";
        }
        else if(state == "unknown")
        {
            cssstatename = "unknown";
        }
        else
        {
            window.console && console.log("Unknown " + key + " Status " + state);
        }

        // Show / Hide reconnect button
        if(key == "musicdb")
        {
            if(state == "connected")
                this.reconnectelement.dataset.visible = false;
            else
                this.reconnectelement.dataset.visible = true;
        }

        // Apply status
        this.musicdbstatus[key].element.dataset.state = cssstatename;
        return;
    }



    onMusicDBNotification(fnc, sig, rawdata)
    {
        this.SetStatus("musicdb", "connected");
        return;
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        this.SetStatus("musicdb", "connected");

        if(fnc == "GetAudioStreamState")
        {
            if(args.isconnected)
                this.SetStatus("icecast", "connected");
            else
                this.SetStatus("icecast", "disconnected");

            if(args.isplaying)
                this.SetStatus("audiostream", "playing");
            else
                this.SetStatus("audiostream", "stopped");
        }

        else if(fnc == "GetVideoStreamState")
        {
            if(args.isstreaming)
                this.SetStatus("videostream", "playing");
            else
                this.SetStatus("videostream", "stopped");
        }

        else if(fnc == "LoadWebUIConfiguration" || sig == "UpdateConfig")
        {
            if(args.WebUI.videomode == "enabled")
                this.SetStatus("videostream", "show");
            else
                this.SetStatus("videostream", "hide");
        }
        return;
    }


    onMusicDBConnectionOpen()
    {
        this.SetStatus("musicdb",     "connected");
    }
    onMusicDBConnectionError()
    {
        this.SetStatus("musicdb",     "disconnected");
        this.SetStatus("icecast",     "unknown");
        this.SetStatus("audiostream", "unknown");
        this.SetStatus("videostream", "unknown");
    }
    onMusicDBWatchdogBarks()
    {
        this.SetStatus("musicdb",     "disconnected");
        this.SetStatus("icecast",     "unknown");
        this.SetStatus("audiostream", "unknown");
        this.SetStatus("videostream", "unknown");
    }
    onMusicDBConnectionClosed()
    {
        this.SetStatus("musicdb",     "disconnected");
        this.SetStatus("icecast",     "unknown");
        this.SetStatus("audiostream", "unknown");
        this.SetStatus("videostream", "unknown");
    }
}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

