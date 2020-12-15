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
        this.element.onclick      = ()=>{this.onClick();};
        this.element.onmouseenter = ()=>{this.onMouseEnter();};
        this.element.onmouseleave = ()=>{this.onMouseLeave();};
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
        /*
        if(this.tagtype == "genre")
        {
            this.createbutton = new SVGButton("Add", ()=>{this.CreateTag();});
            this.createbutton.SetTooltip("Create new tag");
            this.createbutton.Hide();
        }
        */

        this.element    = document.createElement("div");
        this.element.classList.add("tagedit");
        this.element.classList.add("flex-row");
        this.element.classList.add("smallfont");
        this.element.classList.add("hlcolor");

        this.element.appendChild(this.infoicon.GetHTMLElement());
        this.element.appendChild(this.tagview.GetHTMLElement());
        this.element.appendChild(this.taginput);
        /*
        if(this.tagtype == "genre")
        {
            this.element.appendChild(this.createbutton.GetHTMLElement());
        }
        */
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

        /*
        if(this.tagtype == "genre")
            this.createbutton.Hide();
        */
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
            //this.createbutton.Hide();
        }
        else
        {
            this.tagselect.Show();
            //this.createbutton.Show();
        }
    }



    /*
    CreateTag()
    {
        // Create Tag
        let tagname = this.taginput.value;
        if(this.tagtype == "genre")
            MusicDB_Request("AddGenre", "NewGenre", {name: tagname});

        // Clean user interface
        this.taginput.value = "";
        this.tagselect.Hide();
        this.createbutton.Hide();
        return;
    }
    */
}



class TagSelection
{
    // tagtype: "genre", "subgenre"
    constructor(tagtype)
    {
        this.tagtype    = tagtype;
        this.musictype  = null;
        this.musicid    = null;
        this.mdbtags    = null;

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

        //this.Hide(); // Hide list after selection
    }



    // MDBTags: All tags including .genres and .subgenres
    // All parameters are optional. If not given, they are used from a previous call
    Update(musictype, musicid, MDBTags)
    {
        if(musictype !== undefined)
            this.musictype = musictype;
        if(musicid !== undefined)
            this.musicid   = musicid;
        if(MDBTags !== undefined)
            this.mdbtags   = MDBTags;

        let listelement;
        if(this.tagtype == "genre")
        {
            listelement = this._CreateGenreList(this.mdbtags.genres);
        }
        else if(this.tagtype == "subgenre")
        {
            listelement = this._CreateSubgenreList(this.mdbtags.genres, this.mdbtags.subgenres);
        }

        this.listbox.innerHTML = "";
        this.listbox.appendChild(listelement);    

    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

