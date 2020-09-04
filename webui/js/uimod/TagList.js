// MusicDB,  a music manager with web-bases UI that focus on music.
// Copyright (C) 2017-2020  Ralf Stemmer <ralf.stemmer@gmx.net>
// 
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
// 
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
// 
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.

"use strict";


class Tag
{
    constructor(MDBTag)
    {
        this.tagname        = MDBTag.name;
        this.tagid          = MDBTag.id;
        this.confidence     = MDBTag.confidence;
        this.approval       = MDBTag.approval;  // 0: Set by AI, >0: Set by User

        this.onclick        = null;
        this.onapprove      = null;
        this.onremove       = null;

        this.approvebutton  = new SVGButton("Approve", ()=>{this.onApprove()});
        this.removebutton   = new SVGButton("Remove",  ()=>{this.onRemove()});
        this.addbutton      = new SVGButton("Add",     ()=>{this.onClick()});
        this.approvebutton.SetTooltip("Confirm this Tag");
        this.removebutton.SetTooltip("Remove this Tag");
        this.addbutton.SetTooltip("Add this Tag");
        this.nameelement    = document.createElement("div");
        this.nameelement.innerText = this.tagname;

        this.element        = document.createElement("div");
        this.element.classList.add("frame");
        this.element.classList.add("flex-row");
        this.element.classList.add("tag");
        this.element.appendChild(this.nameelement);
        this.element.onclick = ()=>{this.onClick();};
    }



    SetConfidence(confidence)
    {
        let percent  = Math.round(confidence * 100)
        let ratiobar = new RatioBar(percent);

        ratiobar.SetTooltip("Confidence: " + percent + "%");

        this.element.appendChild(ratiobar.GetHTMLElement());
    }



    SetClickAction(onclick)
    {
        this.onclick = onclick;
    }
    SetAddAction(onclick)
    {
        this.onclick = onclick;
        this.element.appendChild(this.addbutton.GetHTMLElement());
    }
    SetRemoveAction(onremove)
    {
        this.onremove = onremove;
        this.element.appendChild(this.removebutton.GetHTMLElement());
    }
    SetApproveAction(onapprove)
    {
        this.onapprove = onapprove;
        this.element.appendChild(this.approvebutton.GetHTMLElement());
    }



    GetHTMLElement()
    {
        return this.element;
    }



    onApprove()
    {
        event.stopPropagation();

        if(typeof this.onapprove === "function")
            this.onapprove(this.tagid);
    }

    onRemove()
    {
        event.stopPropagation();

        if(typeof this.onremove === "function")
            this.onremove(this.tagid);
    }

    onClick()
    {
        event.stopPropagation();

        if(typeof this.onclick === "function")
            this.onclick(this.tagid);
    }
}



class TagListView
{
    // Optional allowremove - if true, remove button is always visible
    constructor(allowremove)
    {
        this.allowremove= allowremove;
        this.taglist    = new Array();
        this.musictype  = null;
        this.musicid    = null;
        this.element    = document.createElement("div");
        this.element.classList.add("tagview");
        this.element.classList.add("flex-row");
        this.element.classList.add("smallfont");
        this.element.classList.add("hlcolor");
    }



    GetHTMLElement()
    {
        return this.element;
    }



    // musictype: "audio" or "video" or "album"
    Update(musictype, musicid, MDBTagArray)
    {
        this.musicid            = musicid;
        this.musictype          = musictype;
        this.taglist            = new Array();
        this.element.innerHTML  = "";

        for(let MDBTag of MDBTagArray)
        {
            let tag;
            if(MDBTag.approval > 0)
            {
                if(this.allowremove === true)
                {
                    tag = new Tag(MDBTag);
                    tag.SetRemoveAction((tagid)=>{this.onRemove(tagid);});
                }
                else
                {
                    tag = new Tag(MDBTag);
                }
            }
            else
            {
                tag = new Tag(MDBTag);
                tag.SetConfidence(MDBTag.confidence);
                tag.SetApproveAction((tagid)=>{this.onApprove(tagid);});
                tag.SetRemoveAction((tagid)=>{this.onRemove(tagid);});
            }

            this.taglist.push(tag);
            this.element.appendChild(tag.GetHTMLElement());
        }

    }



