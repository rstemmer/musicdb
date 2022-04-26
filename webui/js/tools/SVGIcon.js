// MusicDB,  a music manager with web-bases UI that focus on music.
// Copyright (C) 2017 - 2022  Ralf Stemmer <ralf.stemmer@gmx.net>
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
        let maskcss = `mask: ${maskurl}; -webkit-mask: ${maskurl}`;

        this.element.style.cssText = maskcss;
    }
}



class SVGButton extends SVGIcon
{
    constructor(name, onclick, tooltip=null)
    {
        super(name)
        this.onclick = onclick;
        this.Enable();
        if(typeof tooltip === "string")
            this.SetTooltip(tooltip);
    }

    Enable()
    {
        this.element.dataset.disabled = false;
        this.element.onclick = this.onclick;
    }
    Disable()
    {
        this.element.dataset.disabled = true;
        this.element.onclick = null;
    }
}



// The switch can have one of the two different states: "a" or "b"
class SVGSwitch extends SVGButton
{
    constructor(icona, iconb, onstatechange, initstate="a")
    {
        let iconname;
        if(initstate == "a")
            iconname = icona;
        else
            iconname = iconb;

        super(iconname, ()=>{this.onClick();});
        this.iconname_a = icona;
        this.iconname_b = iconb;
        this.state      = initstate;
        this.onclick    = onstatechange;
    }

    onClick()
    {
        if(this.state == "a")
            this.SetSelectionState("b");
        else
            this.SetSelectionState("a");

        if(typeof this.onclick === "function")
            this.onclick(this.state);
    }

    GetSelectionState()
    {
        return this.state;
    }
    SetSelectionState(state)
    {
        this.state = state;
        let iconname;
        if(this.state === "a")
            iconname = this.iconname_a;
        else
            iconname = this.iconname_b;
        this.SetIcon(iconname);
    }
}



class SVGCheckBox extends SVGSwitch
{
    constructor(oncheckstatechange, checked=false)
    {
        super("Checked", "Unchecked", ()=>{this.onStateChange();}, (checked)?"a":"b");
        this.oncheckstatechange = oncheckstatechange;
    }

    onStateChange()
    {
        if(typeof this.oncheckstatechange === "function")
            this.oncheckstatechange(this.GetSelectionState());
    }

    GetSelectionState()
    {
        return super.GetSelectionState() == "a";
    }
    SetSelectionState(state)
    {
        if(state === true)
            state = "a";
        else if(state === false)
            state = "b";
        super.SetSelectionState(state);
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

    SetColor(htmlcolor)
    {
        this.element.style.color = htmlcolor;
    }
}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

