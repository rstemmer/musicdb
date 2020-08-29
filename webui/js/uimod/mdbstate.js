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
        this.CreateStatus("videoplayer", "Video Player");

        this.element = document.createElement("div");
        for(let statuskey in this.musicdbstatus)
        {
            let statusentry = this.musicdbstatus[statuskey];
            this.element.appendChild(statusentry.element);
        }

        return;
    }



    GetHTMLElement()
    {
        return this.element;
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

        let cssstatename = "unknwon";

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
        else
        {
            window.console && console.log("Unknown MusicDB Status " + state);
        }

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

            /*
            if(args.isplaying)
                this.SetStatus("videoplayer", "playing");
            else
                this.SetStatus("videoplayer", "stopped");
            */
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




function ShowMusicDBStateView(parentID)
{
    let html = "";

    html += "<div id=MDBStateView class=\"hlcolor smallfont\">";

    // Playtime
    html += "<span id=CurrentTime class=\"timestats\" data-playstate=\"unknown\">";
    html += "00:00:00";
    html += "</span>";
    html += " / ";
    html += "<span id=PlayTime class=\"timestats\" data-playstate=\"unknown\">";
    html += "00:00:00";
    html += "</span>";

    html += "</div>";
    
    // Create Elements
    document.getElementById(parentID).innerHTML = html;
}



var GLOBAL_TotalPlaytime = 0;   // total playtime of all songs in the queue
var GLOBAL_TimePlayed    = 0;   // time the first song in the queue was played

function AddPlaytime(playtime)
{
    GLOBAL_TotalPlaytime += playtime;
}

function ClearPlaytime()
{
    GLOBAL_TotalPlaytime = 0;
}

function SetTimePlayed(played)
{
    GLOBAL_TimePlayed = played;
    // Ugly but works fine for now.
    // SetTimePlayed gets called by the websocket handler. 
    // The server sends every second the current state of the currently playing song.
    // So this function gets called every second independent if the song is playing or not.
    UpdateTimeview();
}

function UpdateTimeview()
{
    // Get current time
    let date = new Date();

    let h = date.getHours();
    let m = date.getMinutes();
    let s = date.getSeconds();

    // Calculate estimated end time (hours, minutes and seconds)
    let es, em, eh;
    es = s + GLOBAL_TotalPlaytime - GLOBAL_TimePlayed;
    em = m + Math.floor(es / 60);
    es = Math.floor(es % 60);
    eh = h + Math.floor(em / 60);
    em = Math.floor(em % 60);
    eh = Math.floor(eh % 24);

    // convert to string
    let currenttime = HMSToString( h,  m,  s);
    let endtime     = HMSToString(eh, em, es);

    // Display time
    let ctimeelement = document.getElementById("CurrentTime");
    let ptimeelement = document.getElementById("PlayTime");
    ctimeelement.innerHTML = currenttime;
    ptimeelement.innerHTML = endtime;
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

