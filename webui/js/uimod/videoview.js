
"use strict";

/*
 * This class shows a video
 *
 * Requirements:
 *   - JQuery
 *   - mdb_albumview.css
 *   - scrollto.js
 *   - lyrics
 * Show:
 *   - ShowVideo(parentID, MDBArgs);
 * Functions:
 * Callbacks:
 * Recommended Paths:
 * Trigger: (fnc -> sig)
 */

// MDBAlbum and MDBSong can be null
function ShowVideo(parentID, MDBArtist, MDBAlbum, MDBSong, MDBVideo, MDBTags)
{
    //window.console && console.log(args);
    let html = "";

    html += "<div id=VideoViewBox>"; // main box

    // Album title and artist infos
    html += _VV_CreateHeadline(MDBArtist, MDBAlbum, MDBSong, MDBVideo);

    let poster = EncodeVideoThumbnailPath(MDBVideo.framesdirectory, MDBVideo.thumbnailfile);
    html += "<div id=VVVideo>";
    html += "    <video ";
    html += "       class=VV_player";
    html += "       controls";
    html += "       width="  + MDBVideo.xresolution;
    html += "       height=" + MDBVideo.yresolution;
    html += "       poster=" + poster;
    html += "       preload=none";
    html += "       >";
    html += "       <source src=\"/musicdb/music/" + MDBVideo.path + "\">";
    html += "    </video>";
    html += "</div>";

    html += "</div>"; // main box

    // Push content to screen
    $("#"+parentID).html(html);
    return;
}


function _VV_CreateHeadline(MDBArtist, MDBAlbum, MDBSong, MDBVideo)
{
    let html = "";
    html += "<div id=VVHeadlineBox title=\"Origin: " + MDBVideo.origin + "\"";
    //html += " oncontextmenu=\"ToggleVisibility(\'ABVSettings\'); return false;\""; // Show settings
    html += ">";

    html += "<div id=VVMainHeadline>";
    // Video name
    html += "<span ";
    html += " id=VVAlbumName";
    html += " class=\"fgcolor\">";
    html += MDBVideo.name;
    html += "</span>";

    html += "</div>";
    html += "<div id=VVSubHeadline class=\"smallfont\">";
    // Artist name
    html += "<span ";
    html += " onClick=\"ScrollToArtist(" + MDBArtist.id + ");\"";
    html += " id=VVArtistName";
    html += " class=\"hlcolor\">";
    html += MDBArtist.name;
    html += "</span>";

    html += "<span id=VVSHLSeparator class=\"fgcolor\"> – </span>";
    
    // Video release
    html += "<span ";
    html += " id=VVAlbumRelease";
    html += " class=\"hlcolor\">";
    html += MDBVideo.release;
    html += "</span>";

    html += "</div>";
    html += "</div>";
    return html;
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

