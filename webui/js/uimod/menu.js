
"use strict";

class MainMenu
{
    constructor(topoffset, rightoffset)
    {
        //this.icon        = new SVGIcon("img/icons/Menu.svg", "Menu");
        this.icon        = new SVGIcon("img/icons/Artist.svg", "Artist");
        this.topoffset   = topoffset;
        this.rightoffset = rightoffset;
        this.menubutton  = this._CreateMenuToggleButton(this.icon);
        this.menuentries = this._CreateMenuEntries();

        this.element     = document.createElement("div");
        this.element.classList.add("menu");
        this.element.style.top      = this.topoffset;
        this.element.style.right    = this.rightoffset;
        this.element.appendChild(this.menubutton);
        this.element.appendChild(this.menuentries);
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

    _CreateMenuEntries()
    {
        let entries = document.createElement("div");
        entries.classList.add("menuentrylist");
        return entries;
    }



    onToggleMenu()
    {
        window.console && console.log("Toggle Menu.");
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

