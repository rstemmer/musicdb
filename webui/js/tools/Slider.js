
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
        function position(el) 
        {
            // See https://developer.mozilla.org/en-US/docs/Web/API/Element/getBoundingClientRect
            let domrect    = el.getBoundingClientRect(); // Get position in Viewport
            let pageoffset = window.pageXOffset;
            return domrect.left + pageoffset;
        }

        let slidebarpos   = position(this.slidebar);
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


    GetHTMLElement()
    {
        return this.slidebar;
    }
}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

