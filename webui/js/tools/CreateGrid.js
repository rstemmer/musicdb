
"use strict";

class Grid
{
    constructor(columns, rows)
    {
        this.rows         = rows;
        this.columns      = columns;
        this.tableelement = document.createElement("table");
        this.tableelement.classList.add("grid_table");
        
        this.tablecells   = new Array(); // cells[rows][columns]
        for(let y=0; y<rows; y++)
        {
            let rowelement = document.createElement("tr");
            rowelement.classList.add("grid_row");

            let tablecolumns = new Array();
            for(let x=0; x<columns; x++)
            {
                let cellelement = document.createElement("td");
                cellelement.classList.add("grid_cell");
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
}


function CreateGrid(name, columns, rows)
{
    var grid = "";

    grid += "<table id=\"GRID_" + name + "\" class=\"grid_table\">";
    for(let y=0; y<rows; y++)
    {
        grid += "<tr class=\"grid_row\">";
        for(let x=0; x<columns; x++)
        {
            let gridid;
            gridid = GridCellID(name, x, y);
            grid += "<td id=\"" + gridid + "\" class=\"grid_cell\">";
            grid += "</td>"
        }
        grid += "</tr>"
    }
    grid += "</table>"


    return grid;
}


function GridCellID(name, x, y)
{
    var gridid;
    gridid = "GRID_" + name + "_" + x + "_" + y;
    return gridid;
}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

