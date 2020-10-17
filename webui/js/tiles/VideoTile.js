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


class VideoQueueTile extends QueueTile
{
    constructor(MDBVideo, MDBArtist, entryid, position, buttonbox)
    {
        super();
        this.videoid     = MDBVideo.id;
        let videoname    = MDBVideo.name.replace(" - ", " – ");
        let videorelease = MDBVideo.release;
        let artistname   = MDBArtist.name;
        let artistid     = MDBArtist.id;

        this.artwork                  = new VideoArtwork(MDBVideo, "small");

        this.infobox                  = document.createElement("div");
        this.infobox.classList.add("infobox");

        this.title             = document.createElement("div");
        this.title.textContent = videoname;
        this.title.onclick     = ()=>{this.ShowVideo();};

        this.subtitle            = document.createElement("div");
        this.subtitle.textContent = artistname;
        this.subtitle.onclick    = ()=>{artistsview.ScrollToArtist(artistid);};

        this.CreateTile("video", this.videoid, entryid, this.artwork, this.title, this.subtitle, buttonbox);

        if(position > 0)
            this.BecomeDraggable();
    }



    ShowVideo()
    {
        MusicDB_Request("GetVideo", "ShowVideo", {videoid: this.videoid});
    }
}



class VideoTile extends Draggable
{
    // flagbar is optional
    constructor(MDBVideo, onclick, flagbar)
    {
        super();

        let videoid      = MDBVideo.id;
        let videoname    = MDBVideo.name;
        let videorelease = MDBVideo.release;

        this.artwork                  = new VideoArtwork(MDBVideo, "medium");

        this.titleelement             = document.createElement("span");
        this.titleelement.textContent = videoname;
        this.titleelement.classList.add("hlcolor");
        this.titleelement.classList.add("smallfont");

        this.buttonbox                = new ButtonBox_AddVideoToQueue(videoid);

        this.element                  = document.createElement("div");
        this.element.id               = videoid;
        this.element.dataset.musictype= "video";
        this.element.dataset.musicid  = videoid;
        this.element.dataset.droptask = "insert";
        this.element.classList.add("VideoTile");
        this.element.appendChild(this.artwork.GetHTMLElement());
        this.element.appendChild(this.buttonbox.GetHTMLElement());
        this.element.appendChild(this.titleelement);
        if(flagbar !== undefined)
            this.element.appendChild(flagbar.GetHTMLElement());
        this.element.onclick = onclick;

        if(MDBVideo.disabled)
            this.SetDisabled();
        else
            this.SetEnabled();

        this.BecomeDraggable();
    }


    ReplaceFlagBar(newflagbar)
    {
        let newflagbarelement = newflagbar.GetHTMLElement();
        let oldflagbarelement = this.element.getElementsByClassName("FlagBar")[0];
        this.element.replaceChild(newflagbarelement, oldflagbarelement);
    }

    SetEnabled()
    {
        this.element.dataset.enabled = true;
    }
    SetDisabled()
    {
        this.element.dataset.enabled = false;
    }


    GetHTMLElement()
    {
        return this.element;
    }
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

