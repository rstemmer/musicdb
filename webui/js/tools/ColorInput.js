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
        super("div", ["ColorInput", "flex-row"]);

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

        // Color input elements
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


        // Quality indicators
        this.bgindicator = new IndicatorBar("Darkness",  5, 10,  5);
        this.fgindicator = new IndicatorBar("Contrast", 70, 90, 20);
        this.hlindicator = new IndicatorBar("Contrast", 40, 70, 20);
        this.UpdateIndicators();

        this._CreateColorControl(this.bginput, this.bgindicator);
        this._CreateColorControl(this.fginput, this.fgindicator);
        this._CreateColorControl(this.hlinput, this.hlindicator);
    }



    _CreateColorControl(colorinput, qualityindicator)
    {
        let element = new Element("div", ["flex-row", "flex-right"]);
        element.AppendChild(colorinput);
        element.AppendChild(qualityindicator);
        this.AppendChild(element);
    }



    SetColors(bgcolor, fgcolor, hlcolor)
    {
        this.bginput.SetColor(bgcolor);
        this.fginput.SetColor(fgcolor);
        this.hlinput.SetColor(hlcolor);
    }



    UpdateIndicators()
    {
        // Calculate Accessibility (color contrast) to W3.org:
        // https://www.w3.org/TR/WCAG21/#contrast-minimum
        let rl_bg = CalculateRelativeLuminance(this.bginput.GetColor());
        let rl_fg = CalculateRelativeLuminance(this.fginput.GetColor());
        let rl_hl = CalculateRelativeLuminance(this.hlinput.GetColor());

        let fgcontrast = CalculateContrast(rl_fg, rl_bg);
        let hlcontrast = CalculateContrast(rl_hl, rl_bg);

        // Background should be dark, so only the lower 10% of the scale is considered.
        // To scale this up to 0…100, the color is multiplied by 1000 and cut to 100 max
        let bgvalue = rl_bg * 1000;
        if(bgvalue > 100)
            bgvalue = 100;

        this.bgindicator.SetIndicator(bgvalue);
        this.fgindicator.SetIndicator((fgcontrast / 21) * 100);    // 21 is max
        this.hlindicator.SetIndicator((hlcontrast / 21) * 100);    // 21 is max
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
        this.UpdateIndicators();
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

