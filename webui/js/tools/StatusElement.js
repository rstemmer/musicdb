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


class StatusElementBase extends Element
{
    // type: "li", "div"
    // classes: CSS classes list
    constructor(type, classes, text=null, state=null)
    {
        super(type, ["StatusElement", ...classes]);
        if(typeof text === "string")
            this.SetText(text);
        if(typeof state === "string")
            this.SetState(state);
    }


    // state: unknown, good, bad, active, open
    SetState(state)
    {
        this.element.dataset.state = state;
        if(typeof text === "string")
            this.SetText(text);
    }



    SetStatus(state, text=null)
    {
        this.SetState(state);
        if(typeof text === "string")
            this.SetText(text);
    }



    SetText(text)
    {
        this.element.innerText = text;
    }
}



class StatusText extends StatusElementBase
{
    constructor(text=null, state=null)
    {
        super("span", ["flex-row"], text, state);
    }
}



class UploadStatusText extends StatusText
{
    constructor(uploadstatus="")
    {
        switch(uploadstatus)
        {
            case "waitforchunk"     : super("Uploading …",              "active");
            case "uploadcomplete"   : super("Upload Succeeded",         "good");
            case "uploadfailed"     : super("Upload Failed",            "bad");
            case "notexisting"      : super("Internal Chaos",           "bad");
            case "preprocessed"     : super("Upload Succeeded",         "good");
            case "invalidcontent"   : super("Invalid Content",          "bad");
            case "integrated"       : super("Integration Succeeded",    "good");
            case "integrationfailed": super("Integration Failed",       "bad");
            case "startimport"      : super("Importing …",              "active");
            case "importfailed"     : super("Import Failed",            "bad");
            case "importartwork"    : super("Importing …",              "active");
            case "importcomplete"   : super("Import Succeeded",         "good");
            case "remove"           : super("Removing Upload",          "active");
            default                 : super("No upload processing",     "open");
        }
    }
}



class StatusItem extends StatusElementBase
{
    constructor(text, state=null)
    {
        super("li", ["flex-row"], text, state);
    }



    Show()
    {
        this.element.style.display = "list-item";
    }
    Hide()
    {
        this.element.style.display = "none";
    }
}



class StatusList extends Element
{
    constructor()
    {
        super("ul", ["StatusList", "flex-column"]);
        this.states = new Object();
    }



    AddState(statename, statelabel)
    {
        let item = new StatusItem(statelabel, "unknown");
        this.states[statename] = item;
        this.element.appendChild(item.GetHTMLElement());
        return;
    }



    SetState(statename, state)
    {
        this.states[statename].SetState(state);
    }
}
// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

