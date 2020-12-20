// MusicDB,  a music manager with web-bases UI that focus on music.
// Copyright (C) 2017-2020  Ralf Stemmer <ralf.stemmer@gmx.net>
// 
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
// 
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
// 
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.

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

