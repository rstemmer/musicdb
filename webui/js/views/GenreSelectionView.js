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

var RELOAD_INTERVAL = 1000; //ms

class GenreSelectionView
{
    constructor()
    {
        this.reloadtimeouthandler = null;
        this.activegenres         = null;
        this.element = document.createElement("div");
        this.element.classList.add("flex-row");
        this.element.classList.add("frame");
        this.element.classList.add("hlcolor");
        this.element.classList.add("smallfont");
        this.element.classList.add("hovpacity");
        this.element.classList.add("GenreSelectionView");
    }



    GetHTMLElement()
    {
        return this.element;
    }



    // MDBState is optional
    // if it is undefined a cached state is used
    Update(MDBState)
    {
        if(MDBState !== undefined)
            this.activegenres = MDBState.albumfilter;

        // Create all buttons
        this.element.innerHTML = "";
        let genres = tagmanager.GetGenres();
        for(let genre of genres)
        {
            let tag = new Tag(genre);
            tag.SetClickAction(()=>{this.onTagClicked(tag, genre);});

            let tagelement = tag.GetHTMLElement();

            // Check if genre is active
            if(this.activegenres.indexOf(genre.name) >= 0)
                tagelement.dataset.active = true;
            else
                tagelement.dataset.active = false;

            // append button
            this.element.appendChild(tagelement);
        }

        return;
    }



    onTagClicked(tagobject, mdbtag)
    {
        let tagelement = tagobject.GetHTMLElement();

        // Update visual state
        let active;
        if(tagelement.dataset.active === "true")
            active = false;
        else
            active = true;

        tagelement.dataset.active = active;


        // Send update to server
        // The Call will trigger a broadcast of GetMDBState
        // By making a Request and giving a function signature the broadcast
        // gets handled exactly like a GetMDBState request
        MusicDB_Request("SetMDBState", "UpdateMDBState",
            {category:"albumfilter", name:mdbtag.name, value:active});

        // To avoid flickering when switching multiple genres,
        // use a timeout until the artist lists shall be refreshed
        if(this.reloadtimeouthandler !== null)
            window.clearTimeout(this.reloadtimeouthandler);
        this.reloadtimeouthandler = window.setTimeout(()=>
            {
                let mode = mdbmodemanager.GetCurrentMode();
                if(mode == "audio")
                    MusicDB_Broadcast("GetFilteredArtistsWithAlbums", "ShowArtists");
                else if(mode == "video")
                    MusicDB_Broadcast("GetFilteredArtistsWithVideos", "ShowArtists");

            }, RELOAD_INTERVAL);
        
        return;
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        if(fnc == "GetMDBState" && sig == "UpdateMDBState")
        {
            this.Update(args);
        }
        else if(fnc == "GetTags" && sig == "NewGenre")
        {
            this.Update();
        }
        return;
    }
}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

