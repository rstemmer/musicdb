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

class MusicProperties
{
    constructor(musictype)
    {
        this.musictype  = musictype;
        this.propgrid   = new Grid(4, 2);
        this.properties = new Object();
        this.properties["like"         ] = this._CreatePropertyButton("Like",          "like",          "Like");
        this.properties["dislike"      ] = this._CreatePropertyButton("Dislike",       "dislike",       "Dislike");
        this.properties["liverecording"] = this._CreatePropertyButton("LiveRecording", "liverecording", "Live Recording");
        this.properties["love"         ] = this._CreatePropertyButton("Favorite",      "love",          "Loved Song");
        this.properties["hate"         ] = this._CreatePropertyButton("Hate",          "hate",          "Hated Song");
        this.properties["badaudio"     ] = this._CreatePropertyButton("BadAudio",      "badaudio",      "Bad Audio");
        this.properties["disable"      ] = this._CreatePropertyButton("Disable",       "disable",       "Disable Song");

        this.propgrid.InsertElement(0, 0, this.properties["like"         ].GetHTMLElement());
        this.propgrid.InsertElement(1, 0, this.properties["dislike"      ].GetHTMLElement());
        this.propgrid.InsertElement(2, 0, this.properties["liverecording"].GetHTMLElement());
        this.propgrid.InsertElement(0, 1, this.properties["love"         ].GetHTMLElement());
        this.propgrid.InsertElement(1, 1, this.properties["hate"         ].GetHTMLElement());
        this.propgrid.InsertElement(2, 1, this.properties["badaudio"     ].GetHTMLElement());
        this.propgrid.InsertElement(3, 1, this.properties["disable"      ].GetHTMLElement());

        // Videos have more properties
        if(this.musictype == "video")
        {
            this.properties["lyricsvideo"] = this._CreatePropertyButton("LyricsVideo", "lyricsvideo", "Lyrics Video");
            this.propgrid.InsertElement(3, 0, this.properties["lyricsvideo"  ].GetHTMLElement());
        }

        // Create Element
        this.element = document.createElement("div");
        this.element.classList.add("musicproperties");
        this.element.appendChild(this.propgrid.GetHTMLElement());
    }



    GetHTMLElement()
    {
        return this.element
    }


    _CreatePropertyButton(iconname, propertyname, tooltip)
    {
        let button;
        button = new SVGToggleButton(iconname, (state)=>{this.onPropertyClicked(propertyname, state);});
        button.SetTooltip(tooltip);
        return button;
    }



    onPropertyClicked(propertyname, newstate)
    {
        window.console && console.log("Setting " + propertyname + " to " + newstate);
    }



    UpdateButtons(MDBMusic)
    {
        this.properties["love"         ].SetSelectionState(MDBMusic.favorite      ==  1);
        this.properties["hate"         ].SetSelectionState(MDBMusic.favorite      == -1);
        this.properties["disable"      ].SetSelectionState(MDBMusic.disabled      !=  0);
        this.properties["liverecording"].SetSelectionState(MDBMusic.liverecording ==  1);
        this.properties["badaudio"     ].SetSelectionState(MDBMusic.badaudio      ==  1);
        if(this.musictype == "video")
            this.properties["lyricsvideo"].SetSelectionState(MDBMusic.lyricsvideo == 1);
        return;
    }



    ResetButtons()
    {
        for(let key in this.properties)
            this.properties[key].SetSelectionState(false);
        return;
    }

}



class VideoProperties extends MusicProperties
{
    constructor()
    {
        super("video");
    }
}

class SongProperties extends MusicProperties
{
    constructor()
    {
        super("audio");
    }
}

/*
 * This function creates and shows a grid of property controls (like,fav, …
 * 
 * Args:
 *  parentid (str): ID of the HTML element in that the grid shall be placed
 *  controlname (str): Name of the grid to identify if later
 */
