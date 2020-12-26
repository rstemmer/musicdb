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

class HiddenAlbums extends MainView
{
    constructor()
    {
        let headline = new SimpleMainViewHeadline("Hidden Albums");
        super("HiddenAlbums", headline);

        let settingsbox = document.createElement("div");
        settingsbox.classList.add("flex-row");
        settingsbox.classList.add("flex-grow");

        this.element.appendChild(settingsbox);
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        if(fnc == "GetHiddenAlbums" && sig == "ShowHiddenAlbums")
        {
            window.console && console.log(args);
        }
        return;
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

