
"use strict";

class SVGIcon
{
    constructor(path, groupid)
    {
        this.icon      = document.createElement("object");
        this.icon.type = "image/svg+xml";
        this.icon.data = path;
        this.groupid   = groupid;
    }

    GetHTMLElement()
    {
        return this.icon;
    }

    SetColor(color)
    {
        if(this.icon.contentDocument == null)
        {
             // image not yet loaded
            this.icon.addEventListener("load",()=>
                {
                    let content = this.icon.contentDocument;
                    content.getElementById(this.groupid).setAttribute("fill", color);
                }, false);
            return;
        }

        let svg = this.icon.contentDocument.getElementById(this.groupid)
        if(svg == null)
            return;

        if(typeof svg.setAttribute === "function")
        {
            svg.setAttribute("fill",   color);
            svg.setAttribute("stroke", color);
        }

        //this._SetChildsColor(svg, color);
        return;
    }

    _SetChildsColor(parentnode, color)
    {
        if(!parentnode.hasChildNodes())
            return;

        let childnodes = parentnode.childNodes;
        for(let child of childnodes)
        {
            if(typeof child.setAttribute === "function")
            {
                child.setAttribute("fill",   color);
                child.setAttribute("stroke", color);
            }
            this._SetChildsColor(child, color);
        }
        return;
    }
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

