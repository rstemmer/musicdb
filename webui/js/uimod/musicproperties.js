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
        this.musicid    = null;
        this.propgrid   = new Grid(4, 2);
        this.properties = new Object();
        this.properties["like"         ] = this._CreatePropertyButton("Like",          "like",          "Like");
        this.properties["dislike"      ] = this._CreatePropertyButton("Dislike",       "dislike",       "Dislike");
        this.properties["liverecording"] = this._CreatePropertyButton("LiveRecording", "liverecording", "Live Recording");
        this.properties["love"         ] = this._CreatePropertyButton("Favorite",      "love",          "Loved Song");
        this.properties["hate"         ] = this._CreatePropertyButton("Hate",          "hate",          "Hated Song");
        this.properties["badaudio"     ] = this._CreatePropertyButton("BadFile",       "badaudio",      "Bad Audio");
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
        let key   = null;
        let value = null;

        // Like / Dislike
        if(propertyname == "like"
        || propertyname == "dislike")
        {
            if(newstate === true)
                value = "inc";
            else if(newstate === false)
                value = "dec";

            key = propertyname + "s"; // it's a counter and uses plural intern
        }
        // Love / Hate (Only one is allowed to be checked)
        else if(propertyname == "love"
             || propertyname == "hate"
               )
        {
            if(propertyname == "love" && newstate === true)
            {
                value = "love";
                this.properties["hate"].SetSelectionState(false);
            }
            else if(propertyname == "hate" && newstate === true)
            {
                value = "hate";
                this.properties["love"].SetSelectionState(false);
            }
            else
                value = "none";

            key = "favorite";
        }
        // Other properties
        else if(propertyname == "disable"
             || propertyname == "liverecording"
             || propertyname == "badaudio"
             || propertyname == "lyricsvideo"
               )
        {
            window.console && console.log("Setting " + propertyname + " to " + newstate);
            if(newstate === true)
                value = "yes";
            else if(newstate === false)
                value = "no";
            window.console && console.log("Setting " + propertyname + " to " + value);

            key = propertyname;
        }

        // Check if key/value pair exists
        if(key == null || value == null)
            return;

        // Send update to server including a request to sync other clients
        let parameters;
        let requestfunction;
        let requestsignature;
        if(this.musictype == "audio")
        {
            parameters       = {songid:  this.musicid, statistic: key, modifier: value};
            requestfunction  = "UpdateSongStatistic";
            requestsignature = "UpdateSong";
        }
        else if(this.musictype == "video")
        {
            parameters       = {videoid: this.musicid, statistic: key, modifier: value};
            requestfunction  = "UpdateVideoStatistic";
            requestsignature = "UpdateVideo";
        }
        else
            return

        MusicDB_Request(requestfunction, requestsignature, parameters);
        return;
    }



    UpdateButtons(MDBMusic)
    {
        this.musicid = MDBMusic.id;

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
        this.musicid = null;
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
    constructor(MDBSong = null)
    {
        super("audio");
        if(MDBSong != null)
            this.UpdateButtons(MDBSong);
    }
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

