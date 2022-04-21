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


class VideoTimeFrameSelection
{
    constructor(videoplayer, MDBVideo)
    {
        this.videoplayer        = videoplayer;
        this.videoid            = MDBVideo.id;
        this.vbegin             = MDBVideo.vbegin;
        this.vend               = MDBVideo.vend;
        this.vplaytime          = MDBVideo.playtime;

        this.begintimeselect    = new BeginTimeSelect("Video Begin", this.videoplayer, this.vbegin, this.vplaytime, 0);
        this.endtimeselect      = new EndTimeSelect(  "Video End",   this.videoplayer, this.vend,   this.vplaytime, this.vplaytime);

        this.savebutton         = new SVGButton("Save", ()=>{this.onSave();});
        this.savebutton.SetTooltip("Save selected time frame at MusicDB server");
        this.loadbutton         = new SVGButton("Load", ()=>{this.onLoad();});
        this.loadbutton.SetTooltip("Load and reset selected time frame from MusicDB server");

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
        this.controltitle.innerText = "Select time frame that will be played";
        this.controlboxrow.appendChild(this.controltitle);
        this.controlboxrow.appendChild(this.savestate);
        this.controlboxrow.appendChild(this.loadbutton.GetHTMLElement());
        this.controlboxrow.appendChild(this.savebutton.GetHTMLElement());

        this.timeselectrow      = document.createElement("div");
        this.timeselectrow.classList.add("flex-row");
        this.timeselectrow.classList.add("vtfs_timeselection");
        this.timeselectrow.appendChild(this.begintimeselect.GetHTMLElement());
        this.timeselectrow.appendChild(this.endtimeselect.GetHTMLElement());

        this.messageboxrow      = document.createElement("div");
        this.messageboxrow.classList.add("flex-row");
        this.messageboxrow.classList.add("vtfs_messagebox");

        this.errormessage_begin = document.createElement("div");
        this.errormessage_end   = document.createElement("div");
        this.errormessage_begin.classList.add("vtfs_errormessage");
        this.errormessage_end.classList.add("vtfs_errormessage");
        this.ClearErrorMessage("begin");
        this.ClearErrorMessage("end");
        this.messageboxrow.appendChild(this.errormessage_begin);
        this.messageboxrow.appendChild(this.errormessage_end);


        this.element.appendChild(this.controlboxrow);
        this.element.appendChild(this.timeselectrow);
        this.element.appendChild(this.messageboxrow);

        this.begintimeselect.SetValidationFunction((time) => 
            {
                let endtime = this.endtimeselect.GetSelectedTime();
                if(endtime == null)
                    return true;

                this.ClearErrorMessage("begin");

                if(time < 0)
                {
                    this.ShowErrorMessage("begin", "Negative time is not allowed");
                    return false;
                }

                if(time < endtime)
                {
                    this._UpdateSaveState(time, endtime);
                    return true;
                }

                let beginstr = SecondsToTimeString(time);
                let endstr   = SecondsToTimeString(endtime);
                this.ShowErrorMessage("begin", `Invalid time: Begin (${beginstr}) >= End (${endstr}) not allowed`);
                return false;
            }
        );

        this.endtimeselect.SetValidationFunction((time) =>
            {
                let begintime = this.begintimeselect.GetSelectedTime();
                if(begintime == null)
                    return true;

                this.ClearErrorMessage("end");

                if(time < 0)
                {
                    this.ShowErrorMessage("end", "Negative time is not allowed");
                    return false;
                }

                if(time > this.vplaytime)
                {
                    let timestr = SecondsToTimeString(time);
                    let playstr = SecondsToTimeString(this.vplaytime);
                    this.ShowErrorMessage("end", `Invalid time: End (${timestr}) greater than maximum play time (${playstr}) not allowed`);
                    return false;
                }

                if(time > begintime)
                {
                    this._UpdateSaveState(begintime, time);
                    return true;
                }

                let beginstr = SecondsToTimeString(begintime);
                let endstr   = SecondsToTimeString(time);
                this.ShowErrorMessage("end", `Invalid time: End (${endstr}) <= Begin (${beginstr}) not allowed`);
                return false;
            }
        );
    }



    GetHTMLElement()
    {
        return this.element;
    }



    // Call this after the element is append to the DOM
    Initialize()
    {
        this.onLoad();
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

    // do not read newbegin and newend vie GetSelectedTime.
    // This method expects an intermediate selector state from within the validation methon
    _UpdateSaveState(newbegin, newend)
    {
        if(newbegin == this.vbegin && newend == this.vend)
        {
            this.SetSaveState("unchanged");
        }
        else
        {
            this.SetSaveState("notsaved");
        }
        return;
    }



    ShowErrorMessage(side, message)
    {
        let msgbox;
        if(side == "begin")
            msgbox = this.errormessage_begin
        else if(side == "end")
            msgbox = this.errormessage_end
        else
            return;

        msgbox.innerText       = message;
        msgbox.dataset.visible = true;
        return;
    }
    ClearErrorMessage(side)
    {
        let msgbox;
        if(side == "begin")
            msgbox = this.errormessage_begin
        else if(side == "end")
            msgbox = this.errormessage_end
        else
            return;

        msgbox.innerText       = "";
        msgbox.dataset.visible = false;
        return;
    }



    onSave()
    {
        let begintime = this.begintimeselect.GetSelectedTime();
        let endtime   = this.endtimeselect.GetSelectedTime();

        this.vbegin = begintime;
        this.vend   = endtime;
        this.SetSaveState("saved");

        MusicDB.Call("SetVideoTimeFrame", 
            {
                videoid: this.videoid,
                begin:   begintime,
                end:     endtime
            });
    }

    onLoad()
    {
        this.begintimeselect.SetNewTime(this.vbegin);
        this.endtimeselect.SetNewTime(this.vend);
        this.begintimeselect.ValidateNewTime(this.vbegin);
        this.endtimeselect.ValidateNewTime(this.vend);
    }
}
// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

