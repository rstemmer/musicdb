
"use strict";

/*
 * This function creates and shows a grid of property controls (like,fav, …
 * 
 * Args:
 *  parentid (str): ID of the HTML element in that the grid shall be placed
 *  controlname (str): Name of the grid to identify if later
 */
function Videoproperties_ShowControl(parentid, controlname)
{
    // There are no differences between songs and videos at this point
    Songproperties_ShowControl(parentid, controlname);
}
function Songproperties_ShowControl(parentid, controlname)
{
    if($("#"+parentid).length === 0)
    {
        window.console && console.log("Parent " + parentid + "does not exist!");
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

function Videoproperties_UpdateControl(controlname, MDBVideo, resetlike)
{
    if(resetlike == true)
    {
        Videoproperties_SetProperty(controlname, MDBVideo.id, "like",    false);
        Videoproperties_SetProperty(controlname, MDBVideo.id, "dislike", false);
    }
    Videoproperties_SetProperty(controlname, MDBVideo.id, "love",    MDBVideo.favorite ==  1);
    Videoproperties_SetProperty(controlname, MDBVideo.id, "hate",    MDBVideo.favorite == -1);
    Videoproperties_SetProperty(controlname, MDBVideo.id, "disable", MDBVideo.disabled !=  0);
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
            Musicproperties_onPropertyButtonClick(buttonid, songid, property, "song");
        }
    );
}

function Videoproperties_SetProperty(controlname, videoid, property, pressed)
{
    let buttonid;
    buttonid = "#" + controlname + "_" + property;

    // determine state
    let buttonstate;
    if(pressed == true)
        buttonstate = "pressed";
    else
        buttonstate = "unpressed";

    $(buttonid).attr("data-button", buttonstate);
    $(buttonid).off().on("click",
        function()
        {
            Musicproperties_onPropertyButtonClick(buttonid, videoid, property, "video");
        }
    );
}


/*
 * type can be "song" or "video"
 */
function Musicproperties_onPropertyButtonClick(buttonid, musicid, property, type)
{
    let buttonstate = $(buttonid).attr("data-button");
    let newstate;
    let value       = null; // value that will be sent to the server
    let requestfunction;
    let requestsignature;
    let parameters;
    if(type == "song")
    {
        requestfunction  = "UpdateSongStatistic";
        requestsignature = "UpdateSong";
    }
    else if(type == "video")
    {
        requestfunction  = "UpdateVideoStatistic";
        requestsignature = "UpdateVideo";
    }
    else
    {
        window.console && console.log("Invalid type " + type + "!");
        return;
    }

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

        // update music statistics
        let statistic = property + "s"; // it's a counter and uses plural intern
        if(type == "song")
            parameters = {songid:musicid, statistic:statistic, modifier:value};
        else if(type == "video")
            parameters = {videoid:musicid, statistic:statistic, modifier:value};
        else
            return

        MusicDB_Request(requestfunction, requestsignature, parameters);
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

        // update music statistics
        if(type == "song")
            parameters = {songid:musicid,  statistic:"favorite", modifier:value};
        else if(type == "video")
            parameters = {videoid:musicid, statistic:"favorite", modifier:value};
        else
            return

        MusicDB_Request(requestfunction, requestsignature, parameters);
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

        // update music statistics
        if(type == "song")
            parameters = {songid:musicid,  statistic:"disable", modifier:value};
        else if(type == "video")
            parameters = {videoid:musicid, statistic:"disable", modifier:value};
        else
            return

        MusicDB_Request(requestfunction, requestsignature, parameters);
        $(buttonid).attr("data-button", newstate);
    }

    $(buttonid).attr("data-button", newstate);
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

