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



    AddContextView(htmlelement)
    {
        let lastrow    = this.rows[this.rows.length - 1];
        let tablewidth = lastrow.cells.length;
        let contextrow = new TableSpanRow(tablewidth, ["ContextRow"], htmlelement);

        // Show/Hide on right click on previous cell
        contextrow.Hide();
        lastrow.GetHTMLElement().oncontextmenu = (event)=>
            {
                event.preventDefault();
                event.stopPropagation();
                for(let row of this.rows)
                {
                    if(row.element.classList.contains("ContextRow") && row != contextrow)
                        row.Hide();
                }
                contextrow.ToggleVisibility();
            };

        // Add row
        this.AddRow(contextrow);
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



    Show()
    {
        this.element.style.display = "table-row";
    }
    Hide()
    {
        this.element.style.display = "none";
    }
    ToggleVisibility()
    {
        if(this.element.style.display == "none")
            this.Show();
        else
            this.Hide();
    }
}



class TableSpanRow extends TableRow
{
    constructor(numcells, classes=[], htmlcontent)
    {
        super(1, classes);
        this.cells[0].colSpan = numcells;

        // Set content if available
        if(htmlcontent !== null)
            this.SetContent(htmlcontent);
    }



    SetContent(htmlelement)
    {
        super.SetContent(0, htmlelement);
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

