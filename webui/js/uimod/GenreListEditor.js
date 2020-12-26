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
    // removehandler: function called when tag shall be removed - parameter is an object describing the tag
    // handler can be null
    constructor(headline, selecthandler, addhandler, removehandler, renamehandler)
    {
        super("div", ["GenreListEditor", "flex-column"]);

        this.addhandler    = addhandler;
        this.removehandler = removehandler;
        this.renamehandler = renamehandler;
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
        this.inputelement.oninput = ()=>{this.onInput()};
        this.inputelement.onkeyup = (event)=>{this.onKeyUp(event)};
        this.addbutton    = new SVGButton("Add", ()=>{this.onAdd();});

        this.inputbar.appendChild(this.inputelement);
        this.inputbar.appendChild(this.addbutton.GetHTMLElement());

        this.msg_info   = new MessageBarInfo();
        this.msg_added  = new MessageBarConfirm();
        this.msg_double = new MessageBarError();

        this.element.appendChild(this.headelement);
        this.element.appendChild(this.listelement);
        this.element.appendChild(this.msg_info.GetHTMLElement());
        this.element.appendChild(this.msg_added.GetHTMLElement());
        this.element.appendChild(this.msg_double.GetHTMLElement());
        this.element.appendChild(this.inputbar);

        this.list = new Array();
    }



    // This method can be handy when there are external conditions to fulfill until the input element can be used
    ForceInputElementState(enabled, infomessage=null)
    {
        this.inputelement.disabled = !enabled;

        if(enabled == false)
        {
            this.inputelement.dataset.valid =  enabled;
            this.inputelement.value         = "";
        }

        if(typeof infomessage === "string")
        {
            this.msg_info.UpdateMessage(infomessage);
            this.msg_info.Show();
        }
        else
        {
            this.msg_info.Hide();
        }
        return;
    }



    UpdateHeadline(headlinetext)
    {
        this.headelement.innerText = headlinetext;
    }



    onInput()
    {
        let tagname = this.inputelement.value;

        // Is there a name?
        if(tagname.length == 0)
        {
            this.inputelement.dataset.valid = "";
            return;
        }

        // Check if name already exists
        for(let entry of this.list)
        {
            if(entry.tag.name == tagname)
            {
                this.msg_double.UpdateMessage(`Tag "${tagname}" already exists!`);
                this.msg_double.Show();
                this.inputelement.dataset.valid = false;
                return;
            }
        }
        this.msg_double.Hide();

        // Seems to be Valid
        this.inputelement.dataset.valid = true;
        return;
    }



    onKeyUp(event)
    {
        let keycode = event.which || event.keyCode;

        if(keycode == 13 /*ENTER*/)
        {
            this.onAdd();
        }
        return;
    }



    // TODO: Something like a dedicated "EditableElement" would be useful
    // Double click on the tags name -> start renaming-mode
    onStartRenaming(element, MDBTag)
    {
        if(typeof this.renamehandler !== "function")
            return;

        let inputelement = document.createElement("input");
        inputelement.value   = MDBTag.name;
        inputelement.onkeyup = (event)=>
            {
                let keycode = event.which || event.keyCode;

                if(keycode != 13 && keycode != 27)
                    return;

                let name = document.createElement("span");
                name.ondblclick = ()=>{this.onStartRenaming(name, MDBTag);}

                if(keycode == 13 /*ENTER*/)
                {
                    if(typeof this.renamehandler === "function")
                        this.renamehandler(MDBTag.id, event.target.value);
                    name.innerText = event.target.value;
                }
                else if(keycode == 27 /*ESC*/)
                {
                    name.innerText = MDBTag.name;
                }

                event.target.replaceWith(name);
                event.preventDefault();
                return;

            }
        element.replaceWith(inputelement);
        return;
    }



    // When highlight is false, nothing gets selected, otherwise the MDBTag
    ForceSelection(MDBTag, highlight=true)
    {
        if(typeof MDBTag !== "object")
            return;

        for(let entry of this.list)
        {
            if(highlight === true && entry.tag.id == MDBTag.id)
                entry.element.dataset.highlight = true;
            else
                entry.element.dataset.highlight = false;
        }
        return;
    }



    onSelect(MDBTag)
    {
        if(typeof this.selecthandler !== "function")
            return;

        let highlight = this.selecthandler(MDBTag);
        if(typeof highlight !== "boolean")
            return;

        this.ForceSelection(MDBTag, highlight);
    }



    onAdd()
    {
        if(typeof this.addhandler != "function")
            return;

        if(this.inputelement.dataset.valid != "true") // could be undefined
            return;

        // Add Tag
        let tagname = this.inputelement.value;
        this.addhandler(tagname);

        // Clear input after adding tag
        this.inputelement.dataset.valid = "";
        this.inputelement.value         = "";

        // Show info that tag was added
        this.msg_added.UpdateMessage(`Tag "${tagname}" added.`);
        this.msg_added.Show();
    }



    onRemove(MDBTag, numdependencies)
    {
        event.stopPropagation();

        if(typeof this.removehandler != "function")
            return;

        if(numdependencies > 0)
        {
            // Ask for confirmation
            //return;
        }

        // Remove Tag
        let tagid = MDBTag.id;
        this.removehandler(tagid);
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
        name.innerText  = MDBTag.name;
        name.ondblclick = ()=>{this.onStartRenaming(name, MDBTag);}

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

        let numdependencies = numsongs + numalbums + numvideos + numchildren;
        let removebutton    = new SVGButton("Remove", ()=>{this.onRemove(MDBTag, numdependencies);});

        // When there are dependencies, make the remove-button a bit less opaque
        if(numdependencies > 0)
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

