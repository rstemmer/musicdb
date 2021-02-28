// MusicDB,  a music manager with web-bases UI that focus on music.
// Copyright (C) 2017-2021  Ralf Stemmer <ralf.stemmer@gmx.net>
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

class VideoTile extends Draggable
{
    // flagbar is optional
    constructor(MDBVideo, onclick, flagbar)
    {
        super("div", ["VIdeoTile"]);

        let videoid      = MDBVideo.id;
        let videoname    = MDBVideo.name;
        let videorelease = MDBVideo.release;

        this.artwork                  = new VideoArtwork(MDBVideo, "medium");

        this.titleelement             = document.createElement("span");
        this.titleelement.textContent = videoname;
        this.titleelement.classList.add("hlcolor");
        this.titleelement.classList.add("smallfont");

        this.buttonbox                = new ButtonBox_AddVideoToQueue(videoid);

        super.AppendChild(this.artwork);
        super.AppendChild(this.buttonbox);
        super.AppendChild(this.titleelement);
        if(flagbar !== undefined)
            super.AppendChild(flagbar);
        this.element.onclick = onclick;

        if(MDBVideo.disabled)
            this.SetDisabled();
        else
            this.SetEnabled();

        this.ConfigDraggable("video", videoid, "insert");
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
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

