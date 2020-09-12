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

class QueueControlView
{
    constructor()
    {
        this.element = document.createElement("div");
        this.label   = document.createElement("label");
        this.buttons = new ButtonBox_QueueControls();
        this.element.classList.add("QueueControlView");
        this.element.classList.add("hlcolor");
        this.element.classList.add("hovpacity");
        this.element.appendChild(this.label);
        this.element.appendChild(this.buttons.GetHTMLElement());
    }



    Update()
    {
        let musictype = mdbmodemanager.GetCurrentMode();
        let label     = null;
        if(musictype == "audio")
        {
            label = "Add Random Song:";
        }
        else if(musictype == "video")
        {
            label = "Add Random Video:";
        }

        this.label.innerText = label;
        this.buttons.UpdateTooltips();
        return;
    }



    GetHTMLElement()
    {
        return this.element;
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

