
"use strict";

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

function CreateSongTile(MDBSong, MDBAlbum, MDBArtist, topbuttonbox, bottombuttonbox)
{
    var html        = "";
    var imgpath     = EncodeArtworkPath(MDBAlbum.artworkpath, "50x50");
    var albumid     = MDBAlbum.id;
    var songname    = MDBSong.name.replace(" - ", " – ");
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

    html += "</div>"; // main box

    return html;
}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

