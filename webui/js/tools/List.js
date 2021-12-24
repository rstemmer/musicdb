// MusicDB,  a music manager with web-bases UI that focus on music.
// Copyright (C) 2017 - 2021  Ralf Stemmer <ralf.stemmer@gmx.net>
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


class List extends Element
{
    constructor(headline=null, classes=[])
    {
        super("div", ["List", "flex", "flex-column", ...classes]);
        this.headline = new Element("div", ["listhead", "flex", "flex-center"]);
        this.listbody = new Element("div", ["listbody", "flex", "flex-column", "frame"]);
        this.entries  = null;
        this.selectable  = false;
        this.multiselect = false;

        if(typeof headline == "string")
            this.SetHeadline(headline);

        this.Clear();

        this.AppendChild(this.headline);
        this.AppendChild(this.listbody);
    }



    SetHeadline(headline)
    {
        this.headline.SetInnerText(headline);
    }



    Clear()
    {
        this.entries = new Array();
        this.listbody.RemoveChilds();
    }



    MakeSelectable(selectable=true, multiselect=false)
    {
        this.selectable  = selectable;
        this.multiselect = multiselect;
    }



    // entry: Element instance
    AddEntry(entry)
    {
        // When an entry gets selected, the list needs to know this.
        entry.onclickparentcallback = (entry)=>{this.onEntrySelect(entry);}
        this.entries.push(entry);
        this.listbody.AppendChild(entry);
    }



    RemoveEntry(entry)
    {
        let htmlelement = entry.GetHTMLElement();

        // Remove entry from the DOM
        htmlelement.remove();

        // Remove rows from the internal array
        let index = this.entries.indexOf(entry);
        if(index > -1)
            this.entries.splice(index, 1);

        return;
    }



    onEntrySelect(selectedentry)
    {
        if(this.selectable == false)
            return;

        // Remove selection state from all entries except the selected one
        for(let entry of this.entries)
        {
            if(entry == selectedentry)
                entry.ToggleSelection();
            else if(this.multiselect == false)
                entry.Select(false);
        }
    }



    // Returns an array of all selected entries. Empty array if no entry is selected
    GetSelectedEntries()
    {
        let entries = new Array();
        for(let entry of this.entries)
        {
            if(entry.GetSelectionState() == true)
                entries.push(entry);
        }
        return entries;
    }
}



class ListEntry extends Element
{
    constructor(onclick=null, classes=[], id=null)
    {
        super("div", ["ListEntry", "hoverframe", ...classes], id);
        this.onclickusercallback   = null;
        this.onclickparentcallback = null; // expects one parameter: this entry
        this.element.onclick       = ()=>{this.onClick();};

        this.SetClickEventCallback(onclick);
    }



    Select(select=true)
    {
        this.SetData("highlight", select);
    }
    GetSelectionState()
    {
        return this.GetData("highlight") == "true";
    }
    ToggleSelection()
    {
        this.Select(! this.GetSelectionState());
    }



    // No parameters and no return value handled
    SetClickEventCallback(onclick)
    {
        if(typeof onclick !== "function")
            return;
        this.onclickusercallback = onclick;
    }



    onClick()
    {
        // The parent may update the selection state
        if(typeof this.onclickparentcallback === "function")
            this.onclickparentcallback(this);
        if(typeof this.onclickusercallback === "function")
            this.onclickusercallback();
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

