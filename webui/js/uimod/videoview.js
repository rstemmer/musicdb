
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

    html += "<div id=AlbumViewBox>"; // main box

    // Album title and artist infos
    html += _VV_CreateHeadline(MDBArtist, MDBAlbum, MDBSong, MDBVideo);

    html += "<div id=ABVSongs>";
    html += "    <video controls preload=none >";
    html += "       <source src=\"/musicdb/music/"+MDBVideo.path+"\">";
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
    html += "<div id=ABVHeadlineBox title=\"Origin: " + MDBVideo.origin + "\"";
    //html += " oncontextmenu=\"ToggleVisibility(\'ABVSettings\'); return false;\""; // Show settings
    html += ">";

    html += "<div id=ABVMainHeadline>";
    // Video name
    html += "<span ";
    html += " id=ABVAlbumName";
    html += " class=\"fgcolor\">";
    html += MDBVideo.name;
    html += "</span>";

    html += "</div>";
    html += "<div id=ABVSubHeadline class=\"smallfont\">";
    // Artist name
    html += "<span ";
    html += " onClick=\"ScrollToArtist(" + MDBArtist.id + ");\"";
    html += " id=ABVArtistName";
    html += " class=\"hlcolor\">";
    html += MDBArtist.name;
    html += "</span>";

    html += "<span id=ABVSHLSeparator class=\"fgcolor\"> – </span>";
    
    // Video release
    html += "<span ";
    html += " id=ABVAlbumRelease";
    html += " class=\"hlcolor\">";
    html += MDBVideo.release;
    html += "</span>";

    html += "</div>";
    html += "</div>";
    return html;
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

