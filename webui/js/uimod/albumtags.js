
"use strict";

/*
 *
 * Requirements:
 *   - JQuery
 *   - tools/hovpacoty.css
 * Show:
 * Functions:
 * Callbacks:
 * Recommended Paths:
 * Trigger: (fnc -> sig)
 *
 */

/*
 * This function creates a control-element to set or remove album tags.
 *
 * Currently, only genres are supported
 *
 * The the albumid is also prefix and allows multiple element in one document
 */
function Albumtags_CreateGenreControl(albumid, albumtags)
{
    var html = "";

    // Create a list of tags that are set
    var taglist = [];
    for(let tag of albumtags.genres)
    {
        taglist.push(tag.id);
    }

    html += "<div id=AT" + albumid + "Box class=\"ATAGSBox\">";

    // Get all available genre tags
    var genres;
    genres = Tagmanager_GetGenres();
    if(genres == null)
        return;

    // Create a button for each genre
    for(let genre of genres)
        html += _AT_CreateTagButton(albumid, genre, (taglist.indexOf(genre.id) >= 0));

    html += "</div>";

    return html;
}


function _AT_CreateTagButton(albumid, MDBTag, state)
{
    var html = "";

    html += "<div";
    html += " id=AT_" + albumid + "_TagButton_" + MDBTag.id;
    html += " class=\"ATtagbutton frame fmcolor hlcolor smallfont\"";
    html += " data-checked=" + state;
    html += " data-albumid=" + albumid;
    html += " onClick=\"_AT_onToggleTagButton(\'" + albumid + "\', \'" + MDBTag.id + "\');\"";
    html += ">";
    html += MDBTag.name;
    html += "</div>";

    return html;
}


function _AT_onToggleTagButton(albumid, tagid)
{
    var buttonid = "#AT_" + albumid + "_TagButton_" + tagid;
    var state    = $(buttonid).attr("data-checked");
    var newstate = null;

    if(state === "false")
    {
        newstate = true;
        window.console && console.log("SetAlbumTag("+albumid+", "+tagid+")");
        MusicDB_Call("SetAlbumTag", {albumid:albumid, tagid:tagid});
    }
    else
    {
        newstate = false;
        window.console && console.log("RemoveAlbumTag("+albumid+", "+tagid+")");
        MusicDB_Call("RemoveAlbumTag", {albumid:albumid, tagid:tagid});
    }

    $(buttonid).attr("data-checked", newstate);
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

