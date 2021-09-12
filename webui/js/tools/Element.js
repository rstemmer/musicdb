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
     * type: A: a string like "div" or "span"
     *       B: an object representing an existing HTML element
     * classes: A set of CSS classes
     * id: element ID
     */
    constructor(type, classes=[], id=null)
    {
        if(typeof type === "object")
            this.element = type;
        else
            this.element = document.createElement(type);

        this.element.classList.add(...classes);

        if(typeof id === "string")
            this.element.id = id;

        this.displaystyle = this.element.style.display;
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
    ReplaceChild(newchild, oldchild)
    {
        if(typeof oldchild.GetHTMLElement === "function")
            oldchild = oldchild.GetHTMLElement();
        if(typeof newchild.GetHTMLElement === "function")
            newchild = newchild.GetHTMLElement();

        this.element.replaceChild(newchild, oldchild);
    }



    AddCSSClass(cssclass)
    {
        this.element.classList.add(cssclass);
    }
    RemoveCSSClass(cssclass)
    {
        this.element.classList.remove(cssclass);
    }



    SetData(property, value)
    {
        this.element.dataset[property] = value;
    }
    GetData(property)
    {
        return this.element.dataset[property];
    }



    SetTooltip(tooltip)
    {
        this.element.title = tooltip;
    }



    SetInnerText(text)
    {
        this.element.innerText = text;
    }
    SetInnerHTML(html)
    {
        this.element.innerHTML = html;
    }


    InsertBefore(newelement)
    {
        if(typeof newelement.GetHTMLElement === "function")
            newelement = newelement.GetHTMLElement();
        this.element.parentElement.insertBefore(newelement, this.element)
    }
    InsertAfter(newelement)
    {
        if(typeof newelement.GetHTMLElement === "function")
            newelement = newelement.GetHTMLElement();
        if(this.element.nextSibling !== null)
            this.element.parentElement.insertBefore(newelement, this.element.nextSibling)
        else
            this.element.parentElement.appendChild(newelement);
    }


    Show()
    {
        this.element.style.display = this.displaystyle;
    }
    Hide()
    {
        this.displaystyle = this.element.style.display;
        this.element.style.display = "none";
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

