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

class SVGIcon
{
    constructor(name)
    {
        let maskurl  = `url("img/icons/${name}.svg");`;

        this.icon    = document.createElement("div");
        this.icon.classList.add("SVGIcon");
        this.icon.style.cssText = "mask: "+maskurl;
    }

    GetHTMLElement()
    {
        return this.icon;
    }

    SetTooltip(tooltip)
    {
        this.icon.title = tooltip;
    }

    SetColor(htmlcolor)
    {
        this.icon.style.backgroundColor = htmlcolor;
    }

    Show()
    {
        this.icon.style.display = "block";
    }
    Hide()
    {
        this.icon.style.display = "none";
    }
}



class SVGButton extends SVGIcon
{
    constructor(name, onclick)
    {
        super(name)
        this.icon.onclick = onclick;
    }
}



class SVGToggleButton extends SVGIcon
{
    constructor(name, onclick)
    {
        super(name)
        this.onclick               = onclick;
        this.icon.dataset.selected = false;
        this.icon.onclick          = ()=>{this.onIconClick();};
    }

    onIconClick()
    {
        let oldstate = this.GetSelectionState();
        let newstate = ! oldstate;
        this.SetSelectionState(newstate);

        if(typeof this.onclick === "function")
            this.onclick(newstate);

        return;
    }


    GetSelectionState()
    {
        let state = this.icon.dataset.selected;
        return (state === "true");
    }
    SetSelectionState(state)
    {
        this.icon.dataset.selected = state;
    }
}



class UnicodeToggleButton extends SVGToggleButton
{
    constructor(character, onclick)
    {
        super("", onclick);

        // Destroy SVG icon
        this.icon.classList.remove("SVGIcon")
        this.icon.style.cssText = "";

        // Create Unicode icon
        this.icon.innerText     = character;
        this.icon.classList.add("unicodeicon");
    }
}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

