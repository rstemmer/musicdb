
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
            document.documentElement.requestFullscreen();
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



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

