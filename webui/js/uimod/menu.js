
"use strict";



class MainMenu
{
    constructor(topoffset, rightoffset)
    {
        this.icon        = new SVGIcon("Menu");
        this.entryarray  = new Array();
        
        this.topoffset   = topoffset;
        this.rightoffset = rightoffset;

        this.menubutton  = this._CreateMenuToggleButton(this.icon);


        this.entrylistelement = document.createElement("div");
        this.entrylistelement.classList.add("menuentrylist");
        this.entrylistelement.style.display = "none"; // Hide by default
        this.isopen      = false;

        this.element     = document.createElement("div");
        this.element.classList.add("menu");
        this.element.style.top      = this.topoffset;
        this.element.style.right    = this.rightoffset;
        this.element.appendChild(this.menubutton);
        this.element.appendChild(this.entrylistelement);
    }

    GetHTMLElement()
    {
        return this.element;
    }



    _CreateMenuToggleButton(icon)
    {
        let button = document.createElement("div");

        button.appendChild(icon.GetHTMLElement());
        button.classList.add("hovpacity");
        button.classList.add("menutogglebutton");

        button.onclick = ()=>
            {
                this.onToggleMenu();
            };
        return button;
    }



    UpdateMenuEntryList()
    {
        this.entrylistelement.innerHTML = "";

        for(let entry of this.entryarray)
        {
            this.entrylistelement.appendChild(entry.element);
        }

        return;
    }



    CreateSwitch(aicon, atext, afunction, bicon, btext, bfunction)
    {
        let entry = new Object();

        entry.aicon = aicon.GetHTMLElement();
        entry.bicon = bicon.GetHTMLElement();

        entry.atext             = document.createElement("span");
        entry.atext.textContent = atext;
        entry.btext             = document.createElement("span");
        entry.btext.textContent = btext;

        entry.afunction = afunction;
        entry.bfunction = bfunction;

        entry.switchstate = "a";

        entry.element = document.createElement("div");
        entry.element.classList.add("menuentry");
        entry.element.appendChild(entry.aicon);
        entry.element.appendChild(entry.atext);

        entry.element.onclick = (event)=>
            {
                if(entry.switchstate == "a")
                {
                    entry.afunction();
                    entry.switchstate = "b";
                    entry.element.innerHTML = "";
                    entry.element.appendChild(entry.bicon);
                    entry.element.appendChild(entry.btext);
                }
                else
                {
                    entry.bfunction();
                    entry.switchstate = "a";
                    entry.element.innerHTML = "";
                    entry.element.appendChild(entry.aicon);
                    entry.element.appendChild(entry.atext);
                }
            }

        this.entryarray.push(entry);
        return;
    }

    _CreateFullscreenSwitch()
    {
        let text  = document.createElement("span");
        text.textContent = "Enter Fullscreen";
        
        let icon  = new SVGIcon("img/icons/EnterFullscreen.svg");

        let entry = document.createElement("div");
        entry.classList.add("menuentry");
        entry.appendChild(icon.GetHTMLElement());
        entry.appendChild(text);
        return entry;
    }

    _CreateMDBModeSwitch()
    {
        let text  = document.createElement("span");
        text.textContent = "Switch to Video Mode";
        
        let icon  = new SVGIcon("img/icons/Switch2Video.svg");

        let entry = document.createElement("div");
        entry.classList.add("menuentry");
        entry.appendChild(icon.GetHTMLElement());
        entry.appendChild(text);
        return entry;
    }

    onToggleMenu()
    {
        if(this.isopen)
        {
            this.entrylistelement.style.display = "none";
            this.isopen = false;
        }
        else
        {
            this.entrylistelement.style.display = "flex";
            this.isopen = true;
        }
    }

}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

