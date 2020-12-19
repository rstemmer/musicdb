
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
                let cellelement = document.createElement("td");
                cellelement.classList.add("grid-cell");
                rowelement.appendChild(cellelement);

                tablecolumns.push(cellelement);
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

