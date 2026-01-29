// MusicDB,  a music manager with web-bases UI that focus on music.
// Copyright (C) 2017 - 2025  Ralf Stemmer <ralf.stemmer@gmx.net>
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

    // This method overloads Element::SetColor.
    // Instead of the foreground color, the background color gets changed.
    // This is needed because of the icon being a masked div element
    // so that the div elements background appears to be the icons foreground.
    SetColor(htmlcolor)
    {
        this.element.style.backgroundColor = htmlcolor;
    }

    SetIcon(name)
    {
        // Try to get the icon as data-URI
        let iconmanager = WebUI.GetManager("Icons");
        let icon = iconmanager.GetIcon(name);

        // Define where to get the icon from (cache or server)
        let maskurl;
        if(typeof icon === "string")
            maskurl = `url(${icon});`;
        else
            maskurl = `url("img/icons/${name}.svg");`;

        // Apply CSS
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
        this.SetData("enabled", true);
        this.SetClickEventCallback(this.onclick);
    }
    Disable()
    {
        this.SetData("enabled", false);
        this.SetClickEventCallback(null);
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



class SVGToggleButton extends SVGButton
{
    constructor(name, onclick)
    {
        super(name)
        this.onclick = onclick;
        this.SetSelectionState(false);
        this.SetClickEventCallback(()=>{this.onIconClick();});
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
        let state = this.GetData("selected");
        return (state === "true");
    }
    SetSelectionState(state)
    {
        this.SetData("selected", state);
    }
}



class UnicodeToggleButton extends SVGToggleButton
{
    constructor(character, onclick)
    {
        super("", onclick);

        // Destroy SVG icon
        this.RemoveCSSClass("SVGIcon");
        this.element.style.cssText = "";

        // Create Unicode icon
        this.SetInnerText(character);
        this.AddCSSClass("unicodeicon");
    }

    // Reset SetColor function to its default behavior.
    // I has been overloaded by the super class SVGIcon.
    SetColor(htmlcolor)
    {
        this.element.style.color = htmlcolor;
    }
}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