    onApprove(tagid)
    {
        switch(this.musictype)
        {
            case "audio":
                MusicDB_Request("SetSongTag",  "UpdateTagInput", {songid:this.musicid,  tagid:tagid});
                break;
            case "video":
                MusicDB_Request("SetVideoTag", "UpdateTagInput", {videoid:this.musicid, tagid:tagid});
                break;
            case "album":
                MusicDB_Request("SetAlbumTag", "UpdateTagInput", {albumid:this.musicid, tagid:tagid});
                break;
            default:
                window.console && console.log("Invalid music type: " + this.musictype);
        }
    }
    onRemove(tagid)
    {
        switch(this.musictype)
        {
            case "audio":
                MusicDB_Request("RemoveSongTag",  "UpdateTagInput", {songid:this.musicid,  tagid:tagid});
                break;
            case "video":
                MusicDB_Request("RemoveVideoTag", "UpdateTagInput", {videoid:this.musicid, tagid:tagid});
                break;
            case "album":
                MusicDB_Request("RemoveAlbumTag", "UpdateTagInput", {albumid:this.musicid, tagid:tagid});
                break;
            default:
                window.console && console.log("Invalid music type: " + this.musictype);
        }
    }
}



class TagListEdit
{
    // tagtype: "genre", "subgenre"
    constructor(tagtype)
    {
        this.tagtype    = tagtype;

        this.infoicon   = new SVGIcon("Tags");
        this.tagview    = new TagListView(true); // Show remove button on all tags
        this.taginput   = document.createElement("input");
        this.taginput.type    = "string";
        this.taginput.oninput = ()=>{this.Find(this.taginput.value);};
        this.tagselect  = new TagSelection(tagtype);
        this.listbutton = new SVGButton("DropDown", ()=>{this.tagselect.ToggleSelectionList();});
        this.listbutton.SetTooltip("Show available tags");
        if(this.tagtype == "genre")
        {
            this.createbutton = new SVGButton("Add", ()=>{this.CreateTag();});
            this.createbutton.SetTooltip("Create new tag");
            this.createbutton.Hide();
        }

        this.element    = document.createElement("div");
        this.element.classList.add("tagedit");
        this.element.classList.add("flex-row");
        this.element.classList.add("smallfont");
        this.element.classList.add("hlcolor");

        this.element.appendChild(this.infoicon.GetHTMLElement());
        this.element.appendChild(this.tagview.GetHTMLElement());
        this.element.appendChild(this.taginput);
        if(this.tagtype == "genre")
        {
            this.element.appendChild(this.createbutton.GetHTMLElement());
        }
        this.element.appendChild(this.listbutton.GetHTMLElement());
        this.element.appendChild(this.tagselect.GetHTMLElement());
    }



    GetHTMLElement()
    {
        return this.element;
    }



    // MDBTags: All tags including .genres and .subgenres
    Update(musictype, musicid, MDBTags)
    {
        if(this.tagtype == "genre")
            this.tagview.Update(musictype, musicid, MDBTags.genres);
        else if(this.tagtype == "subgenre")
            this.tagview.Update(musictype, musicid, MDBTags.subgenres);

        this.tagselect.Update(musictype, musicid, MDBTags);
        this.tagselect.Hide();

        if(this.tagtype == "genre")
            this.createbutton.Hide();
        return;
    }



    Find(string)
    {
        let result = this.tagselect.Find(string);

        if(result.length === 1)
        {
            result[0].tagobject.onClick(); // == Add Tag
            this.taginput.value = "";
            this.tagselect.Hide();
            this.createbutton.Hide();
        }
        else
        {
            this.tagselect.Show();
            this.createbutton.Show();
        }
    }



    CreateTag()
    {
        // Create Tag
        let tagname = this.taginput.value;
        MusicDB_Request("AddGenre", "NewGenre", {name: tagname});
        // Clean user interface
        this.taginput.value = "";
        this.tagselect.Hide();
        this.createbutton.Hide();

        // Show info that tag was creates (allow undo)
    }
}



class TagSelection
{
    // tagtype: "genre", "subgenre"
    constructor(tagtype)
    {
        this.tagtype    = tagtype;
        this.musictype  = null;
        this.musicid    = null;

        this.listbox    = document.createElement("div");
        this.listbox.classList.add("tagselect");
        this.listbox.classList.add("smallfont");
        this.listbox.classList.add("hlcolor");
        this.listbox.classList.add("frame");
        this.listbox.style.display = "none";
    }



    GetHTMLElement()
    {
        return this.listbox;
    }



    ToggleSelectionList()
    {
        if(this.listbox.style.display == "none")
        {
            this.Show();
        }
        else
        {
            this.Hide();
        }
    }

