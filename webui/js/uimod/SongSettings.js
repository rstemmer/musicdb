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

class SongSettings extends TabSelect
{
    constructor(MDBSong, MDBTags)
    {
        super();
        this.element.classList.add("SongSettings");

        this.songmoods      = new SongMoods();
        this.songproperties = new SongProperties();
        this.genreedit      = new TagListEdit("genre");
        this.subgenreedit   = new TagListEdit("subgenre");
        this.audioplayer    = new AudioPlayer(MDBSong.path);

        this.Update(MDBSong, MDBTags);

        this.genrestab  = document.createElement("div");
        this.moodstab   = document.createElement("div");
        this.previewtab = document.createElement("div");

        this.genrestab.classList.add("flex-grow");
        this.moodstab.classList.add("flex-row");
        this.moodstab.classList.add("flex-grow");
        this.previewtab.classList.add("flex-grow");

        this.moodstab.appendChild(this.songmoods.GetHTMLElement());
        this.moodstab.appendChild(this.songproperties.GetHTMLElement());

        this.genrestab.appendChild(this.genreedit.GetHTMLElement());
        this.genrestab.appendChild(this.subgenreedit.GetHTMLElement());

        this.previewtab.appendChild(this.audioplayer.GetHTMLElement());

        this.AddTab(new SVGIcon("Tags"), "Genre Tags",         this.genrestab, true);
        this.AddTab(new SVGIcon("Tags"), "Moods & Properties", this.moodstab);
        this.AddTab(new SVGIcon("Play"), "Preview",            this.previewtab);
    }



    Update(MDBSong, MDBTags)
    {
        this.songmoods.UpdateButtons(MDBSong, MDBTags);
        this.songproperties.UpdateButtons(MDBSong);
        this.genreedit.Update("audio", MDBSong.id, MDBTags);
        this.subgenreedit.Update("audio", MDBSong.id, MDBTags);
    }
}




// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

