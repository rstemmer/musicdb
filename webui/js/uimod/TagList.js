// MusicDB,  a music manager with web-bases UI that focus on music.
// Copyright (C) 2017-2021  Ralf Stemmer <ralf.stemmer@gmx.net>
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
        this.element.onclick      = ()=>{this.onClick();};
        this.element.onmouseenter = ()=>{this.onMouseEnter();};
        this.element.onmouseleave = ()=>{this.onMouseLeave();};
    }



    SetConfidence(confidence)
    {
        let percent  = Math.round(confidence * 100)
        let ratiobar = new RatioBar(percent, `Confidence: ${percent} %`); // U+202F (NARROW NO-BREAK SPACE)
        this.element.appendChild(ratiobar.GetHTMLElement());
    }



    SetClickAction(onclick)
    {
        this.onclick = onclick;
    }
    SetMouseEnterAction(onmouseenter)
    {
        this.onmouseenter = onmouseenter;
    }
    SetMouseLeaveAction(onmouseleave)
    {
        this.onmouseleave = onmouseleave;
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

    onMouseEnter()
    {
        event.stopPropagation();

        if(typeof this.onmouseenter === "function")
            this.onmouseenter(this.tagid);
    }
    onMouseLeave()
    {
        event.stopPropagation();

        if(typeof this.onmouseleave  === "function")
            this.onmouseleave(this.tagid);
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



    AddGhostTag(tag)
    {
        let tagelement = tag.GetHTMLElement();
        tagelement.classList.add("ghost");
        this.element.appendChild(tagelement);
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



    GetTagList()
    {
        return this.taglist;
    }



    onApprove(tagid)
    {
        switch(this.musictype)
        {
            case "audio":
                MusicDB_Request("SetSongTag",  "UpdateTags", {songid:this.musicid,  tagid:tagid});
                break;
            case "video":
                MusicDB_Request("SetVideoTag", "UpdateTags", {videoid:this.musicid, tagid:tagid});
                break;
            case "album":
                MusicDB_Request("SetAlbumTag", "UpdateTags", {albumid:this.musicid, tagid:tagid});
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
                MusicDB_Request("RemoveSongTag",  "UpdateTags", {songid:this.musicid,  tagid:tagid});
                break;
            case "video":
                MusicDB_Request("RemoveVideoTag", "UpdateTags", {videoid:this.musicid, tagid:tagid});
                break;
            case "album":
                MusicDB_Request("RemoveAlbumTag", "UpdateTags", {albumid:this.musicid, tagid:tagid});
                break;
            default:
                window.console && console.log("Invalid music type: " + this.musictype);
        }
    }
}





// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

