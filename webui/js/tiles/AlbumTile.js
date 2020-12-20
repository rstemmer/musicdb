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

class BaseAlbumTile extends Draggable
{
    /*
     * size: "small", "medium"
     */
    constructor(MDBAlbum, onclick, size)
    {
        super();
        let albumid      = MDBAlbum.id;
        let albumname    = OptimizeAlbumName(MDBAlbum.name);
        let albumrelease = MDBAlbum.release;

        this.artwork     = new AlbumArtwork(MDBAlbum, size);

        this.metadata                 = document.createElement("div");
        this.metadata.classList.add("smallfont");

        this.titleelement             = document.createElement("span");
        this.titleelement.textContent = albumname;
        this.titleelement.classList.add("fgcolor");
        this.metadata.appendChild(this.titleelement);

        if(size == "medium")
        {
            this.releaseelement           = document.createElement("span");
            this.releaseelement.textContent=albumrelease
            this.releaseelement.classList.add("hlcolor");
            this.metadata.appendChild(this.releaseelement);
        }

        this.element                  = document.createElement("div");
        this.element.classList.add("AlbumTile");
        this.element.appendChild(this.artwork.GetHTMLElement());
        this.element.appendChild(this.metadata);
        this.element.onclick      = onclick;
        this.element.dataset.size = size;

        this.ConfigDraggable("album", albumid, "insert", size); // Use size as ID-Prefix
        this.BecomeDraggable();
    }



    GetHTMLElement()
    {
        return this.element;
    }
}



class AlbumTile extends BaseAlbumTile
{
    constructor(MDBAlbum, onclick)
    {
        super(MDBAlbum, onclick, "medium");
    }
}



class SmallAlbumTile extends BaseAlbumTile
{
    constructor(MDBAlbum, onclick)
    {
        super(MDBAlbum, onclick, "small");
    }
}



function OptimizeAlbumName(albumname)
{
    let name = albumname;

    // Remove "notes"
    let startofnote = name.indexOf("(", 1); // do not recognize an album name starting with ( as note
    if(startofnote > 0)
    {
        name = name.substring(0, startofnote);
    }

    // Remove suffixed
    name = _RemoveSuffix(name, " - EP");
    name = _RemoveSuffix(name, " - Single");

    // Remove edition-Info: " - * Edition"
    let startofedition = name.search(/\s-\s\D*\sEdition/);
    if(startofedition > 0)
    {
        name = name.substring(0, startofedition);
    }

    // Make nicer dashes
    name = name.replace(" - ", " – ");
    return name;
}



function _RemoveSuffix(albumname, suffix)
{
    let startofsuffix = albumname.indexOf(suffix);
    if(startofsuffix > 0)
    {
        albumname = albumname.substring(0, startofsuffix);
    }
    return albumname;
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

