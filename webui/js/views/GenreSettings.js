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
        let headline = new SimpleMainViewHeadline("Genre and Subgenre Manager")
        super("GenreSettings", headline);

        this.genrelisteditor    = new GenreListEditor("Genres",
            (MDBTag)=>{return this.onSelectGenre(MDBTag);},
            (tag)=>{this.onAddGenre(tag);});
        this.subgenrelisteditor = new GenreListEditor("Sub-Genres",
            null,
            (tag)=>{this.onAddSubgenre(tag);});

        let settingsbox = document.createElement("div");
        settingsbox.classList.add("flex-row");
        settingsbox.classList.add("flex-grow");
        settingsbox.classList.add("genreeditors");
        settingsbox.appendChild(this.genrelisteditor.GetHTMLElement());
        settingsbox.appendChild(this.subgenrelisteditor.GetHTMLElement());

        this.element.appendChild(settingsbox);

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
            return;

        let subgenres = this.subgenres.filter(tag => tag.parentid == this.selectedgenre.id);
        this.subgenrelisteditor.UpdateList(subgenres, this.tagsstats);
        return;
    }



    onSelectGenre(MDBTag)
    {
        // Update Sub-Genre Editor
        this.selectedgenre = MDBTag;
        this.UpdateSubgenreEditor();
        return true;
    }



    onAddGenre(tag)
    {
    }
    onAddSubgenre(tag)
    {
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        if(fnc == "GetTags")
        {
            window.console && console.log(args);
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

