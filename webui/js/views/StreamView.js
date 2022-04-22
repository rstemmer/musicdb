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

class StreamView extends MainView
{
    constructor()
    {
        super("StreamView");
        this.element.classList.add("StreamView");

        this.videoelement = document.createElement("video");
        this.element.appendChild(this.videoelement);

        this.streamplayer = new VideoStreamPlayer();
        this.streamplayer.SetVideoPlayerElement(this.videoelement);
        
        // Manage Detecting if Stream View is in a Visible Area of the WebUI
        this.intersectionobserver = new IntersectionObserver(
                (entries, observer)=>{this.onLeaveViewPort(entries[0], observer);}, // We observe only 1 entry
                {root: null, threshold: 0.5}
            );
        this.intersectionobserver.observe(this.videoelement);

        this.viewposition = null; // Can be "MainView", "QueueView", "VideoPanel"
    }



    onLeaveViewPort(entry, observer)
    {
        // Ignore invalid position state - this happens during initialization phase
        if(this.viewposition == null)
            return;

        // Change View Position when not visible anymore
        if(entry.isIntersecting == false)
        {
            if(this.viewposition == "VideoPanel")
                this.ShowInMainView();
            else
                this.ShowInVideoPanel();
        }

        return;
    }



    onViewUnmounted()
    {
        if(this.viewposition == "MainView")
            this.ShowInQueueView();
    }



    ShowInMainView()
    {
        if(this.viewposition == "QueueView")
            WebUI.GetView("Queue").UnmountStreamView();

        WebUI.GetManager("MainView").MountView(this);
        this.viewposition = "MainView";
    }
    ShowInQueueView()
    {
        WebUI.GetView("Queue").MountStreamView(this);
        this.viewposition = "QueueView";
    }
    ShowInVideoPanel()
    {
        if(this.viewposition == "QueueView")
            WebUI.GetView("Queue").UnmountStreamView();

        WebUI.GetManager("VideoPanel").MountView(this);
        this.viewposition = "VideoPanel";
    }



    onMusicDBNotification(fnc, sig, rawdata)
    {
        this.streamplayer.onMusicDBNotification(fnc, sig, rawdata);
        return;
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        this.streamplayer.onMusicDBMessage(fnc, sig, args, pass);
        return;
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