function Videoproperties_ShowControl(parentid, controlname)
{
    let parentelement = document.getElementById(parentid);
    if(!parentelement)
    {
        window.console && console.log("Parent " + parentid + "does not exist!");
        return;
    }

    // Create grid
    var html = "";
    html += CreateGrid(controlname, 4, 2);
    parentelement.innerHTML = html;

    // Create mood buttons
    Songproperties_CreateButton(controlname, 0, 0, "<i class=fa>&#xf087;</i>", "like",          "Like");
    Songproperties_CreateButton(controlname, 1, 0, "<i class=fa>&#xf088;</i>", "dislike",       "Dislike");
    Songproperties_CreateButton(controlname, 2, 0, "<i class=fa>&#xf0c0;</i>", "liverecording", "Live Recording");
    Songproperties_CreateButton(controlname, 3, 0, "<i class=fa>&#xf0e5;</i>", "lyricsvideo",   "Lyrics Video");
    Songproperties_CreateButton(controlname, 0, 1, "<i class=fa>&#xf006;</i>", "love",          "Loved Song");
    Songproperties_CreateButton(controlname, 1, 1, "<i class=fa>&#xf014;</i>", "hate",          "Hated Song");
    Songproperties_CreateButton(controlname, 2, 1, "<i class=fa>&#xf131;</i>", "badaudio",      "Bad Audio");
    Songproperties_CreateButton(controlname, 3, 1, "<i class=fa>&#xf05e;</i>", "disable",       "Disable Song");
    return;
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
    html += CreateGrid(controlname, 4, 2);
    $("#"+parentid).html(html);

    // Create mood buttons
    Songproperties_CreateButton(controlname, 0, 0, "<i class=fa>&#xf087;</i>", "like",          "Like");
    Songproperties_CreateButton(controlname, 1, 0, "<i class=fa>&#xf088;</i>", "dislike",       "Dislike");
    Songproperties_CreateButton(controlname, 2, 0, "<i class=fa>&#xf0c0;</i>", "liverecording", "Live Recording");
    Songproperties_CreateButton(controlname, 0, 1, "<i class=fa>&#xf006;</i>", "love",          "Loved Song");
    Songproperties_CreateButton(controlname, 1, 1, "<i class=fa>&#xf014;</i>", "hate",          "Hated Song");
    Songproperties_CreateButton(controlname, 2, 1, "<i class=fa>&#xf131;</i>", "badaudio",      "Bad Audio");
    Songproperties_CreateButton(controlname, 3, 1, "<i class=fa>&#xf05e;</i>", "disable",       "Disable Song");
}
    


function Songproperties_CreateButton(controlname, x, y, icon, property, tooltip)
{
    let html = "";
    let buttonid = controlname + "_" + property;
    html += "<div";
    html += " title=\"" + tooltip + "\"";
    html += " id=\"" + buttonid + "\"";
    html += " class=\"propertybutton\"";
    html += " data-button=\"unpressed\"";
    html += ">";
    html += icon;
    html += "</div>";

    let cellid;
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
    Songproperties_SetProperty(controlname, MDBSong.id, "love",          MDBSong.favorite      ==  1);
    Songproperties_SetProperty(controlname, MDBSong.id, "hate",          MDBSong.favorite      == -1);
    Songproperties_SetProperty(controlname, MDBSong.id, "disable",       MDBSong.disabled      !=  0);
    Songproperties_SetProperty(controlname, MDBSong.id, "liverecording", MDBSong.liverecording ==  1);
    Songproperties_SetProperty(controlname, MDBSong.id, "badaudio",      MDBSong.badaudio      ==  1);
}

function Videoproperties_UpdateControl(controlname, MDBVideo, resetlike)
{
    if(resetlike == true)
    {
        Videoproperties_SetProperty(controlname, MDBVideo.id, "like",    false);
        Videoproperties_SetProperty(controlname, MDBVideo.id, "dislike", false);
    }
    Videoproperties_SetProperty(controlname, MDBVideo.id, "love",          MDBVideo.favorite      ==  1);
    Videoproperties_SetProperty(controlname, MDBVideo.id, "hate",          MDBVideo.favorite      == -1);
    Videoproperties_SetProperty(controlname, MDBVideo.id, "disable",       MDBVideo.disabled      !=  0);
    Videoproperties_SetProperty(controlname, MDBVideo.id, "liverecording", MDBVideo.liverecording ==  1);
    Videoproperties_SetProperty(controlname, MDBVideo.id, "badaudio",      MDBVideo.badaudio      ==  1);
    Videoproperties_SetProperty(controlname, MDBVideo.id, "lyricsvideo",   MDBVideo.lyricsvideo   ==  1);
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
    else if(property == "disable"
         || property == "liverecording"
         || property == "badaudio"
         || property == "lyricsvideo"
           )
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
            parameters = {songid:musicid,  statistic:property, modifier:value};
        else if(type == "video")
            parameters = {videoid:musicid, statistic:property, modifier:value};
        else
            return

        MusicDB_Request(requestfunction, requestsignature, parameters);
        $(buttonid).attr("data-button", newstate);
    }

    $(buttonid).attr("data-button", newstate);
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

