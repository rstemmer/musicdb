
"use strict";

/*
 *
 * Requirements:
 *   - JQuery
 *   - albumtile.css
 * Show:
 * Functions:
 * Callbacks:
 * Recommended Paths:
 * Trigger: (fnc -> sig)
 *   - GetVideo -> ShowVideo
 *
 */

function CreateVideoTile(MDBVideo, MDBAlbum, MDBArtist, topbuttonbox, bottombuttonbox = null, MDBTags = null)
{
    // Album is not used because it may be undefined very often
    let html        = "";
    let imgpath     = EncodeVideoThumbnailPath(MDBVideo.framesdirectory, MDBVideo.thumbnailfile, "50×50");
    let anipath     = EncodeVideoThumbnailPath(MDBVideo.framesdirectory, MDBVideo.previewfile,   "50×50");
    let songname    = MDBVideo.name.replace(" - ", " – ");
    let songid      = MDBVideo.id;
    let artistname  = MDBArtist.name;
    let artistid    = MDBArtist.id;
    let videorelease= MDBVideo.release;
    let videorequest= "MusicDB_Request(\'GetVideo\', \'ShowVideo\', {videoid:"+videoid+"});";

    html += "<div class=\"ST_tile\">"; // main box

    // Artwork
    html += "<div class=\"ST_artworkbox\">";
        html += "<img class=\"ST_artwork\" ";
        html += " src=\"" + imgpath + "\" ";
        html += " onmouseover=\"this.src=\'"+anipath+"\'\"";
        html += " onmouseout =\"this.src=\'"+imgpath+"\'\"";
        html += " onClick=\"" + videorequest + "\"";
        html += " title=\"Show this video\"";
        html += ">";
    html += "</div>";

    // Body
    html += "<div class=\"ST_body\">";
    html += "<div class=\"ST_row\">";
        // Video name
        html += "<div";
        html += " class=\"ST_songname fgcolor\">";
        html += videoname;
        html += "</div>";
    html += "</div>";
    html += "<div class=\"ST_row\">";
        // Artist name
        html += "<div class=\"ST_subtitle smallfont\">";
        html += "<span ";
        html += " onClick=\'ScrollToArtist("+artistid+");\'";
        html += " title=\"Scroll to this artist\"";
        html += " class=\"ST_artistname hlcolor\">";
        html += artistname;
        html += "</span>";

    html += "</div>";
    html += "</div>";

    // Tagsbox (must be updated from external, only the empty divs are created
    html += "<div class=\"ST_tagbox hovpacity\">";
    html += "<div class=\"ST_row\">";
        html += "<div id=\"VideoTileGenre_"+videoid+"\" class=\"hlcolor\"></div>";
    html += "</div>";
    html += "<div class=\"ST_row\">";
        html += "<div id=\"VideoTileSubgenre_"+videoid+"\" class=\"hlcolor\"></div>";
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

    html += "</div>"; // main box

    return html;
}



function CreateSmallVideoTile(MDBVideo)
{
    let html        = "";
    let imgpath     = EncodeVideoThumbnailPath(MDBVideo.framesdirectory, MDBVideo.thumbnailfile, "150×150");
    let anipath     = EncodeVideoThumbnailPath(MDBVideo.framesdirectory, MDBVideo.previewfile,   "150×150");
    let videoid     = MDBVideo.id;
    let videoname   = MDBVideo.name;
    let videorelease= MDBVideo.release;
    let videorequest= "MusicDB_Request(\'GetVideo\', \'ShowVideo\', {videoid:"+videoid+"});";
    let datawidth   = "data-size=\"" + "medium" + "\"";

    html += "<div";
    html += " class=\"VT_videoentry\"";
    html += " " + datawidth;
    html += " onClick=\"" + videorequest + "\"";
    html += ">";

    // Cover
    html += "<div title=\"Show this Video\" class=\"VT_videocover\" " + datawidth + ">";
    html += "  <img src=\"" + imgpath + "\"";
    html += "    onmouseover=\"this.src=\'"+anipath+"\'\"";
    html += "    onmouseout =\"this.src=\'"+imgpath+"\'\"";
    html += "  \">";
    html += "</div>";

    html += "<div class=\"VT_videometadata\">";
    html += "<span class=\"VT_videorelease hlcolor smallfont\">" + videorelease + "</span>";
    html += "<span class=\"VT_videoname fgcolor smallfont\" title=\""+videoname+"\">" + videoname + "</span>";
    html += "</div>";

    html += "</div>";

    return html;
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

