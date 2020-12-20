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


class ToolBar
{
    constructor()
    {
        this.element = document.createElement("div");
        this.element.classList.add("ToolBar");
        this.element.classList.add("flex-row");
    }



    GetHTMLElement()
    {
        return this.element;
    }



    // button: objects like SVGButton or ToolGroup
    // button.GetHTMLElement() must exist and return a div element
    AddButton(button)
    {
        this.element.appendChild(button.GetHTMLElement());
    }



    AddSpacer(grow=false)
    {
        let spacer = document.createElement("span");
        spacer.classList.add("spacer");
        if(grow)
            spacer.classList.add("flex-grow");
        this.element.appendChild(spacer);
    }
}



class ToolGroup
{
    constructor(buttons = [])
    {
        this.element = document.createElement("div");
        this.element.classList.add("ToolGroup");
        this.element.classList.add("flex-row");

        for(let button of buttons)
        {
            this.AddButton(button);
        }
    }



    GetHTMLElement()
    {
        return this.element;
    }



    // button: objects like SVGButton
    // button.GetHTMLElement() must exist and return a div element
    //
    // returns the outer container div element
    AddButton(button)
    {
        let div = document.createElement("div");
        div.appendChild(button.GetHTMLElement());
        this.element.appendChild(div);
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
            box.onclick= ()=>{this.Select(index);};

            this.buttons.push(new Object());
            this.buttons[index].button = button;
            this.buttons[index].box    = box;
        }
        this.Select(select);
    }



    Select(index)
    {
        for(let entry of this.buttons)
        {
            entry.box.dataset.selected = false;
        }

        this.buttons[index].box.dataset.selected = true;

        this.selected = index;
        return;
    }



    GetSelectionIndex()
    {
        return this.selected;
    }
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

