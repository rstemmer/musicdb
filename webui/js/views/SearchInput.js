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

class SearchInput
{
    constructor()
    {
        this.element = document.createElement("div");
        this.element.classList.add("flex-row");
        this.element.classList.add("hlcolor");
        this.element.classList.add("hovpacity");
        this.element.classList.add("SearchInput");
        this._AddInputBoxElements();
    }



    _AddInputBoxElements()
    {
        this.icon        = new SVGIcon("MusicDB");
        
        this.clearbutton = new SVGButton("Remove", ()=>{this.ClearInput();});
        this.clearbutton.GetHTMLElement().classList.add("hovpacity");

        this.input       = document.createElement("input");
        this.input.onInput     = ()=>{onInput(event);};
        this.input.onKeyup     = ()=>{onKeyUp(event);};
        this.input.onClick     = ()=>{onClick(event);};
        this.input.type        = "search";
        this.input.placeholder = "Search…";

        this.element.appendChild(this.icon.GetHTMLElement());
        this.element.appendChild(this.input);
        this.element.appendChild(this.clearbutton.GetHTMLElement());
        return;
    }



    GetHTMLElement()
    {
        return this.element;
    }



    ClearInput()
    {
        return;
    }



    // Events from the text input element
    onInput(event)
    {
    }
    onKeyUp(event)
    {
    }
    onClick(event)
    {
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        return;
    }
}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

