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



class Curtain extends Element
{
    constructor(cssclasses=[])
    {
        super("div", ["Curtain", ...cssclasses]);
        this.element.onclick     = ()=>{this.onClick();};
        this.element.ondragenter = ()=>{this.onDragEnter();};
        this.element.ondragleave = ()=>{this.onDragLeave();};

        this.clickhandler = new Array();

        this.Hide();
    }



    onClick()
    {
        this.Hide();
        for(let handler of this.clickhandler)
            handler();
    }



    onDragEnter()
    {
        this.Hide();
    }
    onDragLeave()
    {
        this.Show();
    }



    AddClickEvent(handler)
    {
        this.clickhandler.push(handler);
    }



    Show()
    {
        this.element.style.visibility = "visible";
    }
    Hide()
    {
        this.element.style.visibility = "hidden";
    }
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

