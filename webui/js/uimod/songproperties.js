
"use strict";

/*
 * This function creates and shows a grid of property controls (like,fav, …
 * 
 * Args:
 *  parentid (str): ID of the HTML element in that the grid shall be placed
 *  controlname (str): Name of the grid to identify if later
 */
function Songproperties_ShowControl(parentid, controlname)
{
    if($("#"+parentid).length === 0)
    {
        window.console && console.log("Parent " + parenid + "does not exist!");
        return;
    }

    // Create grid
    var html = "";
    html += CreateGrid(controlname, 3, 2);
    $("#"+parentid).html(html);

    // Create mood buttons
    Songproperties_CreateButton(controlname, 0, 0, "<i class=fa>&#xf087;</i>", "like");
    Songproperties_CreateButton(controlname, 1, 0, "<i class=fa>&#xf088;</i>", "dislike");
    Songproperties_CreateButton(controlname, 0, 1, "<i class=fa>&#xf006;</i>", "love");
    Songproperties_CreateButton(controlname, 1, 1, "<i class=fa>&#xf014;</i>", "hate");
    Songproperties_CreateButton(controlname, 2, 1, "<i class=fa>&#xf05e;</i>", "disable");
}
    


function Songproperties_CreateButton(controlname, x, y, icon, property)
{
    var html = "";
    var buttonid = controlname + "_" + property;
    var tooltip = property.charAt(0).toUpperCase() + property.slice(1);
    html += "<div";
    html += " title=\"" + tooltip + "\"";
    html += " id=\"" + buttonid + "\"";
    html += " class=\"propertybutton\"";
    html += " data-button=\"unpressed\"";
    html += ">";
    html += icon;
    html += "</div>";

    var cellid;
    cellid = GridCellID(controlname, x, y);
    $("#"+cellid).html(html);
}


/*
 * This function sets the properties and functionality of the Control for a specific song
 *
 * Args:
 *  controlname (str): To identify the grid
 *  MDBSong: The tags of a specific song
 */
function Songproperties_UpdateControl(controlname, MDBSong, resetlike)
{
    if(resetlike == true)
    {
        Songproperties_SetProperty(controlname, MDBSong.id, "like",    false);
        Songproperties_SetProperty(controlname, MDBSong.id, "dislike", false);
    }
    Songproperties_SetProperty(controlname, MDBSong.id, "love",    MDBSong.favorite ==  1);
    Songproperties_SetProperty(controlname, MDBSong.id, "hate",    MDBSong.favorite == -1);
    Songproperties_SetProperty(controlname, MDBSong.id, "disable", MDBSong.disabled !=  0);
}



function Songproperties_SetProperty(controlname, songid, property, pressed)
{
    var buttonid;
    buttonid = "#" + controlname + "_" + property;

    // determin state
    var buttonstate;
    if(pressed == true)
        buttonstate = "pressed";
    else
        buttonstate = "unpressed";

    $(buttonid).attr("data-button", buttonstate);
    $(buttonid).off().on("click",
        function()
        {
            Songproperties_onPropertyButtonClick(buttonid, songid, property);
        }
    );
}


function Songproperties_onPropertyButtonClick(buttonid, songid, property)
{
    var buttonstate = $(buttonid).attr("data-button");
    var newstate;
    var value       = null; // value that will be sent to the server

    if(property == "like"
    || property == "dislike"
      )
    {
        if(buttonstate == "unpressed")
        {
            newstate = "pressed";
            value    = "inc";
        }
        else
        {
            newstate = "unpressed";
            value    = "dec";
        }

        // update song statistics
        var statistic = property + "s"; // it's a counter and uses plural intern
        MusicDB_Request("UpdateSongStatistic", "UpdateSong",
            {songid:songid, statistic:statistic, modifier:value});
        $(buttonid).attr("data-button", newstate);
    }
    else if(property == "love"
         || property == "hate"
           )
    {
        let newlovestate, newhatestate;
        if(property == "love" && buttonstate == "unpressed")
        {
            newstate = "pressed";
            value    = "love";
        }
        else if(property == "hate" && buttonstate == "unpressed")
        {
            newstate = "pressed";
            value    = "hate";
        }
        else
        {
            value   = "none";
        }

        // update song statistics
        MusicDB_Request("UpdateSongStatistic", "UpdateSong",
            {songid:songid, statistic:"favorite", modifier:value});
        $(buttonid).attr("data-button", newstate);
    }
    else if(property == "disable")
    {
        if(buttonstate == "unpressed")
        {
            newstate = "pressed";
            value    = "yes";
        }
        else if(buttonstate == "pressed")
        {
            newstate = "unpressed";
            value    = "no";
        }

        MusicDB_Request("UpdateSongStatistic", "UpdateSong",
            {songid:songid, statistic:"disable", modifier:value});
        $(buttonid).attr("data-button", newstate);
    }

    $(buttonid).attr("data-button", newstate);
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

