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



class GenreListEditor extends Element
{
    // headliner: string
    // addhandler: function called when new tag shall be added - parameter is an object describing the tag
    constructor(headline, addhandler)
    {
        super("div", ["GenreListEditor", "flex-column"]);

        this.addhandler = addhandler;

        this.headelement  = document.createElement("span");
        this.headelement.classList.add("flex-center");
        this.headelement.innerText = headline;

        this.listelement  = document.createElement("div");
        this.listelement.classList.add("flex-column");
        this.listelement.classList.add("flex-grow");
        this.listelement.classList.add("frame");

        this.inputbar     = document.createElement("div");
        this.inputbar.classList.add("inputbar");
        this.inputbar.classList.add("flex-row");

        this.inputelement = document.createElement("input");
        this.inputelement.classList.add("flex-grow");
        this.addbutton    = new SVGButton("Add", ()=>{this.onClick();});

        this.inputbar.appendChild(this.inputelement);
        this.inputbar.appendChild(this.addbutton.GetHTMLElement());

        this.element.appendChild(this.headelement);
        this.element.appendChild(this.listelement);
        this.element.appendChild(this.inputbar);
    }



    onClick()
    {
        if(typeof this.addhandler != "function")
            return;

        // TODO: Create tag
        let tag;

        this.addhandler(tag);
    }



    UpdateList(genres)
    {
        return;
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

