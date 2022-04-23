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
                {
                    let albumid = modemanager.GetCurrentAlbumID();
                    MusicDB.Request("GetAlbum", "ShowAlbum", {albumid: albumid});
                }
                else
                {
                    let videoid = modemanager.GetCurrentVideoID();
                    MusicDB.Request("GetVideo", "ShowVideo", {videoid: videoid});
                }
            },
            "Hide advanced genre selection menu and go back to the Music list");

        this.toolbar.AddSpacer(true); // grow
        this.toolbar.AddButton(this.closebutton);
        this.toolbar.AddSpacer(true); // grow

        this.AppendChild(this.toolbar);
    }



    Update()
    {
        let tagmanager = WebUI.GetManager("Tags");
        let genretree  = tagmanager.GetGenreTree();
        window.console?.log(genretree);

        // Render the tree
        let genrelist = new Element("ul");
        for(let genreid in genretree)
        {
            let entry     = genretree[genreid];
            let genre     = entry.genre;
            let subgenres = entry.subgenres;

            let genreitem = new Element("li");
            let genrecheckbox = this.CreateGenreCheckbox(genre);
            let subgenrelist  = this.CreateSubgenreList(subgenres);
            genreitem.AppendChild(genrecheckbox);
            genreitem.AppendChild(subgenrelist);
            genrelist.AppendChild(genreitem);

        }

        this.RemoveChilds();
        this.AppendChild(this.toolbar);
        this.AppendChild(genrelist);
    }


    CreateGenreCheckbox(genre) // TODO
    {
        let checkbox = new SettingsCheckbox(genre.name, null, ()=>{});
        return checkbox;
    }


    
    CreateSubgenreList(subgenres)
    {
        let list = new Element("ul");
        for(let subgenreid in subgenres)
        {
            let subgenre = subgenres[subgenreid];
            let item     = new Element("li");
            let checkbox = this.CreateSubgenreCheckbox(subgenre);
            item.AppendChild(checkbox);
            list.AppendChild(item);
        }
        return list;
    }

    CreateSubgenreCheckbox(subgenre) // TODO
    {
        let checkbox = new SettingsCheckbox(subgenre.name, null, ()=>{});
        return checkbox;
    }



    onViewMounted()
    {
        this.Update();
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        return;
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

