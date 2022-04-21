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


class Tag extends Element
{
    constructor(MDBTag)
    {
        super("div", ["Tag", "frame", "smallfont", "flex-row"]);
        this.tagname        = MDBTag.name;
        this.tagid          = MDBTag.id;
        this.confidence     = MDBTag.confidence;
        this.approval       = MDBTag.approval;  // 0: Set by AI, >0: Set by User

        this.onclick        = null;
        this.onapprove      = null;
        this.onremove       = null;

        this.approvebutton  = new SVGButton("Approve", ()=>{this.onApprove()}, "Confirm this Tag");
        this.removebutton   = new SVGButton("Remove",  ()=>{this.onRemove()} , "Remove this Tag" );
        this.addbutton      = new SVGButton("Add",     ()=>{this.onClick()}  , "Add this Tag"    );
        this.nameelement    = document.createElement("div");
        this.nameelement.innerText = this.tagname;

        this.AppendChild(this.nameelement);
        this.element.onclick      = ()=>{this.onClick();};
        this.element.onmouseenter = ()=>{this.onMouseEnter();};
        this.element.onmouseleave = ()=>{this.onMouseLeave();};
    }



    SetConfidence(confidence)
    {
        let percent  = Math.round(confidence * 100)
        let ratiobar = new RatioBar(percent, `Confidence: ${percent} %`); // U+202F (NARROW NO-BREAK SPACE)
        this.AppendChild(ratiobar);
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
        this.AppendChild(this.addbutton);
    }
    SetRemoveAction(onremove)
    {
        this.onremove = onremove;
        this.AppendChild(this.removebutton);
    }
    SetApproveAction(onapprove)
    {
        this.onapprove = onapprove;
        this.AppendChild(this.approvebutton);
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



class TagListView extends Element
{
    // Optional allowremove - if true, remove button is always visible
    constructor(allowremove)
    {
        super("div", ["TagView", "flex-row", "smallfont", "hlcolor"]);
        this.allowremove= allowremove;
        this.taglist    = new Array();
        this.musictype  = null;
        this.musicid    = null;
    }



    AddGhostTag(tag)
    {
        let tagelement = tag.GetHTMLElement();
        tagelement.classList.add("ghost");
        this.AppendChild(tagelement);
    }



    // musictype: "audio" or "video" or "album"
    Update(musictype, musicid, MDBTagArray)
    {
        this.musicid            = musicid;
        this.musictype          = musictype;
        this.taglist            = new Array();
        this.RemoveChilds();

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
            this.AppendChild(tag);
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
                MusicDB.Request("SetSongTag",  "UpdateTags", {songid:this.musicid,  tagid:tagid});
                break;
            case "video":
                MusicDB.Request("SetVideoTag", "UpdateTags", {videoid:this.musicid, tagid:tagid});
                break;
            case "album":
                MusicDB.Request("SetAlbumTag", "UpdateTags", {albumid:this.musicid, tagid:tagid});
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
                MusicDB.Request("RemoveSongTag",  "UpdateTags", {songid:this.musicid,  tagid:tagid});
                break;
            case "video":
                MusicDB.Request("RemoveVideoTag", "UpdateTags", {videoid:this.musicid, tagid:tagid});
                break;
            case "album":
                MusicDB.Request("RemoveAlbumTag", "UpdateTags", {albumid:this.musicid, tagid:tagid});
                break;
            default:
                window.console && console.log("Invalid music type: " + this.musictype);
        }
    }
}





// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

