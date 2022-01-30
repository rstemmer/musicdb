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
        this.RemoveChilds();
    }



    // tablerow: TableRow object
    AddRow(tablerow)
    {
        this.rows.push(tablerow);
        this.AppendChild(tablerow);
    }



    RemoveRow(tablerow, includecontextrow=false)
    {
        // Double-remove can happen…
        if(tablerow === undefined)
            return;

        let rowelement   = tablerow.element;

        // Remove rows from the DOM
        let rowstoremove = 1
        if(includecontextrow === true)
        {
            rowelement.nextElementSibling.remove();
            rowstoremove++;
        }

        rowelement.remove();

        // Remove rows from the internal array
        let index = this.rows.indexOf(tablerow);
        if(index > -1)
            this.rows.splice(index, rowstoremove);

        return;
    }



    AddContextView(element)
    {
        let lastrow    = this.rows[this.rows.length - 1];
        let tablewidth = lastrow.cells.length;
        let contextrow = new TableSpanRow(tablewidth, ["ContextRow"], element);

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
        lastrow.GetHTMLElement().onclick = lastrow.GetHTMLElement().oncontextmenu;

        // Add row
        this.AddRow(contextrow);
    }
}



class TableCell extends Element
{
    constructor(span=null)
    {
        super("td");
    }



    SetColumnSpan(numcells)
    {
        this.GetHTMLElement().colSpan = numcells;
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
            let cell = new TableCell("td");
            this.cells.push(cell);
            this.AppendChild(cell);
        }
    }



    SetContent(cellnum, element)
    {
        this.cells[cellnum].RemoveChilds();
        this.cells[cellnum].AppendChild(element);
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
    constructor(numcells, classes=[], content=null)
    {
        super(1, classes);
        this.cells[0].SetColumnSpan(numcells);

        // Set content if available
        if(content !== null)
            this.SetContent(content);
    }



    SetContent(element)
    {
        super.SetContent(0, element);
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