    Show()
    {
        this.listbox.style.display = "flex";
    }
    Hide()
    {
        this.listbox.style.display = "none";
    }


    // exclude: MDBTag array with tags that shall not appear in the list
    _CreateGenreList(exclude)
    {
        // Create array of Valid Genres
        let taglist = new Array();
        let genres  = tagmanager.GetGenres();

        for(let genre of genres)
        {
            // Check if genre is listed in the exclude-array
            if(exclude.some((element)=>{return element.id === genre.id;}))
                continue;

            taglist.push(genre);
        }

        // Create HTML element from array
        let genrelist = document.createElement("div");
        genrelist.classList.add("flex-row");
        this.tagmap = new Array();  // Keep a list of possible tags for searching
        for(let tag of taglist)
        {
            let item = new Tag(tag);
            item.SetAddAction((tagid)=>{this.onTagSelect(tagid)});
            genrelist.appendChild(item.GetHTMLElement());
            this.tagmap.push({tag: item, genre: tag});
        }

        return genrelist;
    }



    // genres: main genres that are set
    // exclude: MDBTag array with tags that shall not appear in the list
    _CreateSubgenreList(genres, exclude)
    {
        let subgenres   = tagmanager.GetSubgenres();
        let genrematrix = document.createElement("div");
        genrematrix.classList.add("flex-column");

        // Get subgenres for each genre
        this.tagmap = new Array();  // Keep a list of possible tags for searching
        for(let genre of genres)
        {
            let subgenrelist = document.createElement("div");
            subgenrelist.classList.add("flex-row");

            let title        = document.createElement("span");
            title.classList.add("flex-row");
            title.classList.add("fgcolor");
            title.innerText  = genre.name;

            for(let subgenre of subgenres)
            {
                if(subgenre.parentid != genre.id)
                    continue
                if(exclude.some((element)=>{return element.id === subgenre.id;}))
                    continue;

                let item = new Tag(subgenre);
                item.SetAddAction((tagid)=>{this.onTagSelect(tagid)});
                subgenrelist.appendChild(item.GetHTMLElement());

                this.tagmap.push({tag: item, genre: subgenre});
            }
            
            // Do not add an empty list entry
            if(subgenrelist.childElementCount === 0)
                continue;

            genrematrix.appendChild(title);
            genrematrix.appendChild(subgenrelist);
        }
        return genrematrix;
    }



    Find(string)
    {
        let foundtags = new Array(); // return a list of MDBTags that match

        string = string.toLowerCase();
        for(let tag of this.tagmap)
        {
            let tagobject = tag.tag;
            let element   = tagobject.GetHTMLElement();
            let dbentry   = tag.genre;
            let tagname   = dbentry.name.toLowerCase();

            let similarity = Similarity(string, tagname);
            // 1st: Highlight all entries that are similar to the entered name
            //      Do not add these in the found array because similarity may not
            //      represent the users intention
            if(similarity > 0.5)
            {
                element.dataset.highlight = true;
            }
            else
            {
                element.dataset.highlight = false;
            }

            // 2nd: Add all exact matched
            if(string === tagname)
            {
                foundtags.push({tagobject: tagobject, mdbtag: dbentry});
            }
        }

        return foundtags;
    }



    onTagSelect(tagid)
    {
        switch(this.musictype)
        {
            case "audio":
                MusicDB_Request("SetSongTag",  "UpdateTagInput", {songid:this.musicid,  tagid:tagid});
                break;
            case "video":
                MusicDB_Request("SetVideoTag", "UpdateTagInput", {videoid:this.musicid, tagid:tagid});
                break;
            case "album":
                MusicDB_Request("SetAlbumTag", "UpdateTagInput", {albumid:this.musicid, tagid:tagid});
                break;
            default:
                window.console && console.log("Invalid music type: " + this.musictype);
        }

        //this.Hide(); // Hide list after selection
    }



    // MDBTags: All tags including .genres and .subgenres
    Update(musictype, musicid, MDBTags)
    {
        this.musictype = musictype;
        this.musicid   = musicid;

        let listelement;
        if(this.tagtype == "genre")
        {
            listelement = this._CreateGenreList(MDBTags.genres);
        }
        else if(this.tagtype == "subgenre")
        {
            listelement = this._CreateSubgenreList(MDBTags.genres, MDBTags.subgenres);
        }

        this.listbox.innerHTML = "";
        this.listbox.appendChild(listelement);    

    }
}




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

