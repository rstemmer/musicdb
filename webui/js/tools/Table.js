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


class Table extends Element
{
    constructor(classes=[])
    {
        super("table", ["Table", ...classes]);
        this.rows = new Array();
    }



    Clear()
    {
        this.rows = new Array();
        this.element.innerHTML = "";
    }



    // tablerow: TableRow object
    AddRow(tablerow)
    {
        this.rows.push(tablerow);
        this.element.appendChild(tablerow.GetHTMLElement());
    }
}



class TableRow extends Element
{
    constructor(numcells, classes)
    {
        super("tr", classes);

        this.cells = new Array();
        for(let i=0; i<numcells; i++)
        {
            let cell = document.createElement("td");
            this.cells.push(cell);
            this.element.appendChild(cell);
        }
    }



    SetContent(cellnum, htmlelement)
    {
        this.cells[cellnum].innerHTML = "";
        this.cells[cellnum].appendChild(htmlelement);
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

