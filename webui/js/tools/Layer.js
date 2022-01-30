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


class LayerBackground extends Curtain
{
    constructor(zindex=1, cssclasses=[])
    {
        super(cssclasses);
        this.element.style.zIndex = zindex;
        this.element.onclick     = "";
        this.element.ondragenter = "";
        this.element.ondragleave = "";
        delete this.clickhandler;
        this.AddCSSClass("LayerBackground");
    }
}


class Layer extends Element
{
    // background: Instance of the Curtain class that lays behind the Layer.
    // When the layer is made visible, then also the background will be shown
    constructor(background, id)
    {
        super("div", ["Layer", "frame", "opaque"], id);
        this.background = background;
        this.SetZIndex();
        this.Hide();
    }



    SetZIndex(zindex=null)
    {
        if(zindex === null)
        {
            zindex = parseInt(this.background.element.style.zIndex);
        }
        this.element.style.zIndex = zindex;
    }



    Show()
    {
        this.background.Show();
        this.element.scrollTo({top: 0, left: 0});
        this.element.style.visibility = "visible";
    }
    Hide()
    {
        this.background.Hide();
        this.element.style.visibility = "hidden";
    }



    /*
    onMusicDBMessage(fnc, sig, args, pass)
    {
        window.console?.warn("Derived class must implement a onMusicDBMessage method!");
    }
    */
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

