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

class Grid
{
    constructor(columns, rows)
    {
        this.rows         = rows;
        this.columns      = columns;
        this.tableelement = document.createElement("table");
        this.tableelement.classList.add("grid-table");
        
        this.tablecells   = new Array(); // cells[rows][columns]
        for(let y=0; y<rows; y++)
        {
            let rowelement = document.createElement("tr");
            rowelement.classList.add("grid-row");

            let tablecolumns = new Array();
            for(let x=0; x<columns; x++)
            {
                let cell = new Element("td", ["grid-cell"]);
                rowelement.appendChild(cell.GetHTMLElement());
                tablecolumns.push(cell.GetHTMLElement());
            }

            this.tableelement.appendChild(rowelement);
            this.tablecells.push(tablecolumns);
        }
    }



    GetHTMLElement()
    {
        return this.tableelement;
    }



    InsertElement(column, row, element)
    {
        if(row >= this.rows)
            return;
        if(column >= this.columns)
            return;

        this.tablecells[row][column].innerHTML = "";
        this.tablecells[row][column].appendChild(element);
        return;
    }

    InsertText(column, row, string)
    {
        let textelement       = document.createElement("span");
        textelement.innerText = string;
        this.InsertElement(column, row, textelement);
    }

    InsertLink(column, row, name, url, target)
    {
        let linkelement       = document.createElement("a");
        linkelement.innerText = name;
        linkelement.href      = url;
        linkelement.target    = target;
        this.InsertElement(column, row, linkelement);
    }



    MergeRow(row)
    {
        this.tablecells[row][0].colSpan = this.columns;
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

