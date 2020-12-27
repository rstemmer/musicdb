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


/*
 * Draggables must provide the following four attributes!
        this.element.id               = this.songid;
        this.element.dataset.musictype= "song";
        this.element.dataset.musicid  = this.songid;
        this.element.dataset.droptask = "insert";
*/
class Draggable
{
    constructor()
    {
    }



    /*
     * !! This method overwrites this.element.id to musictype + "_" + musicid
     * droptask: "move", "insert"
     */
    ConfigDraggable(musictype, musicid, droptask, idprefix="")
    {
        this.element.id                = idprefix + musictype + "_" + musicid;
        this.element.dataset.musictype = musictype;
        this.element.dataset.musicid   = musicid;
        this.element.dataset.droptask  = droptask;
    }



    BecomeDraggable()
    {
        if(this.element === undefined)
        {
            window.console && console.error("Unable to make a class object draggable that does not have an element item.");
            return false;
        }

        this.element.draggable   = true;
        this.element.ondragstart = (event)=>{this.onDragStart(event);};
        this.element.ondragend   = (event)=>{this.onDragEnd(event);};
        return true;
    }



    onDragStart(ev)
    {
        ev.dataTransfer.setData("draggableid",   ev.target.id);
        ev.dataTransfer.setData("draggabletype", ev.target.dataset.musictype);
        ev.dataTransfer.dropEffect = "move";

        // Use data-dragging to make these settings configurable in CSS
        this.oldopacity = ev.target.style.opacity || "1.0";
        ev.target.style.opacity = "0.5";
    }



    onDragEnd(ev)
    {
        ev.target.style.opacity = this.oldopacity;
    }

}
class DropTarget
{
    // allowedtypes: list of strings with allowed draggable musictypes (like "song", "album")
    // Only those types of draggable elements are considered
    constructor(allowedtypes=[])
    {
        this.allowedtypes = allowedtypes;
    }



    BecomeDropTarget()
    {
        this.element.ondragover  = (event)=>{this.onDragOver(event);};
        this.element.ondrop      = (event)=>{this.onDrop(event);};
        this.element.ondragenter = (event)=>{this.onDragEnter(event);};
        this.element.ondragleave = (event)=>{this.onDragLeave(event);};
    }



    onDragOver(ev)
    {
        ev.preventDefault();
        ev.dataTransfer.dropEffect = "move";
    }



    onDragEnter(ev)
    {
        let draggableid   = ev.dataTransfer.getData("draggableid");
        let draggabletype = ev.dataTransfer.getData("draggabletype");

        // If unsupported type, do nothing
        if(this.allowedtypes.indexOf(draggabletype) < 0)
        {
            ev.preventDefault();
            return;
        }

        let draggable     = document.getElementById(draggableid);
        let preview       = draggable.cloneNode(true /* include child nodes */);
        preview.style.opacity = 0.5;
        this.element.appendChild(preview);
    }

    onDragLeave(ev)
    {
        this.element.innerHTML = "";
    }



    onDrop(ev)
    {
        let draggableid   = ev.dataTransfer.getData("draggableid");
        let draggabletype = ev.dataTransfer.getData("draggabletype");
        ev.preventDefault();

        // If unsupported type, do nothing
        if(this.allowedtypes.indexOf(draggabletype) < 0)
        {
            return;
        }

        this.element.innerHTML = "";
        this.onTransfer(draggableid);
    }




    // This method should be implemented by a derived class
    onTransfer(draggableid)
    {
        window.console && console.warning("This method should have been implemented by a derived class!");
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

