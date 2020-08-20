
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
    html += "       id=VideoPreviewPlayer";
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
    html += _VV_CreateVideoSettings(MDBVideo, MDBTags);
    html += "    </div>";

    html += "</div>"; // VVVideo
    html += "</div>"; // main box

    // Push content to screen
    $("#"+parentID).html(html);
    UpdateVideoSettings(MDBVideo, MDBTags, true);
    //UpdateStyle(MDBAlbum.bgcolor, MDBAlbum.fgcolor, MDBAlbum.hlcolor);

    let videoplayerid     = "VideoPreviewPlayer";
    let playtimeselection = document.getElementById("BeginEndSelection");
    let begintimeselect   = new TimeSelect("Video Begin", videoplayerid);
    let endtimeselect     = new TimeSelect("Video End",   videoplayerid);
    
    playtimeselection.appendChild(begintimeselect.GetHTMLElement());
    playtimeselection.appendChild(endtimeselect.GetHTMLElement());

    begintimeselect.SetValidationFunction((time) => 
        {
            let endtime = endtimeselect.GetSelectedTime();
            if(endtime == null)
                return true;

            if(time < endtime)
                return true;

            return `begintimeselect: ${time} >= ${endtime}`;
        }
    );
    endtimeselect.SetValidationFunction((time) =>
        {
            let begintime = endtimeselect.GetSelectedTime();
            if(begintime == null)
                return true;

            if(time > begintime)
                return true;

            return `endtimeselect: ${time} <= ${begintime}`;
        }
    );
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
    let bgcolor   = MDBVideo.bgcolor || "#000000";
    let hlcolor   = MDBVideo.hlcolor || "#000000";    
    let fgcolor   = MDBVideo.fgcolor || "#000000";

    // Moods and Properties
    html += "<div class=\"VV_videosettings_row\">";
    html += "    <div id=\""+moodboxid+"\" class=\"VVS_moodbox hlcolor\">"
    html += "    </div>";
    html += "    <div id=\""+propboxid+"\" class=\"VVS_propbox hlcolor\">";
    html += "    </div>";
    html += "</div>";

    // Genres and Sub-genres
    html += "<div class=\"VV_videosettings_row\">";
    html += "    <div id=\""+tagsboxid+"\" class=\"VVS_tagsbox\">";
    html += Taginput_Create("VVS_genre_"    + videoid, videoid, "Genre",    "Video");
    html += Taginput_Create("VVS_subgenre_" + videoid, videoid, "Subgenre", "Video");
    html += "    </div>";
    html += "</div>";

    // Colors
    html += "<div class=\"VV_videosettings_row\">";
    html += "   <span class=\"ABVSettingName\">Background:</span>";
    html += CreateColorInput("CI_BGColor", bgcolor, 
        "_VV_onColorSave("+videoid+", \'CI_BGColor\');",
        _VV_onColorChange
        );
    
    html += "   <span class=\"ABVSettingName\">Foreground:</span>";
    html += CreateColorInput("CI_FGColor", fgcolor, 
        "_VV_onColorSave("+videoid+", \'CI_FGColor\');",
        _VV_onColorChange
        );
    
    html += "   <span class=\"ABVSettingName\">Highlight:</span>";
    html += CreateColorInput("CI_HLColor", hlcolor, 
        "_VV_onColorSave("+videoid+", \'CI_HLColor\');",
        _VV_onColorChange
        );
    html += "</div>";

    // Begin/End Time Selection
    html += "<div class=\"VV_videosettings_row\" id=\"BeginEndSelection\">";
    // TODO
    html += "</div>";
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

    Taginput_Update("VVS_genre_"    + videoid, MDBVideoTags);
    Taginput_Update("VVS_subgenre_" + videoid, MDBVideoTags);
}



function _VV_onColorSave(videoid, elementid)
{
    var color = $("#"+elementid).val();

    // Do not send bullshit even if the server could handle it
    if(color == "#NANNANNAN")
        return;
    if(color == null || color == "null")
        return;

    // this is the NULL-Color. It would be so fucking bad designe-style that I will never use it
    if(color == "#000000")
        return;

    var colorname = "";
    if(elementid == "CI_BGColor")
        colorname = "bgcolor";
    else if(elementid == "CI_FGColor")
        colorname = "fgcolor";
    else if(elementid == "CI_HLColor")
        colorname = "hlcolor";
    else
        return;

    MusicDB_Call("SetVideoColor", {videoid:videoid, colorname:colorname, color:color});
}



function _VV_onColorChange(elementid, color)
{
    if(elementid == "CI_BGColor")
    {
        $(".bgcolor").css("background-color", color);
    }
    else if(elementid == "CI_FGColor")
    {
        $(".fgcolor").css("color", color);
    }
    else if(elementid == "CI_HLColor")
    {
        $(".hlcolor").css("color", color);
        $(".fmcolor").css("border-color", color);
    }
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

