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


class List extends Element
{
    constructor(classes=[])
    {
        super("div", ["List", "flex-column", "frame", ...classes]);
        this.entries = new Array();
    }



    Clear()
    {
        this.entries = new Array();
        super.Clear();
    }



    // entry: Element instance
    AddEntry(entry)
    {
        this.entries.push(entry);
        this.AppendChild(entry);
    }



    RemoveEntry(entry)
    {
        let htmlelement = entry.GetHTMLElement();

        // Remove entry from the DOM
        htmlelement.remove();

        // Remove rows from the internal array
        let index = this.entries.indexOf(entry);
        if(index > -1)
            this.entries.splice(index, 1);

        return;
    }
}



class ListElement extends Element
{
    constructor(classes, id=null)
    {
        super("div", ["ListEntry", "hoverframe", ...classes], id);
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

