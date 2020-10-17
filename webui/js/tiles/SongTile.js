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

class SongQueueTile extends QueueTile
{
    constructor(MDBSong, MDBAlbum, MDBArtist, entryid, position, buttonbox)
    {
        super();
        this.songid     = MDBSong.id;
        let songname    = MDBSong.name.replace(" - ", " – ");
        this.albumid    = MDBAlbum.id;
        let albumname   = MDBAlbum.name.replace(" - ", " – ");
        let release     = MDBAlbum.release;
        let artistname  = MDBArtist.name;
        let artistid    = MDBArtist.id;

        this.artwork    = new AlbumArtwork(MDBAlbum, "small");

        this.title             = document.createElement("span");
        this.title.textContent = songname;
        this.title.onclick     = ()=>{this.ShowAlbum();};

        this.subtitle          = this._CreateSongInformation(MDBAlbum, MDBArtist);

        this.CreateTile("song", this.songid, entryid, this.artwork, this.title, this.subtitle, buttonbox);

        if(position > 0)
            this.BecomeDraggable();
    }



    _CreateSongInformation(MDBAlbum, MDBArtist)
    {
        let songinfos             = document.createElement("div");
        songinfos.classList.add("hlcolor");
        songinfos.classList.add("smallfont");

        let artist = document.createElement("span");
        let spacer = document.createElement("span");
        let album  = document.createElement("span");

        spacer.classList.add("fgcolor");
        
        artist.innerText = MDBArtist.name;
        spacer.innerText = " – ";
        album.innerText  = MDBAlbum.name;


        artist.onclick   = ()=>{artistsview.ScrollToArtist(MDBArtist.id);};
        album.onclick    = ()=>{this.ShowAlbum();};

        songinfos.appendChild(artist);
        songinfos.appendChild(spacer);
        songinfos.appendChild(album);
        return songinfos;
    }



    ShowAlbum()
    {
        MusicDB_Request("GetAlbum", "ShowAlbum", {albumid: this.albumid});
    }
}

/*
 * This class provides the artistloader.
 * It is possible to select a set of genres and/or to reload the artists-list
 *
 * Requirements:
 *   - JQuery
 *   - Font-Awesome
 *   - mdb_songtile.css
 * Show:
 * Functions:
 * Callbacks:
 * Recommended Paths:
 * Trigger: (fnc -> sig)
 *
 */

function CreateSongTile(MDBSong, MDBAlbum, MDBArtist, topbuttonbox, bottombuttonbox, MDBTags = null)
{
    var html        = "";
    var imgpath     = EncodeArtworkPath(MDBAlbum.artworkpath, "50x50");
    var albumid     = MDBAlbum.id;
    var songname    = MDBSong.name.replace(" - ", " – ");
    var songid      = MDBSong.id;
    var albumname   = MDBAlbum.name.replace(" - ", " – ");
    var artistname  = MDBArtist.name;
    var artistid    = MDBArtist.id;
    var albumrequest= "MusicDB_Request(\'GetAlbum\', \'ShowAlbum\', {albumid:"+albumid+"});";

    html += "<div class=\"ST_tile\">"; // main box

    // Artwork
    html += "<div class=\"ST_artworkbox\">";
        html += "<img class=\"ST_artwork\" ";
        html += " src=\"" + imgpath + "\" ";
        html += " onClick=\"" + albumrequest + "\"";
        html += " title=\"Show this album\"";
        html += ">";
    html += "</div>";

    // Body
    html += "<div class=\"ST_body\">";
    html += "<div class=\"ST_row\">";
        // Songname
        html += "<div";
        html += " class=\"ST_songname fgcolor\">";
        html += songname;
        html += "</div>";
    html += "</div>";
    html += "<div class=\"ST_row\">";
        // Artistname
        html += "<div class=\"ST_subtitle smallfont\">";
        html += "<span ";
        html += " onClick=\'artistsview.ScrollToArtist("+artistid+");\'";
        html += " title=\"Scroll to this artist\"";
        html += " class=\"ST_artistname hlcolor\">";
        html += artistname;
        html += "</span>";

        html += "<span class=\"ST_separator fgcolor\"> – </span>";

        // Albumname
        html += "<span ";
        html += " class=\"ST_albumname hlcolor\"";
        html += " title=\"Show this album\"";
        html += " onClick=\"" + albumrequest + "\">";
        html += albumname;
        html += "</span>";
        html += "</div>";
    html += "</div>";
    html += "</div>";

    // Tagsbox
    html += "<div class=\"ST_tagbox hovpacity\">";
    html += "<div class=\"ST_row\">";
        html += "<div id=\"SongTileGenre_"+songid+"\" class=\"hlcolor\"></div>";
    html += "</div>";
    html += "<div class=\"ST_row\">";
        html += "<div id=\"SongTileSubgenre_"+songid+"\" class=\"hlcolor\"></div>";
    html += "</div>";
    html += "</div>";

    // Buttonbox
    html += "<div class=\"ST_buttonbox\">";
    html += "<div class=\"ST_row\">";
        html += "<div";
        html += " class=\"hlcolor\">";
        html += topbuttonbox;
        html += "</div>";
    html += "</div>";
    html += "<div class=\"ST_row\">";
        if(bottombuttonbox)
        {
            html += "<div";
            html += " class=\"hlcolor\">";
            html += bottombuttonbox;
            html += "</div>";
        }
    html += "</div>";
    html += "</div>";
    /*
    html += "<div class=\"ST_body\">";
    html += "<div class=\"ST_row\">";
    
    // Songname
    html += "<div";
    html += " class=\"ST_songname fgcolor\">";
    html += songname;
    html += "</div>";
    
    // Buttonbox
    html += "<div";
    html += " class=\"ST_buttonbox hlcolor\">";
    html += topbuttonbox;
    html += "</div>";
    
    html += "</div>";
    html += "<div class=\"ST_row\">";
    
    // Artistname
    html += "<div class=\"ST_subtitle smallfont\">";
    html += "<span ";
    html += " onClick=\'ScrollToArtist("+artistid+");\'";
    html += " title=\"Scroll to this artist\"";
    html += " class=\"ST_artistname hlcolor\">";
    html += artistname;
    html += "</span>";

    html += "<span class=\"ST_separator fgcolor\"> – </span>";

    // Albumname
    html += "<span ";
    html += " class=\"ST_albumname hlcolor\"";
    html += " title=\"Show this album\"";
    html += " onClick=\"" + albumrequest + "\">";
    html += albumname;
    html += "</span>";
    html += "</div>";
    
    // Buttonbox
    if(bottombuttonbox)
    {
        html += "<div";
        html += " class=\"ST_buttonbox hlcolor\">";
        html += bottombuttonbox;
        html += "</div>";
    }

    html += "</div>";
    html += "</div>";
    */

    html += "</div>"; // main box

    return html;
}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

