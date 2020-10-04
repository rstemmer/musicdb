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

class TabSelect
{
    constructor()
    {
        this.tabs           = new Array();
        this.buttons        = new Array();
        this.showcallback   = new Array();  // Will be called when tag gets selected (after integrating into the DOM)

        this.element        = document.createElement("div");
        this.element.classList.add("flex-column");
        this.element.classList.add("tabbox");
        this.tabbar         = document.createElement("div");
        this.tabbar.classList.add("flex-row");
        this.tabbar.classList.add("hovpacity");
        this.tabbar.classList.add("tabbar");
        this.tabcontent     = document.createElement("div");
        this.tabcontent.classList.add("tabcontent");

        this.element.appendChild(this.tabbar);
        this.element.appendChild(this.tabcontent);
        return;
    }



    GetHTMLElement()
    {
        return this.element;
    }



    // icon: SVGIcon
    // text: plain text
    // content: HTML div element
    // select: optional boolean (when true, the it will be visible by default
    AddTab(icon, text, content, select)
    {
        let arraylength = this.tabs.push(content);
        let tabid       = arraylength - 1;

        let tabtext     = document.createElement("div");
        tabtext.innerText = text;

        let tabbutton   = document.createElement("div");
        tabbutton.classList.add("flex-row");
        tabbutton.classList.add("smallfont");
        tabbutton.classList.add("hlcolor");
        tabbutton.classList.add("tabbutton");
        tabbutton.appendChild(icon.GetHTMLElement());
        tabbutton.appendChild(tabtext);
        tabbutton.onclick = (event)=>{this.SelectTab(tabid);};

        tabbutton.dataset.selected = false;
        this.buttons.push(tabbutton);
        this.showcallback.push(null);
        this.tabbar.appendChild(tabbutton);

        if(select === true)
            this.SelectTab(tabid);
        return tabid;
    }


    SetOnShowCallback(tabid, callback)
    {
        this.showcallback[tabid] = callback;
    }


    SelectTab(tabid)
    {
        this.tabcontent.innerHTML = "";
        this.tabcontent.appendChild(this.tabs[tabid]);

        for(let button of this.buttons)
        {
            button.dataset.selected = false;
        }
        this.buttons[tabid].dataset.selected = true;

        if(typeof this.showcallback[tabid] === "function")
            this.showcallback[tabid]();
        return;
    }

}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

