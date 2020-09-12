
"use strict";

/*
 * This class provides the artistloader.
 * It is possible to select a set of genres and/or to reload the artists-list
 *
 * Requirements:
 *   - JQuery
 *   - Font-Awesome
 *   - mdb_buttons.css
 * Show:
 *   - Button_AddSongToQueue(songid)
 *   - Button_AddRandomSongToQueue()
 *   - Button_AddAlbumToQueue(albumid)
 *   - Button_QueueEntryControls(songid, qposition)
 *   - Button_Lyrics(songid, lyricsstate)
 * Functions:
 * Callbacks:
 * Recommended Paths:
 * Trigger: (fnc -> sig)
 *
 */

function Button_AddSongToQueue(songid)
{
    var html = "";
    html += "<div class=\"BTN_box\">";
    
    html += BTN_CreateIconButton(
        "<i class=\"fa fa-plus-circle\" title=\"Add this song to the queue\"></i>",
        "MusicDB_Call(\'AddSongToQueue\', {songid:"+songid+", position:\'last\'});");
    html += BTN_CreateSeparator();
    html += BTN_CreateIconButton(
        "<i class=\"fa fa-play-circle\" title=\"Play this song next\"></i>",
        "MusicDB_Call(\'AddSongToQueue\', {songid:"+songid+", position:\'next\'});");

    html += "</div>";
    return html;
}

function Button_AddVideoToQueue(videoid)
{
    let html = "";
    html += "<div class=\"BTN_box\">";
    
    html += BTN_CreateIconButton(
        "<i class=\"fa fa-plus-circle\" title=\"Add this video to the queue\"></i>",
        "MusicDB_Call(\'AddVideoToQueue\', {videoid:"+videoid+", position:\'last\'});");
    html += BTN_CreateSeparator();
    html += BTN_CreateIconButton(
        "<i class=\"fa fa-play-circle\" title=\"Play this video next\"></i>",
        "MusicDB_Call(\'AddVideoToQueue\', {videoid:"+videoid+", position:\'next\'});");

    html += "</div>";
    return html;
}

function Button_AddAlbumToQueue(albumid)
{
    var html = "";
    html += "<div class=\"BTN_box\">";
    
    html += BTN_CreateIconButton(
        "<i class=\"fa fa-plus-square\" title=\"Add whole album to queue\"></i>",
        "MusicDB_Call(\'AddAlbumToQueue\', {albumid:"+albumid+"});");
    html += BTN_CreateSeparator();
    html += BTN_CreateSeparator();
    html += BTN_CreateSeparator();
    html += BTN_CreateIconButton(
        "<i class=\"fa fa-plus-circle\" title=\"Add random song to the queue\"></i>",
        "MusicDB_Call(\'AddRandomSongToQueue\', {albumid:"+albumid+", position:\'last\'});");
    html += BTN_CreateSeparator();
    html += BTN_CreateIconButton(
        "<i class=\"fa fa-play-circle\" title=\"Play random song next\"></i>",
        "MusicDB_Call(\'AddRandomSongToQueue\', {albumid:"+albumid+", position:\'next\'});");

    html += "</div>";
    return html;
}

function Button_ShowSettings(containerid)
{
    var html = "";
    html += "<div class=\"BTN_box\">";
    
    html += BTN_CreateIconButton(
        "<i class=\"fa fa-gears\"></i>",
        "ToggleVisibility(\'"+containerid+"\');");

    html += "</div>";
    return html;
}

 

function Button_Lyrics(lyricsstate, callstring)
{
    var html = "";
    html += "<div class=\"BTN_box\">";

    var icon;
    if(lyricsstate == 0) // empty
        icon = "fa-comment-o";
    else if (lyricsstate == 1) // from file
        icon = "fa-commenting-o";
    else if (lyricsstate == 2) // from net
        icon = "fa-commenting-o";
    else if (lyricsstate == 3) // from user
        icon = "fa-commenting";
    else if (lyricsstate == 4) // no lyrics - instrumental 
        icon = "fa-comment";
    else // unexpected state
        icon = "fa-warning";
    
    html += BTN_CreateIconButton(
        "<i class=\"fa " + icon + " hovpacity\" title=\"Show lyrics\"></i>",
        callstring);

    html += "</div>";
    return html;
}

function Button_LyricsViewControls(songid, albumid)
{
    var albumrequest = "MusicDB_Request(\'GetAlbum\', \'ShowAlbum\', {albumid:"+albumid+"});";
    var editurl      = "lyricist.html?songid="+songid;
    var editrequest  = "open(\'" + editurl + "\', \'_blank\', \'\')";

    var html = "";
    html += "<div class=\"BTN_box\">";
    
    // edit-button
    html += BTN_CreateIconButton(
        "<i class=\"fa fa-pencil-square-o hovpacity\" title=\"Open lyrics editor\"></i>",
        editrequest);

    html += BTN_CreateSeparator();
    // show album again
    html += BTN_CreateIconButton(
        "<i class=\"fa fa-list\" title=\"Go back to album view\"></i>",
        albumrequest);

    html += "</div>";
    return html;
}


function Button_RelationshipControls(mainsongid, relatedsongid, relatedsongname, weight)
{
    var html = "";
    html += "<div class=\"BTN_box\">";

    html += BTM_TextLeft("<span class=\"smallfont\">(" + weight + ")</span>");
    html += BTN_CreateIconButton(
        "<i class=\"fa fa-chain-broken\" title=\"Remove relationship with this song\"></i>",
        "_BTN_CutRelationship(" + mainsongid + ", " + relatedsongid + ", \'" + relatedsongname + "\');");

    html += "</span>";
    html += "</div>";
    return html;
}
function _BTN_CutRelationship(songid, relatedsongid, relatedsongname)
{
    // make sure this was no accident
    var confirmation = confirm("Remove relation to song \"" + relatedsongname + "\"?");
    if(confirmation == false) 
        return;

    MusicDB_Request("CutSongRelationship", "ShowSongRelationship", 
        {songid:songid, relatedsongid:relatedsongid});
}


function BTN_CreateSeparator()
{
    return "<span class=\"BTN_separator\"></span>";
}


function BTN_CreateIconButton(icon, onclick)
{
    var html = "";
    html += "<span";
    html += " class=\"BTN_button\"";
    html += " onClick=\""+onclick+"\">";
    html += icon;
    html += "</span>";
    return html;
}

function BTM_TextLeft(text)
{
    var html = "";
    html += "<span";
    html += " class=\"BTN_lefttext\"";
    html += ">";
    html += text;
    html += "</span>";
    return html;
}


function ToggleVisibility(id)
{
    id = "#" + id;
    if($(id).css("display") != "none")
        $(id).css("display", "none");
    else
        $(id).css("display", "flex");
}
// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

