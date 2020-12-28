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

class SVGBase extends Element
{
    constructor()
    {
        super("div", ["SVGIcon"]);
    }
}



// Empty element with the exact size of an SVGIcon or SVGButton
//  as well as the exact same class SVGIcon.
class SVGSpacer extends SVGBase
{
    constructor()
    {
        super();
        this.element.style.visibility = "hidden";
    }
}



class SVGIcon extends SVGBase
{
    constructor(name)
    {
        super();
        this.SetIcon(name);
    }

    SetTooltip(tooltip)
    {
        this.element.title = tooltip;
    }

    SetColor(htmlcolor)
    {
        this.element.style.backgroundColor = htmlcolor;
    }

    SetIcon(name)
    {
        let maskurl = `url("img/icons/${name}.svg");`;
        this.element.style.cssText = "mask: "+maskurl;
    }

    Show()
    {
        this.element.style.display = "block";
    }
    Hide()
    {
        this.element.style.display = "none";
    }
}



class SVGButton extends SVGIcon
{
    constructor(name, onclick)
    {
        super(name)
        this.element.onclick = onclick;
    }
}



class SVGCheckBox extends SVGButton
{
    constructor(onstatechange, checked=false)
    {
        let iconname;
        if(checked === true)
            iconname = "Checked";
        else
            iconname = "Unchecked";

        super(iconname, ()=>{this.onClick();});
        this.checked = checked;
        this.onclick = onstatechange;
    }

    onClick()
    {
        this.SetSelectionState(!this.GetSelectionState());

        if(typeof this.onclick === "function")
            this.onclick(this.checked);
    }

    GetSelectionState()
    {
        return this.checked;
    }
    SetSelectionState(state)
    {
        this.checked = state;
        let iconname;
        if(this.checked === true)
            iconname = "Checked";
        else
            iconname = "Unchecked";
        this.SetIcon(iconname);
    }
}



class SVGToggleButton extends SVGIcon
{
    constructor(name, onclick)
    {
        super(name)
        this.onclick                  = onclick;
        this.element.dataset.selected = false;
        this.element.onclick          = ()=>{this.onIconClick();};
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
        let state = this.element.dataset.selected;
        return (state === "true");
    }
    SetSelectionState(state)
    {
        this.element.dataset.selected = state;
    }
}



class UnicodeToggleButton extends SVGToggleButton
{
    constructor(character, onclick)
    {
        super("", onclick);

        // Destroy SVG icon
        this.element.classList.remove("SVGIcon")
        this.element.style.cssText = "";

        // Create Unicode icon
        this.element.innerText     = character;
        this.element.classList.add("unicodeicon");
    }
}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

