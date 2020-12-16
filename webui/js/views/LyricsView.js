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

        this.lyricsedit = new LyricsEdit();
        this.column1.appendChild(this.lyricsedit.GetHTMLElement());

        this.currentalbumid = -1;
        this.currentsongid  = -1;
    }



    BackToAlbum()
    {
        MusicDB_Request("GetAlbum", "ShowAlbum", {albumid: this.currentalbumid});
    }



    EditLyrics()
    {
        // TODO
    }



    UpdateInformation(MDBSong, MDBAlbum, MDBArtist, lyrics)
    {
        // For new albums, some persistent information need to be updated
        if(MDBAlbum.id != this.currentalbumid)
        {
            this.currentalbumid = MDBAlbum.id;

            // Update Headline
            this.headline.UpdateInformation(MDBAlbum, MDBArtist)
            this.headline.SetSubtitleClickAction(
                ()=>{artistsview.ScrollToArtist(MDBArtist.id);},
                null
            );

            // Update Album Artwork and make it draggable
            let newartwork  = new AlbumArtwork(MDBAlbum, "large");
            this.ReplaceArtwork(newartwork);
            this.artwork.ConfigDraggable("album", MDBAlbum.id, "insert");
            this.artwork.BecomeDraggable();
        }

        if(MDBSong.id != this.currentsongid)
        {
            this.currentsongid = MDBSong.id;

            lyrics = "Dummy Text";
            this.lyricsedit.SetLyrics(lyrics);
        }
        return;
    }


    onMusicDBMessage(fnc, sig, args, pass)
    {
        if(fnc == "GetSongLyrics" && sig == "ShowLyrics")
        {
            window.console && console.log(args);
            this.UpdateInformation(args.song, args.album, args.artist, args.lyrics);
        }
        return;
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

