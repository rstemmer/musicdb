
"use strict";

class FullscreenManager
{
    constructor()
    {
        if(document.fullscreenElement)
            this.infullscreen = true;
        else
            this.infullscreen = false;

        document.addEventListener("fullscreenchange", (event)=>
            {
                if(document.fullscreenElement)  // True when something is in fullscreen
                {
                    this.infullscreen = true;
                }
                else
                {
                    this.infullscreen = false;
                }
            });
    }



    inFullscreen()
    {
        return this.infullscreen;
    }



    EnterFullscreen()
    {
        if(document.fullscreenEnabled)
            document.documentElement.requestFullScreen();
    }

    LeaveFullscreen()
    {
        if(document.fullscreenEnabled && document.fullscreenElement)
            window.document.exitFullscreen();
    }

    ToggleFullscreen()
    {
        if(this.infullscreen)
            this.LeaveFullscreen();
        else
            this.EnterFullscreen();
    }
}


class MainMenu
{
    constructor(topoffset, rightoffset)
    {
        this.icon        = new SVGIcon("img/icons/Menu.svg");
        //this.icon        = new SVGIcon("img/icons/Artist.svg", "Artist");
        this.topoffset   = topoffset;
        this.rightoffset = rightoffset;
        this.menubutton  = this._CreateMenuToggleButton(this.icon);
        this.entrylist   = this._CreateEntryList();
        this.isopen      = false;

        this.element     = document.createElement("div");
        this.element.classList.add("menu");
        this.element.style.top      = this.topoffset;
        this.element.style.right    = this.rightoffset;
        this.element.appendChild(this.menubutton);
        this.element.appendChild(this.entrylist);
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
                window.console && console.log("Button clicked");
                this.onToggleMenu();
            };
        return button;
    }

    _CreateEntryList()
    {
        let entries = document.createElement("div");
        entries.classList.add("menuentrylist");
        entries.style.display = "none"; // Hide by default

        entries.appendChild(this._CreateFullscreenSwitch());
        entries.appendChild(this._CreateMDBModeSwitch());

        return entries;
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
            this.entrylist.style.display = "none";
            this.isopen = false;
        }
        else
        {
            this.entrylist.style.display = "flex";
            this.isopen = true;
        }
    }

}

/*

function ToggleFullscreen()
{
    var state = $("#FSB").attr("data-fsstate");

    if(state == "normal")
    {
        let  el = document.documentElement,
            rfs = el.requestFullscreen
               || el.webkitRequestFullScreen
               || el.mozRequestFullScreen
               || el.msRequestFullscreen 
            ;

        rfs.call(el);
        $("#FSB").attr("data-fsstate", "fullscreen");
    }
    else
    {
        let  el = window.document,
            rfs = el.exitFullscreen
               || el.webkitExitFullscreen
               || el.mozCancelFullScreen
               || el.msExitFullscreen 
            ;

        rfs.call(el);
        $("#FSB").attr("data-fsstate", "normal");
    }
};
*/

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

