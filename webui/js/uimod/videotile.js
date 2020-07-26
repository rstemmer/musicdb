
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

function CreateVideoTile(MDBVideo)
{
    return _CreateVideoTile(MDBVideo, "medium");
}
function CreateSmallVideoTile(MDBVideo)
{
    return _CreateVideoTile(MDBVideo, "small");
}

// valid sizes: medium, small
function _CreateVideoTile(MDBVideo, size)
{
    let html        = "";
    let imgpath     = EncodeVideoThumbnailPath(MDBVideo.framesdirectory, MDBVideo.thumbnailfile, "150×150");
    let anipath     = EncodeVideoThumbnailPath(MDBVideo.framesdirectory, MDBVideo.previewfile,   "150×150");
    let videoid     = MDBVideo.id;
    let videoname   = MDBVideo.name;
    let videorelease= MDBVideo.release;
    let videorequest= "MusicDB_Request(\'GetVideo\', \'ShowVideo\', {videoid:"+videoid+"});";
    let datawidth   = "data-size=\"" + size + "\"";

    html += "<div";
    html += " class=\"AT_albumentry\"";
    html += " " + datawidth;
    html += " onClick=\"" + videorequest + "\"";
    html += ">";

    // Cover
    html += "<div title=\"Show this Video\" class=\"AT_albumcover\" " + datawidth + ">";
    html += "  <img src=\"" + imgpath + "\"";
    html += "    onmouseover=\"this.src=\'"+anipath+"\'\"";
    html += "    onmouseout =\"this.src=\'"+imgpath+"\'\"";
    html += "  \">";
    html += "</div>";
    /* 
    <img src="http://icons.iconarchive.com/icons/fasticon/angry-birds/128/yellow-bird-icon.png" 
        onmouseover="this.src='http://icons.iconarchive.com/icons/fasticon/angry-birds/128/red-bird-icon.png'"
        onmouseout="this.src='http://icons.iconarchive.com/icons/fasticon/angry-birds/128/yellow-bird-icon.png'"
        border="0" alt=""/>
    */

    html += "<div class=\"AT_albummetadata\">";
    if(size != "small")
        html += "<span class=\"AT_albumrelease hlcolor smallfont\">" + videorelease + "</span>";
    html += "<span class=\"AT_albumname fgcolor smallfont\" title=\""+videoname+"\">" + videoname + "</span>";
    html += "</div>";

    html += "</div>";

    return html;
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

