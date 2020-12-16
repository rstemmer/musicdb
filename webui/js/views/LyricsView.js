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

class LyricsView extends MainView2
{
    constructor()
    {
        // Button Array
        let backbutton = new SVGButton("MusicDB", ()=>{this.BackToAlbum();});
        let editbutton = new SVGButton("MusicDB", ()=>{this.EditLyrics();});
        backbutton.SetTooltip("Go back and show album");
        editbutton.SetTooltip("Edit lyrics");

        let headline = new MainViewHeadline(new Array(backbutton, editbutton));
        let artwork  = new AlbumArtwork(null, "large"); // album=null -> default artwork
        super("LyricsView", headline, artwork)
    }



    BackToAlbum()
    {
        // TODO: request this.albumid
    }



    EditLyrics()
    {
        // TODO
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        if(fnc == "GetSongLyrics" && sig == "ShowLyrics")
        {
            window.console && console.log(args);
        }
        return;
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

