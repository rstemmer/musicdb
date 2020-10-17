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
 * This is a base class for SongQueueTile in SongTile.js
 * and VideoQueueTile in VideoTile.js
 */


class QueueTile extends Draggable
{
    constructor()
    {
        super();
    }

    // musictype: "song" or "video"
    CreateTile(musictype, musicid, entryid, artwork, title, subtitle, buttonbox)
    {
        this.element    = document.createElement("div");
        this.element.id = entryid;
        this.element.dataset.entryid   = entryid;
        this.element.dataset.musictype = musictype;
        this.element.dataset.musicid   = musicid;
        this.element.dataset.droptask  = "move";
        this.element.classList.add("flex-row");
        this.element.classList.add("QueueTile");

        title.classList.add("QueueTitle");
        subtitle.classList.add("QueueSubtitle");
        subtitle.classList.add("hlcolor");
        subtitle.classList.add("smallfont");

        // Create info box
        this.infobox    = document.createElement("div");
        this.infobox.classList.add("flex-column");
        this.infobox.classList.add("infobox");

        this.toprow     = document.createElement("div");
        this.toprow.classList.add("flex-row");
        this.toprow.appendChild(title);
        this.toprow.appendChild(buttonbox.GetHTMLElement());

        this.bottomrow  = document.createElement("div");
        this.bottomrow.classList.add("flex-row");
        this.bottomrow.appendChild(subtitle);

        // Create layout
        this.infobox.appendChild(this.toprow);
        this.infobox.appendChild(this.bottomrow);

        this.element.appendChild(artwork.GetHTMLElement());
        this.element.appendChild(this.infobox);
    }



    GetHTMLElement()
    {
        return this.element;
    }
}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

