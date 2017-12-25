
"use strict";

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

