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

class ViewManager
{
    constructor(containerid)
    {
        this.container = document.getElementById(containerid);
    }



    MountView(view)
    {
        let element = view.GetHTMLElement();
        this.container.innerHTML = "";
        this.container.appendChild(element);
        return;
    }
}


// Whenever a view gets removed from the Main View Box,
// its method "onViewRemoved();" gets called if it exists
class MainViewManager extends ViewManager
{
    constructor()
    {
        super("MiddleContentBox");
        this.currentview = null;
    }



    MountView(view)
    {
        if(this.currentview != null
            && typeof this.currentview.GetLockState === "function"
            && this.currentview.GetLockState() == true)
            return;

        super.MountView(view);

        if(this.currentview != null)
        {
            if(typeof this.currentview.onViewRemoved === "function")
                this.currentview.onViewRemoved();
        }

        this.currentview = view;
    }



    ShowAboutMusicDB()
    {
        this.MountView(aboutmusicdb);
    }
    ShowWelcome()
    {
        this.MountView(welcome);
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        if(fnc == "GetAlbum")
        {
            if(sig == "ShowAlbum")
            {
                this.MountView(albumview);
            }
        }
        else if(fnc == "GetVideo")
        {
            if(sig == "ShowVideo")
            {
                this.MountView(videoview);
            }
        }
        else if(fnc == "GetSongLyrics")
        {
            if(sig == "ShowLyrics")
            {
                this.MountView(lyricsview);
            }
        }
        else if(fnc == "Find")
        {
            if(sig == "ShowResults")
            {
                this.MountView(searchresultsview);
            }
        }
        else if(fnc == "GetSongRelationship")
        {
            if(sig == "ShowSongRelationship")
            {
                this.MountView(songrelationsview);
            }
        }
        return;
    }


}



class VideoPanelManager extends ViewManager
{
    constructor()
    {
        super("VideoPanel");
    }
}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

