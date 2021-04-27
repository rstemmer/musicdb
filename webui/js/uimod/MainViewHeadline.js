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

class SimpleMainViewHeadline extends Element
{
    constructor(text=null)
    {
        super("div", ["MainViewHeadline", "flex"]);

        // Main Headline
        this.headline = document.createElement("span");
        this.headline.classList.add("fgcolor");

        if(typeof text === "string")
            this.UpdateRawInformation(text);

        this.element.appendChild(this.headline);
    }



    UpdateRawInformation(headlinetext)
    {
        this.headline.innerText = headlinetext;
        return;
    }
}



class SettingsHeadline extends SimpleMainViewHeadline
{
    constructor(headlinetext=null, infotext=null)
    {
        super(headlinetext);
        this.element.classList.add("flex-column");

        this.infoelement = document.createElement("span");
        this.infoelement.classList.add("hlcolor");
        this.infoelement.classList.add("smallfont");

        if(typeof infotext === "string")
            this.infoelement.innerText = infotext;

        this.element.appendChild(this.infoelement);
    }
}



/* Layout:
 *
 *   headline                       button box
 *   subtitle 1 - subtitle 2
 */

class MainViewHeadline extends Element
{
    constructor(buttonarray)
    {
        super("div", ["MainViewHeadline", "flex-row"]);

        // Info box
        this.infobox    = document.createElement("div");

        // Main Headline
        this.headline   = document.createElement("span");
        this.headline.classList.add("fgcolor");

        // Subtitle 1
        this.sub1       = document.createElement("span");
        this.sub1.classList.add("hlcolor");
        this.sub1.classList.add("smallfont");

        // Spacer between Artist and Release Year
        this.spacer      = document.createElement("span");
        this.spacer.classList.add("fgcolor");
        this.spacer.classList.add("smallfont");
        this.spacer.innerText = " — "; // EM DASH

        // Subtitle 2
        this.sub2       = document.createElement("span");
        this.sub2.classList.add("hlcolor");
        this.sub2.classList.add("smallfont");

        // Info Box for Names
        this.infobox.appendChild(this.headline);
        this.infobox.appendChild(this.sub1);
        this.infobox.appendChild(this.spacer);
        this.infobox.appendChild(this.sub2);

        // Button box
        this.buttonbox  = document.createElement("div");
        this.buttonbox.classList.add("flex-row");
        this.buttonbox.classList.add("hovpacity");
        if(buttonarray != null)
        {
            for(let button of buttonarray)
            {
                this.buttonbox.appendChild(button.GetHTMLElement());
            }
        }

        // Full headline
        this.element.appendChild(this.infobox);
        this.element.appendChild(this.buttonbox);
    }



    /*
     * MDBMusic must provide the following attributes:
     *  · MDBMusic.name
     *  · MDBMusic.release
     *  · MDBMusic.origin
     *  · MDBMusic.added (optional)
     *
     *  This is usually provided by MDBArtist and MDBAlbum
     */
    UpdateInformation(MDBMusic, MDBArtist)
    {
        let tooltip = "";
        tooltip += `Origin: ${MDBMusic.origin}`;

        if("added" in MDBMusic)
        {
            let dateoptions = {year: "numeric", month: "long", day: "numeric"};
            let dateobject  = new Date(MDBMusic.added * 1000);
            let datestring  = dateobject.toLocaleDateString(undefined, dateoptions); // Undefined locale string: browsers locale
            tooltip += `\nAdded: ${datestring}`;
        }

        this.UpdateRawInformation(MDBMusic.name, MDBArtist.name, MDBMusic.release, tooltip);
        return;
    }



    UpdateRawInformation(headlinetext, sub1, sub2, tooltip)
    {
        this.headline.innerText = headlinetext;
        this.sub1.innerText     = sub1;
        this.sub2.innerText     = sub2;
        this.infobox.title      = tooltip;
        return;
    }



    SetRightClickCallback(callback)
    {
        this.element.oncontextmenu = callback;
        return;
    }



    SetSubtitleClickAction(onsub1, onsub2)
    {
        if(typeof onsub1 === "function")
            this.sub1.onclick = onsub1;
        if(typeof onsub2 === "function")
            this.sub2.onclick = onsub2;
        return;
    }

}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

