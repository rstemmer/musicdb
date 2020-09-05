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

class MusicMoods
{
    constructor(musictype)
    {
        this.musictype  = musictype;
        this.musicid    = null;
        this.moods      = tagmanager.GetMoods();

        // Calculate grid size
        this.rows       = 0;
        this.columns    = 0;
        for(let mood of this.moods)
        {
            if(mood.posx == null || mood.posy == null)
                continue;
            if(mood.posx > this.columns) this.columns = mood.posx;
            if(mood.posy > this.rows)    this.rows    = mood.posy;
        }
        this.columns += 1; // \_ position starts with 0 - so max posx=3 indicates 4 columns
        this.rows    += 1; // /

        // Create Mood grid
        this.moodgrid   = new Grid(this.columns, this.rows);
        this.moodbuttons= new Object();

        for(let mood of this.moods)
        {
            this.moodbuttons[mood.id] = this._CreateMoodButton(mood);
            this.moodgrid.InsertElement(mood.posx, mood.posy, this.moodbuttons[mood.id].GetHTMLElement());
        }

        // Create Element
        this.element = document.createElement("div");
        this.element.classList.add("musicmoods");
        this.element.appendChild(this.moodgrid.GetHTMLElement());
    }



    GetHTMLElement()
    {
        return this.element
    }


    _CreateMoodButton(mood)
    {
        let name    = mood.name;
        let moodid  = mood.id;
        let icon    = mood.icon;
        let icontype= mood.icontype;
            /*
             * mood.icontype:
             *      1: Unicode Character
             *      2: HTML code
             *      3: png \_ not yet specified in detail
             *      4: svg /
             *
             * mood.color: HTML color code or null
             */
        let button;
        if(icontype == 1) // Unicode Character Icon
            button = new UnicodeToggleButton(icon, (state)=>{this.onMoodClicked(moodid, state);});
        //button = new SVGToggleButton("Album", (state)=>{this.onMoodClicked(moodid, state);});
        button.SetTooltip(name);
        return button;
    }



    onMoodClicked(moodid, newstate)
    {
        // Send update to server including a request to sync other clients
        let parameters;
        let requestfunction;
        let requestsignature;
        if(this.musictype == "audio")
        {
            parameters       = {songid:  this.musicid, tagid: moodid};
            requestsignature = "UpdateSong";
            if(newstate === true)
                requestfunction = "SetSongTag";
            else if(newstate === false)
                requestfunction = "RemoveSongTag";
            else
                return;
        }
        else if(this.musictype == "video")
        {
            parameters       = {videoid: this.musicid, tagid: moodid};
            requestsignature = "UpdateVideo";
            if(newstate === true)
                requestfunction = "SetVideoTag";
            else if(newstate === false)
                requestfunction = "RemoveVideoTag";
            else
                return;
        }
        else
            return

        MusicDB_Request(requestfunction, requestsignature, parameters);
        return;
    }



    UpdateButtons(MDBMusic, MDBTags)
    {
        this.musicid = MDBMusic.id;

        let taglist = new Array();
        for(let mood of MDBTags.moods)
            taglist.push(mood.id.toString()); // key are strings, and I use the IDs as keys

        for(let key in this.moodbuttons)
        {
            if(taglist.indexOf(key) >= 0)
                this.moodbuttons[key].SetSelectionState(true);
            else
                this.moodbuttons[key].SetSelectionState(false);
        }

        return;
    }



    ResetButtons()
    {
        this.musicid = null;
        for(let key in this.moodbuttons)
            this.moodbuttons[key].SetSelectionState(false);
        return;
    }

}



class VideoMoods extends MusicMoods
{
    constructor()
    {
        super("video");
    }
}

class SongMoods extends MusicMoods
{
    constructor()
    {
        super("audio");
    }
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

