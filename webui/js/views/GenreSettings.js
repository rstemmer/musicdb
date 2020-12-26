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

class GenreSettings extends MainView
{
    constructor()
    {
        let headline = new SimpleMainViewHeadline("Genre and Subgenre Manager");
        super("GenreSettings", headline);

        let infotext = document.createElement("span");
        infotext.classList.add("flex");
        infotext.classList.add("smallfont");
        infotext.classList.add("hlcolor");
        infotext.innerText = "Select genre to edit its sub-genres. Double click on name for renaming.";

        this.genrelisteditor    = new GenreListEditor("Genres",
            (MDBTag)=>{return this.onSelectGenre(MDBTag);},
            (tagname)=>{this.onAddGenre(tagname);},
            (tagid)=>{this.onRemoveGenre(tagid);},
            (tagid, newname)=>{this.onRenameGenre(tagid, newname);}
        );

        this.subgenrelisteditor = new GenreListEditor("Sub-Genres",
            null,
            (tagname)=>{this.onAddSubgenre(tagname);},
            (tagid)=>{this.onRemoveSubgenre(tagid);},
            (tagid, newname)=>{this.onRenameSubgenre(tagid, newname);}
        );

        let settingsbox = document.createElement("div");
        settingsbox.classList.add("flex-row");
        settingsbox.classList.add("flex-grow");
        settingsbox.classList.add("genreeditors");
        settingsbox.appendChild(this.genrelisteditor.GetHTMLElement());
        settingsbox.appendChild(this.subgenrelisteditor.GetHTMLElement());

        this.element.appendChild(settingsbox);
        //this.element.appendChild(infotext);

        this.genres    = [];
        this.subgenres = [];
        this.tagsstats = {};
        this.selectedgenre = null;
    }



    UpdateView(genres, subgenres)
    {
        this.UpdateGenreEditor();
        this.UpdateSubgenreEditor();
        return;
    }

    UpdateGenreEditor()
    {
        this.genrelisteditor.UpdateList(this.genres, this.tagsstats);
        return;
    }
    UpdateSubgenreEditor()
    {
        if(this.selectedgenre == null)
        {
            // Disable input for sub-genres when no genre is selected
            this.subgenrelisteditor.ForceInputElementState(false, "Select a genre to edit its sub-genres");
            this.subgenrelisteditor.UpdateHeadline(`Sub-Genres`);
            return;
        }

        let subgenres = this.subgenres.filter(tag => tag.parentid == this.selectedgenre.id);
        this.subgenrelisteditor.UpdateList(subgenres, this.tagsstats);
        this.subgenrelisteditor.ForceInputElementState(true);   // Enable input for sub-genres
        this.subgenrelisteditor.UpdateHeadline(`${this.selectedgenre.name} Sub-Genres`);
        this.genrelisteditor.ForceSelection(this.selectedgenre);// Reselect after update
        return;
    }



    onSelectGenre(MDBTag)
    {
        // Update Sub-Genre Editor
        this.selectedgenre = MDBTag;
        this.UpdateSubgenreEditor();
        return true;
    }



    onAddGenre(tagname)
    {
        MusicDB_Request("AddGenre", "UpdateTags", {name: tagname}, {origin: "GenreSettings"});
    }
    onAddSubgenre(tagname)
    {
        MusicDB_Request("AddSubgenre", "UpdateTags", {name: tagname, parentname: this.selectedgenre.name}, {origin: "GenreSettings"});
    }

    onRemoveGenre(tagid)
    {
        MusicDB_Request("DeleteTag", "UpdateTags", {tagid: tagid}, {origin: "GenreSettings"});

        if(tagid == this.selectedgenre.id)
        {
            this.selectedgenre = null;
            this.UpdateSubgenreEditor();
        }
    }
    onRemoveSubgenre(tagid)
    {
        MusicDB_Request("DeleteTag", "UpdateTags", {tagid: tagid}, {origin: "GenreSettings"});
    }

    onRenameGenre(tagid, newname)
    {
        window.console && console.log(`Rename Genre ${tagid} to "${newname}"`);
    }
    onRenameSubgenre(tagid, newname)
    {
        window.console && console.log(`Rename Sub-Genre ${tagid} to "${newname}"`);
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        if(fnc == "GetTags")
        {
            window.console && console.log(args);
            window.console && console.log(pass);

            // When tags were added, update the view
            if(pass != null && pass.origin == "GenreSettings")
                MusicDB_Request("GetTagsStatistics", "UpdateTagsStatistics");

            this.genres    = args.genres;
            this.subgenres = args.subgenres;
            this.UpdateView();
        }
        else if(fnc == "GetTagsStatistics")
        {
            window.console && console.log(args);
            this.tagsstats = args;
            this.UpdateView();
        }
        return;
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

