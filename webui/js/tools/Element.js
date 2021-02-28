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

class Element
{
    /* Basic HTML Element
     * type: like "div" or "span"
     * classes: A set of CSS classes
     * id: element ID
     */
    constructor(type, classes=[], id=null)
    {
        this.element = document.createElement(type);
        this.element.classList.add(...classes);
        if(typeof id === "string")
            this.element.id = id;
    }



    GetHTMLElement()
    {
        return this.element;
    }



    AppendChild(child)
    {
        if(typeof child.GetHTMLElement === "function")
            this.element.appendChild(child.GetHTMLElement());
        else
            this.element.appendChild(child);
    }
    RemoveChilds()
    {
        this.element.innerHTML = "";
    }



    SetTooltip(tooltip)
    {
        this.element.title = tooltip;
    }



    SetInnerText(text)
    {
        this.element.innerText = text;
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

