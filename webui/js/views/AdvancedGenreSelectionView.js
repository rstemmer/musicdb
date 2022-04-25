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

class AdvancedGenreSelectionView extends LeftView
{
    constructor()
    {
        super("AdvancedGenreSelectionView");

        // Tool Bar
        this.toolbar     = new ToolBar();
        this.closebutton = new TextButton("Back", "Back to Music",
            ()=>{
                this.UnlockView();
                WebUI.GetManager("LeftView").ShowArtistsView();

                let modemanager = WebUI.GetManager("MusicMode");
                let musicmode   = modemanager.GetCurrentMode();
                if(musicmode == "audio")
                    MusicDB.Broadcast("GetFilteredArtistsWithAlbums", "ShowArtists");
                else
                    MusicDB.Broadcast("GetFilteredArtistsWithVideos", "ShowArtists");
            },
            "Hide advanced genre selection menu and go back to the artists list");

        this.toolbar.AddSpacer(true); // grow
        this.toolbar.AddButton(this.closebutton);
        this.toolbar.AddSpacer(true); // grow

        this.AppendChild(this.toolbar);

        this.tagmanager      = WebUI.GetManager("Tags");
        this.genrestatistics = null;
    }



    // For genres and sub genres
    CreateInfoText(genreid)
    {
        if(this.genrestatistics == null)
            return "<span>Loading ...</span>"

        let stats       = this.genrestatistics[genreid];
        let numsongs    = stats["songs"];
        let numalbums   = stats["albums"];
        let numvideos   = stats["videos"];
        let numchildren = stats["children"];

        let infotext    = "";
        if(typeof numsongs    === "number" && numsongs    > 0) infotext += `<span>${numsongs   }&nbsp;Songs</span>`;
        if(typeof numalbums   === "number" && numalbums   > 0) infotext += `<span>${numalbums  }&nbsp;Albums</span>`;
        if(typeof numvideos   === "number" && numvideos   > 0) infotext += `<span>${numvideos  }&nbsp;Videos</span>`;
        if(typeof numchildren === "number" && numchildren > 0) infotext += `<br><span>${numchildren}&nbsp;Sub-Genres</span>`;
        if(infotext == "") infotext = "<span>This tag is not used yet</span>"

        return infotext;
    }



    Update()
    {
        let genretree  = this.tagmanager.GetGenreTree();

        let activegenreids    = this.tagmanager.GetActiveGenreIDs();
        let activesubgenreids = this.tagmanager.GetActiveSubgenreIDs();

        // Render the tree
        let genrelist = new Element("ul");
        for(let genreid in genretree)
        {
            let entry     = genretree[genreid];
            let genre     = entry.genre;
            let subgenres = entry.subgenres;
            let isactive;
            if(activegenreids.indexOf(genre.id) >= 0)
                isactive = true;
            else
                isactive = false;

            // Create genre activation control
            let genrecheckbox = this.CreateGenreCheckbox(genre, isactive);
            let subgenrelist  = this.CreateSubgenreList(genre, subgenres, activesubgenreids);

            // Create list item
            let genreitem = new Element("li");
            genreitem.AppendChild(genrecheckbox);
            if(isactive) // Only show sub genres when genre is active
                genreitem.AppendChild(subgenrelist);
            genrelist.AppendChild(genreitem);
        }

        this.RemoveChilds();
        this.AppendChild(this.toolbar);
        this.AppendChild(genrelist);
    }

    CreateGenreCheckbox(genre, isactive)
    {
        let infotext = this.CreateInfoText(genre.id);
        let checkbox = new SettingsCheckbox(genre.name, infotext,
            (state)=>
            {
                this.onGenreClicked(genre, state);
            }
            , isactive);
        checkbox.SetTooltip("Activate or Deactivate Genre for Album selection");
        return checkbox;
    }


    
    CreateSubgenreList(genre, subgenres, activesubgenreids)
    {
        let list = new Element("ul");
        for(let subgenreid in subgenres)
        {
            let subgenre = subgenres[subgenreid];
            let item     = new Element("li");
            let isactive;
            if(activesubgenreids.indexOf(subgenre.id) >= 0)
                isactive = true;
            else
                isactive = false;

            let checkbox = this.CreateSubgenreCheckbox(genre, subgenre, isactive);
            item.AppendChild(checkbox);
            list.AppendChild(item);
        }
        return list;
    }

