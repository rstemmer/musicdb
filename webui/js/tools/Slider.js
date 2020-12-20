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

class Slider
{
    constructor(icon, onmove)
    {
        this.icon     = icon;
        this.onmove   = onmove;

        //this.handle   = document.createElement("div"); // TODO: this.icon.GetHTMLElement();
        this.handle   = this.icon.GetHTMLElement();
        this.slidebar = document.createElement("div");
        this.slidebar.classList.add("slidebar");
        this.slidebar.appendChild(this.handle);

        // All width and height values have the unit em
        const handlewidth  = 1.3;
        const handleheight = 1.3;

        this.handle.style.width      = handlewidth + "em";
        this.handle.style.left       = -handlewidth + "em";
        this.handle.style.marginLeft = (handlewidth / 2) + "em";
        this.handle.style.height     = handleheight + "em";
        this.handle.style.top        = -(handleheight / 2) + "em";

        this.mousedown = false;

        this.slidebar.onmousedown = (event)=>
            {
                this.mousedown = true;
                this._UpdateHandle(event.pageX);
            };

        document.addEventListener("mousemove", (event)=>
            {
                if(this.mousedown === true)
                    this._UpdateHandle(event.pageX);
            });

        document.addEventListener("mouseup", (event)=>
            {
                this.mousedown = false;
            });
    }

    _UpdateHandle(mousepos)
    {
        let slidebarpos   = this._ElementPosition(this.slidebar);
        let slidebarwidth = this.slidebar.offsetWidth;
        let handlewidth   = this.handle.offsetWidth;

        if(mousepos >= slidebarpos && mousepos <= (slidebarpos + slidebarwidth))
        {
            let handlepos   = mousepos - slidebarpos - handlewidth;
            let relativepos = (handlepos + handlewidth) / slidebarwidth;
            this.handle.style.left = handlepos + "px";

            if(typeof this.onmove === "function")
                this.onmove(relativepos);
        }
    }

    _ElementPosition(el) 
    {
        // See https://developer.mozilla.org/en-US/docs/Web/API/Element/getBoundingClientRect
        let domrect    = el.getBoundingClientRect(); // Get position in Viewport
        let pageoffset = window.pageXOffset;
        return domrect.left + pageoffset;
    }



    AddMouseWheelEvent(eventhandler)
    {
        this.slidebar.onwheel = eventhandler;
        this.handle.onwheel   = eventhandler;
        return;
    }


    GetHTMLElement()
    {
        return this.slidebar;
    }


    // pos as number relative (0..1)
    SetPosition(relpos)
    {
        if(isNaN(relpos))
            return;

        // If the slider is not in the DOM, it does not have a width.
        // The width is mandatory to calculate the handle position.
        if(document.contains(this.slidebar) == false)
            return;

        let slidebarwidth = this.slidebar.offsetWidth;
        let handlewidth   = this.handle.offsetWidth;
        let handlepos     = slidebarwidth * relpos - handlewidth;
        this.handle.style.left = handlepos + "px";
    }
}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

