// MusicDB,  a music manager with web-bases UI that focus on music.
// Copyright (C) 2017 - 2022  Ralf Stemmer <ralf.stemmer@gmx.net>
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

const RELOAD_INTERVAL = 500; //ms

class GenreSelectionView extends Element
{
    constructor()
    {
        super("div", ["GenreSelectionView", "flex-row", "frame", "hlcolor", "hovpacity"]);
        this.reloadtimeouthandler = null;
        this.activegenres         = null;

        this.SetTooltip("Right click for advanced genre and sub genre selection.");
        this.SetRightClickEventCallback(()=>
            {
                event.preventDefault();
                WebUI.GetManager("LeftView").ShowAdvancedGenreSelection();
            });
    }



    // MDBState is optional
    // if it is undefined a cached state is used
    Update(MDBState)
    {
        if(MDBState !== undefined)
            this.activegenres = MDBState.GenreFilter;

        // Create all buttons
        super.RemoveChilds();
        let genres = WebUI.GetManager("Tags").GetGenres();
        for(let genre of genres)
        {
            // If Other-Genre shall be hidden, skip adding it to the View :)
            if(genre.name === "Other" && configuration.GenreSelectionView.showother === false)
                continue;

            let tag = new Tag(genre);
            tag.SetClickAction(()=>{this.onTagClicked(tag, genre);});

            // Check if genre is active
            if(this.activegenres.indexOf(genre.name) >= 0)
            {
                tag.SetData("active", true);
                tag.SetTooltip("Deactivate genre for album selection.");
            }
            else
            {
                tag.SetData("active", false);
                tag.SetTooltip("Activate genre and all its sub genres for album selection.\nHold shift key for exclusive selection.");
            }

            // append button
            super.AppendChild(tag);
        }

        return;
    }



    onTagClicked(tag, mdbtag)
    {
        // Update visual state
        let active;
        if(tag.GetData("active") === "true")
            active = false;
        else
            active = true;

        tag.SetData("active", active);

        // Activate all sub genres as well
        if(active)
        {
            // Enable all sub genres
            let tagmanager = WebUI.GetManager("Tags");
            let subgenres  = tagmanager.GetSubgenresOfGenre(mdbtag.id);
            let category   = `SubgenreFilter:${mdbtag.name}`;
            for(let subgenre of subgenres)
                MusicDB.Call("SetMDBState", {category:category, name:subgenre.name, value:true});

            // If shift click -> deactivate all other genres (exclusive select)
            if(event.shiftKey)
            {
                let genres         = tagmanager.GetGenres();
                let activegenreids = tagmanager.GetActiveGenreIDs();

                // Deactivate all active genres.
                // A call is enough, there will be a request later on for synchronization
                for(let entry of genres)
                {
                    if(activegenreids.indexOf(entry.id) >= 0)
                        MusicDB.Call("SetMDBState", {category:"GenreFilter", name:entry.name, value:false});
                }
            }
        }

        // Send update to server
        // The Call will trigger a broadcast of GetMDBState
        // By making a Request and giving a function signature the broadcast
        // gets handled exactly like a GetMDBState request
        MusicDB.Request("SetMDBState", "UpdateMDBState",
            {category:"GenreFilter", name:mdbtag.name, value:active});

        // To avoid flickering when switching multiple genres,
        // use a timeout until the artist lists shall be refreshed
        if(this.reloadtimeouthandler !== null)
            window.clearTimeout(this.reloadtimeouthandler);
        this.reloadtimeouthandler = window.setTimeout(()=>
            {
                let mode = WebUI.GetManager("MusicMode").GetCurrentMode();
                if(mode == "audio")
                    MusicDB.Broadcast("GetFilteredArtistsWithAlbums", "ShowArtists");
                else if(mode == "video")
                    MusicDB.Broadcast("GetFilteredArtistsWithVideos", "ShowArtists");

            }, RELOAD_INTERVAL);
        
        return;
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        if(fnc == "GetMDBState" && sig == "UpdateMDBState")
        {
            this.Update(args);
        }
        else if(fnc == "GetTags" && sig == "UpdateTags")
        {
            this.Update();
        }
        return;
    }
}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

