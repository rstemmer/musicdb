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


class ToolBar extends Element
{
    constructor()
    {
        super("div", ["ToolBar", "flex-row"]);
    }



    // FIXME BUG: Only ToolGroup elements are supported (CSS Issue with .SVGIcons vs border)
    // button: objects like SVGButton or ToolGroup
    // button.GetHTMLElement() must exist and return a div element
    AddButton(button)
    {
        this.AppendChild(button);
    }



    AddSpacer(grow=false)
    {
        let spacer = new Element("span", ["spacer"]);
        if(grow)
            spacer.AddCSSClass("flex-grow");
        this.AppendChild(spacer);
    }
}



class ToolGroup extends Element
{
    constructor(buttons = [])
    {
        super("div", ["ToolGroup", "flex-row"]);

        for(let button of buttons)
        {
            this.AddButton(button);
        }
    }



    // button: objects like SVGButton
    // button.GetHTMLElement() must exist and return a div element
    //
    // returns the outer container div element
    AddButton(button)
    {
        let div = new Element("div");
        div.AppendChild(button);
        this.AppendChild(div);
        return div;
    }
}



class SwitchGroup extends ToolGroup
{
    constructor(buttons = [], select=0)
    {
        super();

        this.buttons = new Array();
        for(let index in buttons)
        {
            let button = buttons[index];
            let box    = this.AddButton(button);
            box.GetHTMLElement().onclick= ()=>{this.Select(index);};
            box.SetData("selected", false);
            box.SetData("enabled",  true);

            this.buttons.push(new Object());
            this.buttons[index].button  = button;
            this.buttons[index].box     = box;
            this.buttons[index].enabled = true;
        }
        this.Select(select);
    }



    SetChangeEvent(handler)
    {
        this.element.onclick = handler;
    }



    Select(index)
    {
        // Do not select disabled buttons
        if(this.buttons[index].enabled == false)
            return;

        for(let entry of this.buttons)
        {
            entry.box.SetData("selected", false);
        }

        this.buttons[index].box.SetData("selected", true);

        this.selected = index;
        return;
    }



    Disable(index)
    {
        this._SetEnabledState(index, false);
        return;
    }

    Enable(index)
    {
        this._SetEnabledState(index, true);
        return;
    }
    _SetEnabledState(index, state)
    {
        this.buttons[index].box.SetData("enabled", state);
        this.buttons[index].enabled = state;
        return;
    }



    GetSelectionIndex()
    {
        return this.selected;
    }
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

