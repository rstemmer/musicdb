
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

    // Show the video
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

    // Show settings
    let settingsid = "VV_videosettings_" + MDBVideo.id;
    html += "    <div id=\"" + settingsid + "\" class=\"VV_videosettings fmcolor frame\">";
    html += "        <div class=\"VV_videosettings_row\">";
    html += _VV_CreateVideoSettings(MDBVideo, MDBTags);
    html += "        </div>";
    html += "    <div class=\"VV_videosettings_row\">";
    html += "    </div>";
    html += "    </div>";

    html += "</div>"; // VVVideo
    html += "</div>"; // main box

    // Push content to screen
    $("#"+parentID).html(html);
    UpdateVideoSettings(MDBVideo, MDBTags, true);
    return;
}


function _VV_CreateHeadline(MDBArtist, MDBAlbum, MDBSong, MDBVideo)
{
    let html = "";
    html += "<div id=VVHeadlineBox title=\"Origin: " + MDBVideo.origin + "\">";

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


function _VV_CreateVideoSettings(MDBVideo, MDBVideoTags)
{
    let videoid = MDBVideo.id;
    let html = "";
    let moodboxid = "VVS_moodbox_" + videoid;
    let propboxid = "VVS_propbox_" + videoid;
    let tagsboxid = "VVS_tagsbox_" + videoid;

    html += "<div id=\""+moodboxid+"\" class=\"VVS_moodbox hlcolor\">"
    html += "</div>";
    html += "<div id=\""+propboxid+"\" class=\"VVS_propbox hlcolor\">";
    html += "</div>";
    //html += "<div id=\""+tagsboxid+"\" class=\"VVS_tagsbox\">";
    //html += Taginput_Create("VVS_genre_"    + videoid, videoid, "Genre",    "Song");
    //html += Taginput_Create("VVS_subgenre_" + videoid, videoid, "Subgenre", "Song");
    //html += "</div>";

    return html;
}

function UpdateVideoSettings(MDBVideo, MDBVideoTags, initialize)
{
    let videoid = MDBVideo.id;
    let moodboxid = "VVS_moodbox_" + videoid;
    let propboxid = "VVS_propbox_" + videoid;
    let tagsboxid = "VVS_tagsbox_" + videoid;

    if(initialize == true)
        Videotags_ShowMoodControl(moodboxid, moodboxid);

    Videotags_UpdateMoodControl(moodboxid, MDBVideoTags);
    
    if(initialize == true)
        Videoproperties_ShowControl(propboxid, propboxid);

    Videoproperties_UpdateControl(propboxid, MDBVideo, initialize); // true: initialize and reset like/dislike buttons

    //Taginput_Update("VVS_genre_"    + videoid, MDBVideoTags);
    //Taginput_Update("VVS_subgenre_" + videoid, MDBVideoTags);
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

