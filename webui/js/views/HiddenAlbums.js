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

class HiddenAlbums extends MainSettingsView
{
    constructor()
    {
        super("HiddenAlbums", "Hidden Albums", "All albums marked to be hidden are listed here. Clicking on them opens the album view. They can then be made visible again within the album settings (right click on the headline of the album view).");

        this.albumsbox = document.createElement("div");
        this.albumsbox.classList.add("flex-row");
        this.albumsbox.classList.add("flex-grow");
        this.albumsbox.classList.add("flex-wrap");
        this.albumsbox.classList.add("albumsbox");

        this.element.appendChild(this.albumsbox);
    }



    UpdateView(albumslist)
    {
        this.albumsbox.innerHTML = "";
        for(let entry of albumslist)
        {
            let MDBAlbum = entry.album;
            let MDBTags  = entry.tags;
            let tile = new AlbumTile(MDBAlbum, ()=>{window.console&&console.log(`Clicked on ${MDBAlbum.name}`);});
            this.albumsbox.appendChild(tile.GetHTMLElement());
        }
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        if(fnc == "GetHiddenAlbums" && sig == "ShowHiddenAlbums")
        {
            this.UpdateView(args);
        }
        return;
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

