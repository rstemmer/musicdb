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
    }



    Update()
    {
        let tagmanager = WebUI.GetManager("Tags");
        let genretree  = tagmanager.GetGenreTree();

        let activegenreids    = tagmanager.GetActiveGenreIDs();
        let activesubgenreids = tagmanager.GetActiveSubgenreIDs();

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
        let checkbox = new SettingsCheckbox(genre.name, null,
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
        let checkbox = new SettingsCheckbox(subgenre.name, null,
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
        MusicDB.Request("SetMDBState", "UpdateMDBState",
            {category:"GenreFilter", name:genre.name, value:isactive});
        return;
    }

    onSubgenreClicked(genre, subgenre, isactive)
    {
        let category = `SubgenreFilter:${genre.name}`;
        MusicDB.Request("SetMDBState", "UpdateMDBState",
            {category:category, name:subgenre.name, value:isactive});
        return;
    }



    onViewMounted()
    {
        this.Update();
        return;
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
        return;
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

