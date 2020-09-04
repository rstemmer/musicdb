
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

    SetColor(htmlcolor)
    {
        this.icon.style.backgroundColor = htmlcolor;
    }

    Show()
    {
        this.icon.style.display = "block";
    }
    Hide()
    {
        this.icon.style.display = "none";
    }
}



class SVGButton extends SVGIcon
{
    constructor(name, onclick)
    {
        super(name)
        this.icon.onclick = onclick;
    }
}



class SVGToggleButton extends SVGIcon
{
    constructor(name, onclick)
    {
        super(name)
        this.onclick               = onclick;
        this.icon.dataset.selected = false;
        this.icon.onclick          = ()=>{this.onIconClick();};
    }

    onIconClick()
    {
        let oldstate = this.GetSelectionState();
        let newstate = ! oldstate;
        this.SetSelectionState(newstate);

        if(typeof this.onclick === "function")
            this.onclick(newstate);

        return;
    }


    GetSelectionState()
    {
        let state = this.icon.dataset.selected;
        return (state === "true");
    }
    SetSelectionState(state)
    {
        this.icon.dataset.selected = state;
    }
}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

