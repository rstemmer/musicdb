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



class GenreListEditor extends Element
{
    // headliner: string
    // selecthandler: when an entry gets selected - parameter is the selected MDBTag
    //                When selecthandler returns a boolean true, then the selected entry gets highlighted
    //                A boolean false un-highlights all entries. All other return values will be ignored
    // addhandler: function called when new tag shall be added - parameter is an object describing the tag
    // handler can be null
    constructor(headline, selecthandler, addhandler)
    {
        super("div", ["GenreListEditor", "flex-column"]);

        this.addhandler    = addhandler;
        this.selecthandler = selecthandler;

        this.headelement  = document.createElement("span");
        this.headelement.classList.add("flex-center");
        this.headelement.innerText = headline;

        this.listelement  = document.createElement("div");
        this.listelement.classList.add("listelement");
        this.listelement.classList.add("flex-column");
        this.listelement.classList.add("flex-grow");
        this.listelement.classList.add("frame");

        this.inputbar     = document.createElement("div");
        this.inputbar.classList.add("inputbar");
        this.inputbar.classList.add("flex-row");

        this.inputelement = document.createElement("input");
        this.inputelement.classList.add("flex-grow");
        this.addbutton    = new SVGButton("Add", ()=>{this.onAdd();});

        this.inputbar.appendChild(this.inputelement);
        this.inputbar.appendChild(this.addbutton.GetHTMLElement());

        this.element.appendChild(this.headelement);
        this.element.appendChild(this.listelement);
        this.element.appendChild(this.inputbar);

        this.list = new Array();
    }



    onSelect(MDBTag)
    {
        if(typeof this.selecthandler != "function")
            return;

        let highlight = this.selecthandler(MDBTag);
        if(typeof highlight !== "boolean")
            return;

        for(let entry of this.list)
        {
            entry.element.dataset.highlight = false;
            if(highlight === true)
            {
                if(entry.tag == MDBTag)
                    entry.element.dataset.highlight = true;
            }
        }
    }



    onAdd()
    {
        if(typeof this.addhandler != "function")
            return;

        // TODO: Create tag
        let tag;

        this.addhandler(tag);
    }



    onRemove(MDBTag)
    {
        // TODO: Remove Tag
    }



    // MDBTags is allowed to be [] -> List will be emptied
    // MDBTagsStats is allowed to be {} -> No stats will be shown
    UpdateList(MDBTags, MDBTagsStats)
    {
        this.listelement.innerHTML = "";
        this.list = new Array();

        if(typeof MDBTagsStats !== "object")
            MDBTagsStats = {};  // Get a defined state for MDBTagsStats

        if(MDBTags === [])
            return;

        for(let MDBTag of MDBTags)
        {
            let tagid       = MDBTag.id;
            let numsongs    = null;
            let numalbums   = null;
            let numvideos   = null;
            let numchildren = null;
            let stats       = MDBTagsStats[tagid]
            if(typeof stats === "object")
            {
                numsongs    = stats["songs"];
                numalbums   = stats["albums"];
                numvideos   = stats["videos"];
                numchildren = stats["children"];
            }
            this.AddEntry(MDBTag, numsongs, numalbums, numvideos, numchildren);
        }

        return;
    }



    AddEntry(MDBTag, numsongs, numalbums, numvideos, numchildren=null)
    {
        let element = document.createElement("div");
        element.classList.add("listentry");
        element.classList.add("flex-row");
        element.classList.add("hoverframe");
        element.onclick = ()=>{this.onSelect(MDBTag);};

        let name = document.createElement("span");
        name.innerText = MDBTag.name;

        let removebutton = new SVGButton("Remove", ()=>{this.onRemove(MDBTag);});

        let infos = document.createElement("div");
        infos.classList.add("taginfos");
        infos.classList.add("flex-row");
        infos.classList.add("smallfont");
        infos.classList.add("hlcolor");

        let infotext = "";
        if(typeof numsongs    === "number" && numsongs    > 0) infotext += `<span>${numsongs   } Songs</span>`;
        if(typeof numalbums   === "number" && numalbums   > 0) infotext += `<span>${numalbums  } Albums</span>`;
        if(typeof numvideos   === "number" && numvideos   > 0) infotext += `<span>${numvideos  } Videos</span>`;
        if(typeof numchildren === "number" && numchildren > 0) infotext += `<span>${numchildren} Sub-Genres</span>`;
        if(infotext == "") infotext = "<span>This tag is not used yet</span>"
        infos.innerHTML = infotext;

        // When there are dependencies, make the remove-button a bit less opaque
        if(numsongs + numalbums + numvideos + numchildren > 0)
        {
            removebutton.SetColor("var(--color-red)");
            removebutton.GetHTMLElement().classList.add("hovpacity");
        }

        element.appendChild(name);
        element.appendChild(removebutton.GetHTMLElement());
        element.appendChild(infos);
        this.listelement.appendChild(element);

        let entry = new Object();
        entry.element   = element;
        entry.tag       = MDBTag;
        entry.numsongs  = numsongs;
        entry.numalbums = numalbums;
        entry.numvideos = numvideos;
        entry.numvideos = numchildren;
        this.list.push(entry);
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

