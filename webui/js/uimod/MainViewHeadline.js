// MusicDB,  a music manager with web-bases UI that focus on music.
// Copyright (C) 2017 - 2021  Ralf Stemmer <ralf.stemmer@gmx.net>
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
    constructor(text="")
    {
        super("div", ["MainViewHeadline", "flex"]);

        // Main Headline
        this.headline = new Element("span", ["fgcolor"]);
        this.headline.SetInnerText(text);

        this.AppendChild(this.headline);
    }



    UpdateRawInformation(headlinetext)
    {
        this.headline.SetInnerText(headlinetext);
        return;
    }



    SetRightClickCallback(callback)
    {
        this.element.oncontextmenu = callback;
        return;
    }
}



class SettingsHeadline extends SimpleMainViewHeadline
{
    constructor(headlinetext="", infotext="")
    {
        super(headlinetext);
        this.AddCSSClass("flex-column");

        this.infoelement = new Element("span", ["hlcolor", "smallfont"]);
        this.infoelement.SetInnerText(infotext);

        this.AppendChild(this.infoelement);
    }
}



class LayerHeadline extends SettingsHeadline
{
    constructor(headlinetext="", infotext="")
    {
        super(headlinetext, infotext);
    }
}



/* Layout:
 *
 *   headline                       button box
 *   subtitle 1 - subtitle 2
 */

class MainViewHeadline extends SimpleMainViewHeadline
{
    constructor(buttonarray)
    {
        super();
        this.AddCSSClass("flex-row");

        // Info Box Elements
        this.infobox    = new Element("div");
        this.headline   = new Element("span", ["fgcolor"]);                 // Main Headline
        this.sub1       = new Element("span", ["hlcolor", "smallfont"]);    // Subtitle 1
        this.spacer     = new Element("span", ["fgcolor", "smallfont"]);    // Spacer between Artist and Release Year
        this.spacer.SetInnerText(" — "); // EM DASH
        this.sub2       = new Element("span", ["hlcolor", "smallfont"]);    // Subtitle 2

        // Assemble Info Box for Names
        this.infobox.AppendChild(this.headline);
        this.infobox.AppendChild(this.sub1);
        this.infobox.AppendChild(this.spacer);
        this.infobox.AppendChild(this.sub2);

        // Button box
        this.buttonbox  = new Element("div", ["flex-row", "hovpacity"]);
        if(buttonarray != null)
        {
            for(let button of buttonarray)
            {
                this.buttonbox.AppendChild(button);
            }
        }

        // Full headline
        this.RemoveChilds();
        this.AppendChild(this.infobox);
        this.AppendChild(this.buttonbox);
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
        this.headline.SetInnerText(headlinetext);
        this.sub1.SetInnerText(sub1);
        this.sub2.SetInnerText(sub2);
        this.infobox.SetTooltip(tooltip);
        return;
    }



    SetSubtitleClickAction(onsub1, onsub2)
    {
        if(typeof onsub1 === "function")
            this.sub1.SetClickEventCallback(onsub1);
        if(typeof onsub2 === "function")
            this.sub2.SetClickEventCallback(onsub2);
        return;
    }

}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

