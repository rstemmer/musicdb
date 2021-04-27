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


class TagListEdit extends Element
{
    // tagtype: "genre", "subgenre"
    constructor(tagtype)
    {
        super("div", ["TagListEdit", "flex-row", "smallfont", "hlcolor"]);
        this.tagtype    = tagtype;

        this.infoicon   = new SVGIcon("Tags");
        this.tagview    = new TagListView(true); // Show remove button on all tags
        this.taginput   = document.createElement("input");
        this.taginput.type    = "string";
        this.taginput.oninput = ()=>{this.Find(this.taginput.value);};
        this.taginput.onkeyup = (event)=>{this.onKeyUp(event);};
        this.tagselect  = new TagSelection(tagtype);
        this.tagselect.SetSelectionEvent((tag)=>{this.onTagSelect(tag);});
        this.listbutton = new SVGButton("DropDown", ()=>{this.tagselect.ToggleSelectionList();});
        this.listbutton.SetTooltip("Show available tags");

        this.element.appendChild(this.infoicon.GetHTMLElement());
        this.element.appendChild(this.tagview.GetHTMLElement());
        this.element.appendChild(this.taginput);
        this.element.appendChild(this.listbutton.GetHTMLElement());
        this.element.appendChild(this.tagselect.GetHTMLElement());
    }



    onTagSelect(tag)
    {
        this.tagview.AddGhostTag(tag);
    }


    onKeyUp(event)
    {
        let keycode = event.which || event.keyCode;
        if(keycode == 13 /*ENTER*/ && this.taginput.value.length > 0)
        {
            // Get highlighted tags. If only one is highlighted, select it.
            let highlighted = this.tagselect.GetHighlightedTags();
            if(highlighted.length === 1)
            {
                highlighted[0].tagobject.onClick(); // == Add Tag
                this.taginput.value = "";
            }
        }
        else if(keycode == 27 /*ESC*/)
        {
            this.taginput.value = "";
            this.taginput.oninput();
        }
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
        return;
    }



    Find(string)
    {
        this.tagselect.Update();  // Update genre lists with latest tags
        let result = this.tagselect.Find(string);

        if(result.length === 1)
        {
            result[0].tagobject.onClick(); // == Add Tag
            this.taginput.value = "";
            this.tagselect.Hide();
        }
        else
        {
            this.tagselect.Show();
        }
    }



    SetFocus()
    {
        this.taginput.focus();
    }
}



class TagSelection extends Element
{
    // tagtype: "genre", "subgenre"
    constructor(tagtype)
    {
        super("div", ["TagSelect", "smallfont", "hlcolor", "frame"]);
        this.tagtype    = tagtype;
        this.musictype  = null;
        this.musicid    = null;
        this.mdbtags    = null;

        this.element.style.display = "none";
    }



    // the handler must be a function with the following parameter: Tag-object
    SetSelectionEvent(handler)
    {
        this.onselect = handler;
    }



    ToggleSelectionList()
    {
        if(this.element.style.display == "none")
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
        this.element.style.display = "flex";
    }
    Hide()
    {
        this.element.style.display = "none";
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
            item.SetAddAction((tagid)=>{this.onTagSelect(tagid, item);});
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
                item.SetAddAction((tagid)=>{this.onTagSelect(tagid, item);});
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



    // Get all tags that were highlighted by Find(…)
    GetHighlightedTags()
    {
        let foundtags = new Array(); // return a list of MDBTags that match
        for(let tag of this.tagmap)
        {
            let tagobject = tag.tag;
            let element   = tagobject.GetHTMLElement();
            let dbentry   = tag.genre;
            if(element.dataset.highlight === "true")
                foundtags.push({tagobject: tagobject, mdbtag: dbentry});
        }
        return foundtags;
    }



    onTagSelect(tagid, tag)
    {
        if(typeof this.onselect === "function")
            this.onselect(tag);

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

        this.element.innerHTML = "";
        this.element.appendChild(listelement);    

    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

