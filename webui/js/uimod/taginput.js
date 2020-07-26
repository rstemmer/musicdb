
"use strict";

//function Taginput_UpdateTags();
//

/*
 * on fnc:GetSong/GetAlbum, sig:UpdateTagInput
 *      Taginput_Update(pass.taginputid, args.tags);
 *
 */

/**
 * @param {string} taginputid - id of the input element
 * @param {integer} targetid - songid or albumid (to bind this element with a song
 * @param {string} tagclass - ``"Genre"``, ``"Subgenre"``, ``"Mood"``
 * @param {string} target - ``"Song"``, ``"Album"``, ``"Video"``
 *
 * @returns {string} HTML code of the Taginput control
 */
function Taginput_Create(taginputid, targetid, tagclass, target)
{
    var html = "";
    html += "<div id=\"" + taginputid + "\"";
    html += " data-tagclass=\'" + tagclass + "\'";
    html += " data-target=\'"   + target   + "\'";
    html += " data-targetid="   + targetid + "";
    html += " class=\"TAGI_Container\">";

    html += "<div class=\"TAGI_Frame TAGI_FrameStyle hlcolor\">";

    // Left Icon
    html += "<div class=\"TAGI_IconBoxLeft\">";
    html += "<i class=\"fa fa-tags\"></i>";
    html += "</div>";

    // Input element
    html += "<div class=\"TAGI_InputBox\">";
    html += "<div id=\"TAGI_TagCollection_" + tagclass + target + targetid+"\"";
    html += " class=\"TAGI_TagCollection bgcolor frame fmcolor\">";
    html += "</div>";
    html += "</div>";

    // Empty element to place set tags later on
    html += "<div id=\"" + taginputid + "_tags\" class=\"TAGI_TagsBox\">";
    html += "</div>";

    // dropdown menu button
    html += "<div";
    html += " class=\"TAGI_IconBoxRight\"";
    html += " onClick=\"_TAGI_onShowAll(\'" + taginputid + "\');\"";
    html += " title=\"Set further tags\""
    html += ">";
    html += "<i class=\"fa fa-chevron-circle-down\"></i>";
    html += "</div>";

    html += "</div>";

    html += "</div>";
    return html;
}

/**
 *
 * TODO: mode: "show" or "edit" - default is "edit" if mode gets not set
 *
 *
 * @param {string} taginputid - ID of the taginput that shall be updated
 * @param {object} MDBTags - MusicDB Tags either from an Album or a Song, including all tagclasses
 * @param {string} [mode] - The mode the taginput element shall be used in. Default is ``"edit"``.
 *
 * @returns *nothing*
  */
function Taginput_Update(taginputid, MDBTags, mode)
{
    mode = mode || "edit";

    var jqid = "#"+taginputid;

    var targetid = $("#"+taginputid).attr("data-targetid");
    var tagclass = $(jqid).attr("data-tagclass");
    var target   = $("#"+taginputid).attr("data-target");

    // Make sure that there are no foreign tags - this may happen due to race conditions. Just be sure.
    if(target === "Song")
    {
        if(MDBTags.songid != targetid)
        {
            window.console && console.log("ERROR: The tags to update are for a different Song!");
            window.console && console.log("  This target: " + targetid + "; Received tags: " + MDBTags.songid);
            return;
        }
    }
    else if(target === "Video")
    {
        if(MDBTags.videoid != targetid)
        {
            window.console && console.log("ERROR: The tags to update are for a different Video!");
            window.console && console.log("  This target: " + targetid + "; Received tags: " + MDBTags.videoid);
            return;
        }
    }
    else if(target === "Album")
    {
        if(MDBTags.albumid != targetid)
        {
            window.console && console.log("ERROR: The tags to update are for a different Album!");
            window.console && console.log("  This target: " + targetid + "; Received tags: " + MDBTags.albumid);
            return;
        }
    }

    var htmltaglist;
    htmltaglist = _TAGI_CreateTagList(taginputid, targetid, MDBTags, mode);
    
    $(jqid+"_tags").html(htmltaglist);
    $(jqid).data("targettags", MDBTags);
}

