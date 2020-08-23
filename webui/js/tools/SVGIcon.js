
"use strict";

class SVGIcon
{
    constructor(path, groupid)
    {
        let maskurl  = `url("${path}");`;

        this.icon    = document.createElement("div");
        this.icon.classList.add("icon");
        this.icon.style.cssText = "mask: "+maskurl;
        this.groupid = groupid;
    }

    GetHTMLElement()
    {
        return this.icon;
    }

    SetColor(color)
    {
        this.icon.style.backgroundColor = color;
        return;
    }
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

