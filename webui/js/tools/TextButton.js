// MusicDB,  a music manager with web-bases UI that focus on music.
// Copyright (C) 2021  Ralf Stemmer <ralf.stemmer@gmx.net>
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

class TextButton extends Element
{
    constructor(iconname, text, onclick, tooltip)
    {
        super("div", ["TextButton", "flex-row", "hlcolor", "frame"]);
        this.icon = new SVGIcon(iconname);
        this.text = new Element("span");
        this.text.SetInnerText(text);

        this.SetTooltip(tooltip);
        this.AppendChild(this.icon);
        this.AppendChild(this.text);

        this.onclickcallback = onclick;
        this.element.onclick = ()=>{this.onClick();};
        this.Enable();
    }



    onClick()
    {
        if(this.GetData("enabled") == "false")
            return;

        this.onclickcallback();
    }



    Enable()
    {
        this.SetData("enabled", "true");
    }
    Disable()
    {
        this.SetData("enabled", "false");
    }
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