/**
 * This is a light version to just show the tags (exept approval for AI set tags)
 *
 * @param {string} taginputid - id of the input element
 * @param {integer} targetid - songid or albumid (to bind this element with a song
 * @param {MDBTag-list} taglist - list of tags that shall be shown (all classes)
 * @param {string} tagclass - ``"Genre"``, ``"Subgenre"``, ``"Mood"``
 * @param {string} target - ``"Song"``, ``"Album"``, ``"Video"``
 *
 * @returns *nothing*
 */
function Taginput_Show(parentid, taginputid, targetid, MDBTags, tagclass, target)
{
    var html = "";
    html += "<div id=\"" + taginputid + "\"";
    html += " data-tagclass=\'" + tagclass + "\'";
    html += " data-target=\'"   + target   + "\'";
    html += " data-targetid="   + targetid + "";
    html += " class=\"TAGI_Container\">";

    html += "<div class=\"TAGI_Frame hlcolor smallfont\">";

    // Empty element to place set tags later on
    html += "<div id=\"" + taginputid + "_tags\" class=\"TAGI_TagsBox\">";
    html += "</div>";

    html += "</div>";

    html += "</div>";

    // Show
    $("#" + parentid).html(html);

    Taginput_Update(taginputid, MDBTags, "show");
    UpdateStyle();    // Update new tag frames
}


// mode: "add", "remove"
// MDBTags:  if mode=="edit": list of tags set for a song - they must be removeable
//           if mode=="show": only show the approval-button, otherwise nothing is editable
//           if mode=="add":  all available tags - they must be addable
//           the tags are separated into classes!
function _TAGI_CreateTagList(taginputid, targetid, MDBTags, mode)
{
    var html = "";
    var targetid = $("#"+taginputid).attr("data-targetid");
    var tagclass = $("#"+taginputid).attr("data-tagclass");

    // Only select relevant tagclass
    var MDBTagList;
    if(tagclass === "Genre")
        MDBTagList = MDBTags.genres;
    else if(tagclass === "Subgenre")
        MDBTagList = MDBTags.subgenres;
    else if(tagclass === "Mood")
        MDBTagList = MDBTags.moods;
    else
    {
        window.console && console.log("Invalid tagclass!");
        return;
    }

    // Creatze taglist - there may be some filtering
    var taglist = [];

    if(mode === "add")
    {
        // Only show tags that are not already added
        let storedtags = $("#"+taginputid).data("targettags");
        var MDBSongTags;
        if(tagclass === "Genre")
            MDBSongTags = storedtags.genres;
        else if(tagclass === "Subgenre")
            MDBSongTags = storedtags.subgenres;
        else if(tagclass === "Mood")
            MDBSongTags = storedtags.moods;

        nexttag: for(let tag of MDBTagList) // For each possibly showable tag
        {
            // Do not add already set tags
            for(let songtag of MDBSongTags) // Check if already set
            {
                if(tag.id === songtag.id)
                    continue nexttag;
            }

            // only use subgenres that are in the set genres
            if(tagclass === "Subgenre")
            {
                for(let genre of storedtags.genres)    // check for each genre of the song if subgenre is subset of it
                {
                    if(tag.parentid === genre.id)
                    {
                        taglist.push(tag)
                        continue nexttag;
                    }
                }
            }
            else
            {
                taglist.push(tag);
            }
        }
    }
    else    // No filter for this mode
    {
        taglist = MDBTagList;
    }

    for(let tag of taglist)
    {
        html += "<div class=\"TAGI_TagElement frame fmcolor\">";

        if(tag.icon !== null)
        {
            html += "<div class=\"TAGI_TagElement_Icon\">";
            html += tag.icon;
            html += "</div>";
        }
        
        html += "<div class=\"TAGI_TagElement_Name\">";
        html += tag.name;
        html += "</div>";

        // add-button
        if(mode === "add")
        {
            html += "<div class=\"TAGI_TagElement_Button\"";
            html += " title=\"Set tag\"";
            html += " onClick=\"_TAGI_onAddTag(\'"+taginputid+"\', " + tag.id + ");\">";
            html += "<i class=\"fa fa-plus-circle\"></i>";
            html += "</div>";
        }
        if(mode === "show" || mode === "edit")
        {
            // in case the tag was set by an AI
            if(tag.approval === 0)
            {
                // confidence-bar
                html += "<div class=\"TAGI_TagElement_Confidence\" title=\"" + (tag.confidence * 100).toFixed(2) + "%\">";
                html += "<div class=\"TAGI_TagElement_ConfidenceBar tinyfont\"";
                html += " style=\"height: " + Math.floor(tag.confidence * 100.0) + "%;\">";
                html += Math.floor(tag.confidence * 100);
                html += "</div>";
                html += "</div>";

                // approval-button
                html += "<div class=\"TAGI_TagElement_Button\"";
                html += " title=\"Approve tag\"";
                html += " onClick=\"_TAGI_onApproveTag(\'"+taginputid+"\', " + tag.id + ");\">";
                html += "<i class=\"fa fa-check-circle\"></i>";
                html += "</div>";
            }
        }
        if(mode === "edit" || (mode === "show" && tag.approval === 0))
        {
            // remove-button
            html += "<div class=\"TAGI_TagElement_Button\""
            html += " title=\"Remove tag\"";
            html += " onClick=\"_TAGI_onRemoveTag(\'"+taginputid+"\', " + tag.id + ");\">";
            html += "<i class=\"fa fa-times-circle\"></i>";
            html += "</div>";
        }

        html += "</div>";
    }

    return html;
}


