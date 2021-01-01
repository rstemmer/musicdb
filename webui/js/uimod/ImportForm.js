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


class ImportForm extends Element
{
    constructor(formtable, onsavedraft, onimportfile)
    {
        super("div", ["ImportForm", "flex-row"]);

        let rightcolumn = document.createElement("div");
        rightcolumn.classList.add("flex-column");

        if(typeof onsavedraft === "function")
        {
            let savebutton   = new SVGButton("Save",    onsavedraft);
            rightcolumn.appendChild(savebutton.GetHTMLElement());
        }
        if(typeof onimportfile === "function")
        {
            let importbutton = new SVGButton("MusicDB", onimportfile);
            rightcolumn.appendChild(importbutton.GetHTMLElement());
        }

        this.element.appendChild(formtable.GetHTMLElement());
        this.element.appendChild(rightcolumn);
    }
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

