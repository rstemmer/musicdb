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


class MainViewHeadline
{
    constructor(buttonarray)
    {
        // Info box
        this.infobox        = document.createElement("div");

        // Content Name
        this.contentname    = document.createElement("span");
        this.contentname.classList.add("fgcolor");

        // Artist Name
        this.artistname     = document.createElement("span");
        this.artistname.classList.add("hlcolor");
        this.artistname.classList.add("smallfont");

        // Spacer between Artist and Release Year
        this.spacer         = document.createElement("span");
        this.spacer.classList.add("fgcolor");
        this.spacer.classList.add("smallfont");
        this.spacer.innerText = " — "; // EM DASH

        // Release Year
        this.releaseyear    = document.createElement("span");
        this.releaseyear.classList.add("hlcolor");
        this.releaseyear.classList.add("smallfont");

        // Info Box for Names
        this.infobox.appendChild(this.contentname);
        this.infobox.appendChild(this.artistname);
        this.infobox.appendChild(this.spacer);
        this.infobox.appendChild(this.releaseyear);

        // Button box
        this.buttonbox      = document.createElement("div");
        this.buttonbox.classList.add("flex-row");
        this.buttonbox.classList.add("hovpacity");
        for(let button of buttonarray)
        {
            this.buttonbox.appendChild(button.GetHTMLElement());
        }

        // Full headline
        this.element = document.createElement("div");
        this.element.classList.add("mainview_headline");
        this.element.classList.add("flex-row");
        this.element.appendChild(this.infobox);
        this.element.appendChild(this.buttonbox);
    }

    GetHTMLElement()
    {
        return this.element;
    }



    /*
     * MDBMusic must provide the following attributes:
     *  · MDBMusic.name
     *  · MDBMusic.release
     *  · MDBMusic.origin
     */
    UpdateInformation(MDBMusic, MDBArtist)
    {
        this.contentname.innerText  = MDBMusic.name;
        this.artistname.innerText   = MDBArtist.name
        this.releaseyear.innerText  = MDBMusic.release;
        this.infobox.title          = MDBMusic.origin;
    }



    SetRightClickCallback(callback)
    {
        this.element.oncontextmenu = callback;
    }

}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