function _TAGI_onApproveTag(taginputid, tagid)
{
    var targetid = $("#"+taginputid).attr("data-targetid");
    var target   = $("#"+taginputid).attr("data-target");
    
    // When calling SetSongTag via web API, the approval is always "1: Set By User".
    // So by just calling SetSongTag, the song gets updated as intended.
    
    if(target === "Song")
        MusicDB_Request("SetSongTag",  "UpdateTagInput", {songid:targetid,  tagid:tagid}, {taginputid:taginputid});
    else if(target === "Video")
        MusicDB_Request("SetVideoTag", "UpdateTagInput", {videoid:targetid, tagid:tagid}, {taginputid:taginputid});
    else if(target === "Album")
        MusicDB_Request("SetAlbumTag", "UpdateTagInput", {albumid:targetid, tagid:tagid}, {taginputid:taginputid});
}
function _TAGI_onRemoveTag(taginputid, tagid)
{
    var targetid = $("#"+taginputid).attr("data-targetid");
    var target   = $("#"+taginputid).attr("data-target");

    if(target === "Song")
        MusicDB_Request("RemoveSongTag",  "UpdateTagInput", {songid:targetid,  tagid:tagid}, {taginputid:taginputid});
    else if(target === "Video")
        MusicDB_Request("RemoveVideoTag", "UpdateTagInput", {videoid:targetid, tagid:tagid}, {taginputid:taginputid});
    else if(target === "Album")
        MusicDB_Request("RemoveAlbumTag", "UpdateTagInput", {albumid:targetid, tagid:tagid}, {taginputid:taginputid});
}
function _TAGI_onAddTag(taginputid, tagid)
{
    var targetid = $("#"+taginputid).attr("data-targetid");
    var target   = $("#"+taginputid).attr("data-target");
    var tagclass = $("#"+taginputid).attr("data-tagclass");

    if(target === "Song")
        MusicDB_Request("SetSongTag",  "UpdateTagInput", {songid:targetid,  tagid:tagid}, {taginputid:taginputid});
    if(target === "Video")
        MusicDB_Request("SetVideoTag", "UpdateTagInput", {videoid:targetid, tagid:tagid}, {taginputid:taginputid});
    else if(target === "Album")
        MusicDB_Request("SetAlbumTag", "UpdateTagInput", {albumid:targetid, tagid:tagid}, {taginputid:taginputid});

    $("#TAGI_TagCollection_" + tagclass + target + targetid).css("display", "none");
}

function _TAGI_onShowAll(taginputid)
{
    var targetid = $("#"+taginputid).attr("data-targetid");
    var target   = $("#"+taginputid).attr("data-target");
    var tagclass = $("#"+taginputid).attr("data-tagclass");
    var listid   = "#TAGI_TagCollection_" + tagclass + target + targetid;

    if($(listid).css("display") != "none")
    {
        $(listid).css("display", "none");
        return;
    }

    var taglist;
    taglist = Tagmanager_GetTags();

    var htmltaglist
    htmltaglist = _TAGI_CreateTagList(taginputid, targetid, taglist, "add");
    $(listid).html(htmltaglist);
    $(listid).css("display", "flex");
}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

