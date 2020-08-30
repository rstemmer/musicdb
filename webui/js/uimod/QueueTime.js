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

class QueueTime
{
    constructor()
    {
        this.totaltime  = 0; // total playtime of all songs in the queue
        this.playedtime = 0; // time the first song in the queue was played
    }

    AddTime(time)
    {
        this.totaltime += time;
    }
    ClearTime()
    {
        this.totaltime = 0;
    }



    SetTimePlayed(playedtime)
    {
        this.playedtime = playedtime;
    }



    GetCurrentTimeString()
    {
        // Get current time
        let date = new Date();

        let h = date.getHours();
        let m = date.getMinutes();
        let s = date.getSeconds();

        // convert to string
        let currenttime = HMSToString( h,  m,  s);
        return currenttime;
    }



    GetQueueEndTimeString()
    {
        // Get current time
        let date = new Date();

        let h = date.getHours();
        let m = date.getMinutes();
        let s = date.getSeconds();

        // Calculate estimated end time (hours, minutes and seconds)
        let es, em, eh;
        es = s + this.totaltime - this.playedtime;
        em = m + Math.floor(es / 60);
        es = Math.floor(es % 60);
        eh = h + Math.floor(em / 60);
        em = Math.floor(em % 60);
        eh = Math.floor(eh % 24);

        // convert to string
        let endtime = HMSToString(eh, em, es);
        return endtime;
    }
}



class QueueTimeManager
{
    constructor()
    {
        // The queue time objects should be considered as public
        // Any external program code is allowed to access those methods
        this.audioqueuetime = new QueueTime();
        this.videoqueuetime = new QueueTime();

        this.element            = document.createElement("div");
        this.currenttimeelement = document.createElement("span");
        this.queuetimeelement   = document.createElement("span");
        this.separatorelement   = document.createElement("span");
        this.separatorelement.innerText = " / ";
        this.element.appendChild(this.currenttimeelement);
        this.element.appendChild(this.separatorelement);
        this.element.appendChild(this.queuetimeelement);
    }



    GetHTMLElement()
    {
        return this.element;
    }


    AddTime(queuetype, time)
    {
        if(queuetype == "audio")
            this.audioqueuetime.AddTime(time);
        else if(queuetype == "video")
            this.videoqueuetime.AddTime(time);

        return;
    }

    ClearTime(queuetype)
    {
        if(queuetype == "audio")
            this.audioqueuetime.ClearTime();
        else if(queuetype == "video")
            this.videoqueuetime.ClearTime();

        return;
    }

    SetTimePlayed(queuetype, time)
    {
        if(queuetype == "audio")
            this.audioqueuetime.SetTimePlayed(time);
        else if(queuetype == "video")
            this.videoqueuetime.SetTimePlayed(time);

        this.UpdateElement();
        return;
    }


    
    UpdateElement()
    {
        let mode = mdbmodemanager.GetCurrentMode();

        if(mode == "audio")
        {
            this.currenttimeelement.innerText = this.audioqueuetime.GetCurrentTimeString();
            this.queuetimeelement.innerText   = this.audioqueuetime.GetQueueEndTimeString();
        }
        else if(mode == "video")
        {
            this.currenttimeelement.innerText = this.videoqueuetime.GetCurrentTimeString();
            this.queuetimeelement.innerText   = this.videoqueuetime.GetQueueEndTimeString();
        }

        return;
    }



    onMusicDBNotification(fnc, sig, rawdata)
    {
        if(sig == "onTimeChanged")
        {
            // rawdata is the currently played time of the current song
            // this method gets called every second by the audio streaming thread of MusicDB
            // This also updated the QueueTimeBar
            queuetimemanager.SetTimePlayed("audio", rawdata);
        }
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



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

