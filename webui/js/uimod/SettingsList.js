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


class SettingsList extends Element
{
    constructor()
    {
        super("div", ["SettingsList", "flex-columns"]);
        this.settingslist = new Array();
    }



    // entry: SettingsEntry object
    AddEntry(entry)
    {
        this.element.appendChild(entry.GetHTMLElement());
    }
}



class SettingsEntry extends Element
{
    // name: text string
    // infos: HTML string (multiple lines allowed)
    // icon: SVGIcon, SVGButton, …
    constructor(name, infos, icon)
    {
        super("div", ["SettingsEntry", "flex-row", "hoverframe"]);

        this.description = document.createElement("div");
        this.description.classList.add("flew-column");
        this.control = document.createElement("div");
        this.control.classList.add("flew-row");

        let textbox = document.createElement("div");
        let infobox = document.createElement("div");
        infobox.classList.add("smallfont");
        infobox.classList.add("hlcolor");

        textbox.innerText = name;
        infobox.innerHTML = infos;

        this.description.appendChild(textbox);
        this.description.appendChild(infobox);
        this.control.appendChild(icon.GetHTMLElement());

        this.element.appendChild(this.control);
        this.element.appendChild(this.description);

        this.Enable();
    }



    Disable()
    {
        this.element.dataset.enabled = false;
        this.enabled                 = false;
        return;
    }

    Enable()
    {
        this.element.dataset.enabled = true;
        this.enabled                 = true;
        return;
    }
}



class SettingsCheckbox extends SettingsEntry
{
    constructor(name, infos, onclick=null)
    {
        let iconchecked   = new SVGIcon("Checked");
        let iconunchecked = new SVGIcon("Unchecked");
        super(name, infos, iconchecked);

        this.iconchecked   = iconchecked;
        this.iconunchecked = iconunchecked;
        this.ischecked     = true;
        this.clickhandler  = onclick;
        this.element.onclick = ()=>{this.onClick()};
    }



    GetState()
    {
        return this.ischecked;
    }

    SetState(checked)
    {
        this.ischecked = checked;
        this.control.innerHTML = "";

        if(this.ischecked)
            this.control.appendChild(this.iconchecked.GetHTMLElement());
        else
            this.control.appendChild(this.iconunchecked.GetHTMLElement());
        return;
    }



    SetHandler(onclick)
    {
        this.clickhandler = onclick;
    }



    onClick()
    {
        if(this.enabled === false)
            return;

        this.SetState(! this.GetState());
        if(typeof this.clickhandler === "function")
            this.clickhandler(this.GetState());
    }
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

