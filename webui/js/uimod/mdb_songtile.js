
"use strict";


class SongQueueTile extends Draggable
{
    constructor(MDBSong, MDBAlbum, MDBArtist, entryid, position, buttonbox)
    {
        super();
        this.songid      = MDBSong.id;
        let songname     = MDBSong.name.replace(" - ", " – ");
        this.albumid     = MDBAlbum.id;
        let albumname    = MDBAlbum.name.replace(" - ", " – ");
        let release      = MDBAlbum.release;
        let artistname   = MDBArtist.name;
        let artistid     = MDBArtist.id;

        this.element     = document.createElement("div");
        this.element.id  = entryid;
        this.element.dataset.entryid   = entryid;
        this.element.dataset.musictype = "song";
        this.element.dataset.musicid   = this.songid;
        this.element.dataset.droptask  = "move";
        this.element.classList.add("QueueTile");

        this.artwork                  = new AlbumArtwork(MDBAlbum, "small");

        this.infobox                  = document.createElement("div");
        this.infobox.classList.add("infobox");

        this.titleelement             = document.createElement("div");
        this.titleelement.textContent = songname;
        this.titleelement.onclick     = ()=>{this.ShowAlbum();};

        this.infoelement              = this._CreateSongInformation(MDBAlbum, MDBArtist);
        this.infoelement.classList.add("hlcolor");
        this.infoelement.classList.add("smallfont");

        this.infobox.appendChild(this.titleelement);
        if(position > 0)
            this.infobox.appendChild(buttonbox.GetHTMLElement());
        this.infobox.appendChild(this.infoelement);

        this.element.appendChild(this.artwork.GetHTMLElement());
        this.element.appendChild(this.infobox);

        if(position > 0)
            this.BecomeDraggable();
    }



    GetHTMLElement()
    {
        return this.element;
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

