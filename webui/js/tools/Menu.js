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

class MenuButton extends SVGButton
{
    constructor(offset_top, offset_right, iconname, onclick, tooltip)
    {
        super(iconname, onclick, tooltip);
        this.AddCSSClass("MenuButton");
        this.AddCSSClass("hovpacity");

        this.element.style.top   = offset_top;
        this.element.style.right = offset_right;
    }
}



class MenuEntry extends Element
{
    constructor()
    {
        super("div", ["MenuEntry", "flex-row", "hoverframe"]);
    }


    Update(icon, label, onclick, tooltip)
    {
        let labelelement = new Element("label");
        labelelement.SetInnerText(label);

        this.RemoveChilds();
        this.element.onclick = onclick;
        this.SetTooltip(tooltip);
        this.AppendChild(icon);
        this.AppendChild(labelelement);
    }
}


class MenuEntryButton extends MenuEntry
{
    constructor(icon, label, onclick, tooltip)
    {
        super();
        this.Update(icon, label, onclick, tooltip)
    }
}

class MenuEntrySwitch extends MenuEntry
{
    constructor(icona, labela, onclicka, tooltipa,
                iconb, labelb, onclickb, tooltipb)
    {
        super();
        this.icona    = icona;
        this.labela   = labela;
        this.onclicka = onclicka;
        this.tooltipa = tooltipa;
        this.iconb    = iconb;
        this.labelb   = labelb;
        this.onclickb = onclickb;
        this.tooltipb = tooltipb;
        this.SwitchToA();
    }


    onClick()
    {
        if(this.switchstate === "a")
            this.onclicka();
        else
            this.onclickb();
        this.Toggle();
    }


    SwitchToA()
    {
        this.Update(this.icona, this.labela, ()=>{this.onClick();}, this.tooltipa)
        this.switchstate = "a";
    }
    SwitchToB()
    {
        this.Update(this.iconb, this.labelb, ()=>{this.onClick();}, this.tooltipb)
        this.switchstate = "b";
    }
    Toggle()
    {
        if(this.switchstate === "a")
            this.SwitchToB();
        else
            this.SwitchToA();
    }
}



class Menu extends Element
{
    constructor(classes=[], elementid=null)
    {
        super("div", ["Menu", "flex-column", ...classes], elementid);
        this.entries = new Object();
        this.HideMenu();
    }



    HideMenu()
    {
        this.Hide();
        this.isopen = false;
    }

    ShowMenu()
    {
        this.Show();
        this.isopen = true;
    }

    ToggleMenu()
    {
        if(this.isopen)
            this.HideMenu();
        else
            this.ShowMenu();
    }



    AddButton(name, icon, label, onclick, tooltip)
    {
        let entry = new MenuEntryButton(icon, label, ()=>{onclick(); this.ToggleMenu();}, tooltip);
        this.entries[name] = entry;
        this.AppendChild(entry);
        return
    }



    AddSwitch(name, icona, labela, onclicka, tooltipa,
                    iconb, labelb, onclickb, tooltipb)
    {
        let entry = new MenuEntrySwitch(icona, labela, onclicka, tooltipa,
                                        iconb, labelb, onclickb, tooltipb)
        this.entries[name] = entry;
        this.AppendChild(entry);
        return
    }



    AddSection(headlinetext, htmlelement)
    {
        htmlelement.classList.add("sectionbody");

        let sectiontitle = new Element("div", ["sectiontitle", "hlcolor"]);
        sectiontitle.SetInnerText(headlinetext);

        let section = new Element("div", ["section"]);
        section.AppendChild(sectiontitle);
        section.AppendChild(htmlelement);
        this.AppendChild(section);
    }



    // force can be "a" or "b".
    SwitchEntry(name, force=null)
    {
        let switchentry = this.entries[name];
        if(force === "a")
            switchentry.SwitchToA();
        else if(force === "b")
            switchentry.SwitchToB();
        else
            switchentry.Toggle();
        return;
    }



    HideEntry(entryname)
    {
        if(!(entryname in this.entries))
        {
            window.console && console.warn(`Invalid menu entry name ${entryname}`);
            return;
        }
        this.entries[entryname].Hide();
    }
    ShowEntry(entryname)
    {
        if(!(entryname in this.entries))
        {
            window.console && console.warn(`Invalid menu entry name ${entryname}`);
            return;
        }
        this.entries[entryname].Show();
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

