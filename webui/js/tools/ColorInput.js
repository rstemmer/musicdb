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

class ColorInput extends Element
{
    // when label == null, no label will be created
    constructor(label, tooltip, initcolor, onsave, onpreview)
    {
        super("div", ["ColorInput"]);

        this.input          = document.createElement("input");
        this.input.type     = "color";
        this.input.value    = initcolor;
        this.input.onchange = ()=>{this.onColorChange();};
        this.input.oninput  = ()=>{this.onColorPreview();};
        this.save           = onsave;
        this.preview        = onpreview;
        this.input.title    = tooltip;

        // Connect label and input with random name
        if(label != null)
        {
            this.label          = document.createElement("label");
            this.label.innerText= label;
            this.label.title    = tooltip;
            this.name           = Math.random().toString(16);
            this.input.name     = this.name;
            this.label.for      = this.name;
            this.element.appendChild(this.label);
        }

        this.element.appendChild(this.input);
    }



    SetColor(color)
    {
        this.input.value = color;
    }

    GetColor()
    {
        return this.input.value;
    }



    onColorChange()
    {
        let color = this.input.value;

        if(typeof this.save === "function")
            this.save(color);

        return;
    }


    onColorPreview()
    {
        let color = this.input.value;

        if(typeof this.preview === "function")
            this.preview(color);

        return;
    }
}



class ColorSchemeSelection extends Element
{
    constructor(musictype, musicid)  // Musictype: audio/video
    {
        super("div", ["ColorSchemeSelection", "flex-column"]);
        this.musictype  = musictype;
        this.musicid    = musicid;

        this.bginput = new ColorInput(
            "Background Color",
            "Change background color",
            colormanager.GetBGColor(),
            (color)=>{this.onSave("bgcolor", color);}, 
            (color)=>{this.onPreview("bgcolor", color);});

        this.fginput = new ColorInput(
            "Primary Color",
            "Change primary foreground color",
            colormanager.GetFGColor(),
            (color)=>{this.onSave("fgcolor", color);}, 
            (color)=>{this.onPreview("fgcolor", color);});

        this.hlinput = new ColorInput(
            "Secondary Color",
            "Change secondary foreground color",
            colormanager.GetHLColor(),
            (color)=>{this.onSave("hlcolor", color);}, 
            (color)=>{this.onPreview("hlcolor", color);});

        this.element.appendChild(this.bginput.GetHTMLElement());
        this.element.appendChild(this.fginput.GetHTMLElement());
        this.element.appendChild(this.hlinput.GetHTMLElement());
    }



    SetColors(bgcolor, fgcolor, hlcolor)
    {
        this.bginput.SetColor(bgcolor);
        this.fginput.SetColor(fgcolor);
        this.hlinput.SetColor(hlcolor);
    }



    onSave(colorname, colorvalue)
    {
        this.ApplyColorScheme();

        if(this.musictype == "video")
            MusicDB_Call("SetVideoColor", {videoid: this.musicid, colorname: colorname, color: colorvalue});
        else if(this.musictype == "audio")
            MusicDB_Call("SetAlbumColor", {albumid: this.musicid, colorname: colorname, color: colorvalue});
    }



    onPreview(colorname, colorvalue)
    {
        this.ApplyColorScheme();
    }



    ApplyColorScheme()
    {
        let bgcolor = this.bginput.GetColor();
        let fgcolor = this.fginput.GetColor();
        let hlcolor = this.hlinput.GetColor();

        colormanager.UpdateColor(fgcolor, hlcolor, bgcolor);
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

