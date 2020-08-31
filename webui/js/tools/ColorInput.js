
"use strict";

class ColorInput
{
    constructor(label, tooltip, initcolor, onsave, onpreview)
    {
        this.label          = document.createElement("label");
        this.label.innerText= label;
        this.label.title    = tooltip;

        this.input          = document.createElement("input");
        this.input.type     = "color";
        this.input.value    = initcolor;
        this.input.onchange = ()=>{this.onColorChange();};
        this.input.oninput  = ()=>{this.onColorPreview();};
        this.save           = onsave;
        this.preview        = onpreview;
        this.input.title    = tooltip;

        // Connect label and input with random name
        this.name           = Math.random().toString(16);
        this.input.name     = this.name;
        this.label.for      = this.name;

        // Compose final element
        this.element        = document.createElement("div");
        //this.element.classList.add("flex-row");
        this.element.appendChild(this.label);
        this.element.appendChild(this.input);
    }



    GetHTMLElement()
    {
        return this.element;
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

class ColorSchemeSelection
{
    constructor(musictype, musicid)  // Musictype: audio/video
    {
        this.musictype  = musictype;
        this.musicid    = musicid;

        this.bginput = new ColorInput(
            "Background Color",
            "Change background color",
            lastbgcolor,
            (color)=>{this.onSave("bgcolor", color);}, 
            (color)=>{this.onPreview("bgcolor", color);});

        this.fginput = new ColorInput(
            "Primary Color",
            "Change primary foreground color",
            lastfgcolor,
            (color)=>{this.onSave("fgcolor", color);}, 
            (color)=>{this.onPreview("fgcolor", color);});

        this.hlinput = new ColorInput(
            "Secondary Color",
            "Change secondary foreground color",
            lasthlcolor,
            (color)=>{this.onSave("hlcolor", color);}, 
            (color)=>{this.onPreview("hlcolor", color);});

        this.element    = document.createElement("div");
        this.element.classList.add("flex-cloumn");
        this.element.classList.add("colorsettings");
        this.element.appendChild(this.bginput.GetHTMLElement());
        this.element.appendChild(this.fginput.GetHTMLElement());
        this.element.appendChild(this.hlinput.GetHTMLElement());
    }



    GetHTMLElement()
    {
        return this.element;
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
            MusicDB_Call("SetSongColor",  {songid:  this.musicid, colorname: colorname, color: colorvalue});
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

        UpdateStyle(bgcolor, fgcolor, hlcolor);
    }
}

/**
 * onchange: send color to database
 * preview: apply current selection to UI
 */
function CreateColorInput(id, color, onchange, previewfunction)
{
    var html = "";
    html += "<input type=color class=\"ColorInput\" id=" + id + " value=\"" + color + "\" ";
    //html += " data-previewfunction=" + previewfunction.name;
    html += " onChange=\"" + onchange + "\"";
    html += " onInput=\""  + previewfunction.name + "(this.id, this.value)\">";
    //html += " onBlur=\""   + onblur   + "\">";
    return html;
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