    CreateSubgenreCheckbox(genre, subgenre, isactive)
    {
        let infotext = this.CreateInfoText(subgenre.id);
        let checkbox = new SettingsCheckbox(subgenre.name, infotext,
            (state)=>
            {
                this.onSubgenreClicked(genre, subgenre, state);
            }
            , isactive);
        checkbox.SetTooltip("Activate or Deactivate Genre for Album selection");
        return checkbox;
    }



    onGenreClicked(genre, isactive)
    {
        // On shift click, if isactive is true,
        // deactivate all other genres. Shift+Click = Exclusive select
        if(isactive)
        {
            if(event.shiftKey)
            {
                let genres         = this.tagmanager.GetGenres();
                let activegenreids = this.tagmanager.GetActiveGenreIDs();

                // Deactivate all active genres.
                // A call is enough, there will be a request later on for synchronization
                for(let entry of genres)
                {
                    if(activegenreids.indexOf(entry.id) >= 0)
                        MusicDB.Call("SetMDBState", {category:"GenreFilter", name:entry.name, value:false});
                }
            }

            // Enable all sub genres
            let subgenres = this.tagmanager.GetSubgenresOfGenre(genre.id);
            let category  = `SubgenreFilter:${genre.name}`;
            for(let subgenre of subgenres)
                MusicDB.Call("SetMDBState", {category:category, name:subgenre.name, value:true});
        }

        MusicDB.Request("SetMDBState", "UpdateMDBState",
            {category:"GenreFilter", name:genre.name, value:isactive});
        return;
    }

    onSubgenreClicked(genre, subgenre, isactive)
    {
        let category = `SubgenreFilter:${genre.name}`;

        // On shift click, if isactive is true,
        // deactivate all other genres. Shift+Click = Exclusive select
        if(isactive && event.shiftKey)
        {
            let subgenres         = this.tagmanager.GetSubgenresOfGenre(genre.id);
            let activesubgenreids = this.tagmanager.GetActiveSubgenreIDs();

            // Deactivate all active genres.
            // A call is enough, there will be a request later on for synchronization
            for(let entry of subgenres)
            {
                if(activesubgenreids.indexOf(entry.id) >= 0)
                    MusicDB.Call("SetMDBState", {category:category, name:entry.name, value:false});
            }
        }

        // It can happen that all sub genres are deactivated and this sub genre
        // is the last active one which has be deactivated now. (in isactive = false).
        // In this case, the main genre needs to be deactivated as well.
        if(isactive == false)
        {
            let existingsubgenres = this.tagmanager.GetSubgenresOfGenre(genre.id);
            let activesubgenreids = this.tagmanager.GetActiveSubgenreIDs();

            // Remove the newly removed sub genre from the list of active sub genres
            activesubgenreids.find((id, index)=>{if(id == subgenre.id) delete activesubgenreids[index];});

            let deactivategenre = true;
            for(let existingsubgenre of existingsubgenres)
            {
                // Do not deactivate the main genre when at least one of its sub genres is still active
                if(activesubgenreids.indexOf(existingsubgenre.id) >= 0)
                    deactivategenre = false;
            }

            if(deactivategenre)
            {
                MusicDB.Request("SetMDBState", "UpdateMDBState",
                    {category:"GenreFilter", name:genre.name, value:false});
            }
        }

        MusicDB.Request("SetMDBState", "UpdateMDBState",
            {category:category, name:subgenre.name, value:isactive});
        return;
    }



    onViewMounted()
    {
        // Show UI as soon as possible, based on cached data
        this.Update();

        // Update cached statistics
        MusicDB.Request("GetTagsStatistics", "UpdateGenreSelection");
        return;
    }



    onWebSocketOpen()
    {
        // Initialize tags statistics cache
        MusicDB.Request("GetTagsStatistics", "UpdateGenreSelection");
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        if(fnc == "GetMDBState" && sig == "UpdateMDBState")
        {
            this.Update();
        }
        else if(fnc == "GetTags" && sig == "UpdateTags")
        {
            this.Update();
        }
        else if(fnc == "GetTagsStatistics" && sig == "UpdateGenreSelection")
        {
            this.genrestatistics = args;
            this.Update();
        }
        return;
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

