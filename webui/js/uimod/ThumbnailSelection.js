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



class ThumbnailSelection
{
    constructor(videoplayer, MDBVideo)
    {
        this.videoplayer        = videoplayer;
        this.videoid            = MDBVideo.id;
        this.vbegin             = MDBVideo.vbegin;
        this.vend               = MDBVideo.vend;
        this.vplaytime          = MDBVideo.playtime;

        this.timeselect         = new TimeSelect("Select Frame", this.videoplayer, this.vbegin, "vThis");

        this.savebutton         = new SVGButton("Save", ()=>{this.onSave();});
        this.savebutton.SetTooltip("Save selected time frame at MusicDB server");
        /*
        this.loadbutton         = new SVGButton("Load", ()=>{this.onLoad();});
        this.loadbutton.SetTooltip("Load and reset selected time frame from MusicDB server");
        */

        this.savestate          = document.createElement("div");
        this.savestate.classList.add("vtfs_savestate");
        this.SetSaveState("unchanged");

        this.element            = document.createElement("div");
        this.element.classList.add("videotimeframeselection");
        this.element.classList.add("flex-column");
        this.element.classList.add("frame");

        this.controlboxrow      = document.createElement("div");
        this.controlboxrow.classList.add("flex-row");
        this.controlboxrow.classList.add("vtfs_controlbox");
        this.controltitle       = document.createElement("span");
        this.controltitle.innerText = "Select Thumb Nail Image";
        this.controlboxrow.appendChild(this.controltitle);
        this.controlboxrow.appendChild(this.savestate);
        /*
        this.controlboxrow.appendChild(this.loadbutton.GetHTMLElement());
        */
        this.controlboxrow.appendChild(this.savebutton.GetHTMLElement());

        this.timeselectrow      = document.createElement("div");
        this.timeselectrow.classList.add("flex-row");
        this.timeselectrow.classList.add("vtfs_timeselection");
        this.timeselectrow.appendChild(this.timeselect.GetHTMLElement());

        this.element.appendChild(this.controlboxrow);
        this.element.appendChild(this.timeselectrow);

        this.timeselect.SetValidationFunction((time)=>{this._UpdateSaveState(time); return true;});
    }



    GetHTMLElement()
    {
        return this.element;
    }



    // Call this after the element is append to the DOM
    Initialize()
    {
        this.timeselect.Reset();
        this.SetSaveState("unchanged");
    }



    SetSaveState(state)
    {
        if(state == "notsaved")
        {
            this.savestate.dataset.state = "notsaved";
            this.savestate.innerText     = "Changes not yet saved!";
        }
        else if(state == "unchanged")
        {
            this.savestate.dataset.state = "unchanged";
            this.savestate.innerText     = "";
        }
        else if(state == "saved")
        {
            this.savestate.dataset.state = "saved";
            this.savestate.innerText     = "Changes sucessfully saved.";
        }

    }



    _UpdateSaveState(time)
    {
        this.SetSaveState("notsaved");
        return;
    }



    onSave()
    {
        let timestamp = this.timeselect.GetSelectedTime();

        this.SetSaveState("saved");

        MusicDB_Call("SetVideoThumbnail", 
            {
                videoid:   this.videoid,
                timestamp: timestamp
            });
    }

    /*
    onLoad()
    {
        this.timeselect.SetNewTime(this.vbegin);
    }
    */
}
// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

