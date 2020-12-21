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



class MainMenu
{
    constructor(topoffset, rightoffset, curtain=null)
    {
        this.icon        = new SVGIcon("Menu");
        this.entryarray  = new Array(); // For regular menu entries
        this.sectionarray= new Array(); // For additional sections added as div-elements
        
        this.topoffset   = topoffset;
        this.rightoffset = rightoffset;

        this.menubutton  = this._CreateMenuToggleButton(this.icon);

        this.curtain     = curtain;
        if(this.curtain)
            this.curtain.AddClickEvent(()=>{this.HideMenu();});

        this.entrylistelement = document.createElement("div");
        this.entrylistelement.classList.add("menuentrylist");
        this.entrylistelement.style.display = "none"; // Hide by default
        this.isopen      = false;

        this.element     = document.createElement("div");
        this.element.classList.add("menu");
        this.element.style.top      = this.topoffset;
        this.element.style.right    = this.rightoffset;
        this.element.appendChild(this.menubutton);
        this.element.appendChild(this.entrylistelement);
    }

    GetHTMLElement()
    {
        return this.element;
    }



    _CreateMenuToggleButton(icon)
    {
        let button = document.createElement("div");

        button.appendChild(icon.GetHTMLElement());
        button.classList.add("hovpacity");
        button.classList.add("menutogglebutton");
        button.title = "Show main menu";

        button.onclick = ()=>
            {
                this.ToggleMenu();
            };
        return button;
    }



    UpdateMenuEntryList()
    {
        this.entrylistelement.innerHTML = "";

        for(let entry of this.entryarray)
        {
            this.entrylistelement.appendChild(entry.element);
        }
        for(let section of this.sectionarray)
        {
            this.entrylistelement.appendChild(section.element);
        }

        return;
    }


    CreateButton(icon, text, onclick, tooltip=null)
    {
        let entry = new Object();

        entry.icon              = icon.GetHTMLElement();
        entry.text              = document.createElement("span");
        entry.text.textContent  = text;
        entry.onclick           = onclick;
        entry.element           = document.createElement("div");
        entry.element.classList.add("menuentry");
        entry.element.appendChild(entry.icon);
        entry.element.appendChild(entry.text);

        if(tooltip !== null)
            entry.element.title = tooltip;

        entry.element.onclick = (event)=>
            {
                entry.onclick();
                this.ToggleMenu(); // Hide menu after menu item clicked
                return;
            }

        let newlength = this.entryarray.push(entry);
        let entryid   = newlength - 1;
        return entryid;
    }


    CreateSwitch(aicon, atext, afunction, bicon, btext, bfunction, tooltip=null)
    {
        let entry = new Object();

        entry.aicon = aicon.GetHTMLElement();
        entry.bicon = bicon.GetHTMLElement();

        entry.atext             = document.createElement("span");
        entry.atext.textContent = atext;
        entry.btext             = document.createElement("span");
        entry.btext.textContent = btext;

        entry.afunction = afunction;
        entry.bfunction = bfunction;

        entry.switchstate = "a";

        entry.element = document.createElement("div");
        entry.element.classList.add("menuentry");
        entry.element.appendChild(entry.aicon);
        entry.element.appendChild(entry.atext);

        if(tooltip !== null)
            entry.element.title = tooltip;

        entry.element.onclick = (event)=>
            {
                if(entry.switchstate == "a")
                {
                    entry.afunction();
                    entry.switchstate = "b";
                    entry.element.innerHTML = "";
                    entry.element.appendChild(entry.bicon);
                    entry.element.appendChild(entry.btext);
                }
                else
                {
                    entry.bfunction();
                    entry.switchstate = "a";
                    entry.element.innerHTML = "";
                    entry.element.appendChild(entry.aicon);
                    entry.element.appendChild(entry.atext);
                }

                this.ToggleMenu(); // Hide menu after menu item clicked
                return;
            }

        let newlength = this.entryarray.push(entry);
        let entryid   = newlength - 1;
        return entryid;
    }


    CreateSection(sectionname, sectionelement)
    {
        sectionelement.classList.add("sectionbody");

        let sectiontitle        = document.createElement("div");
        sectiontitle.innerText  = sectionname;
        sectiontitle.classList.add("sectiontitle");
        sectiontitle.classList.add("hlcolor");

        let section             = new Object();
        section.element         = document.createElement("div");
        section.element.classList.add("section");
        section.element.appendChild(sectiontitle);
        section.element.appendChild(sectionelement);

        this.sectionarray.push(section);
        return;
    }


    ForceEntryState(entryid, state)
    {
        if(state == "a")
        {
            this.entryarray[entryid].switchstate = "a";
            this.entryarray[entryid].element.innerHTML = "";
            this.entryarray[entryid].element.appendChild(this.entryarray[entryid].aicon);
            this.entryarray[entryid].element.appendChild(this.entryarray[entryid].atext);
        }
        else if(state == "b")
        {
            this.entryarray[entryid].switchstate = "b";
            this.entryarray[entryid].element.innerHTML = "";
            this.entryarray[entryid].element.appendChild(this.entryarray[entryid].bicon);
            this.entryarray[entryid].element.appendChild(this.entryarray[entryid].btext);
        }

        this.UpdateMenuEntryList();
    }



    HideMenu()
    {
        if(this.curtain)
            this.curtain.Hide();

        this.entrylistelement.style.display = "none";
        this.isopen = false;
    }

    ShowMenu()
    {
        if(this.curtain)
            this.curtain.Show();

        this.entrylistelement.style.display = "flex";
        this.isopen = true;
    }

    ToggleMenu()
    {
        if(this.isopen)
        {
            this.HideMenu();
        }
        else
        {
            this.ShowMenu();
        }
    }

}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

