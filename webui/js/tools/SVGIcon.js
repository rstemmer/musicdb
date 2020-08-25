
"use strict";

class SVGIcon
{
    constructor(name)
    {
        let maskurl  = `url("img/icons/${name}.svg");`;

        this.icon    = document.createElement("div");
        this.icon.classList.add("icon");
        this.icon.style.cssText = "mask: "+maskurl;
    }

    GetHTMLElement()
    {
        return this.icon;
    }

    SetTooltip(tooltip)
    {
        this.icon.title = tooltip;
    }
}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

