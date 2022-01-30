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

class BaseAlbumTile extends Draggable
{
    /*
     * size: "small", "medium"
     */
    constructor(MDBAlbum, onclick, size)
    {
        super("div", ["AlbumTile"]);
        let albumid      = MDBAlbum.id;
        let albumname    = OptimizeAlbumName(MDBAlbum.name);
        let albumrelease = MDBAlbum.release;

        this.artwork     = new AlbumArtwork(MDBAlbum, size);

        this.metadata    = new Element("div", ["smallfont"]);

        this.titleelement= new Element("span", ["fgcolor"]);
        this.titleelement.SetInnerText(albumname);
        this.titleelement.SetTooltip(albumname);
        this.metadata.AppendChild(this.titleelement);

        if(size == "medium")
        {
            this.releaseelement = new Element("span", ["hlcolor"]);
            this.releaseelement.SetInnerText(albumrelease);
            this.metadata.AppendChild(this.releaseelement);
        }

        super.AppendChild(this.artwork);
        super.AppendChild(this.metadata);
        this.element.onclick      = onclick;
        this.element.dataset.size = size;

        this.ConfigDraggable("album", albumid, "insert", size); // Use size as ID-Prefix
        this.BecomeDraggable();
    }



    HideReleaseDate()
    {
        this.releaseelement.Hide();
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
    name = name.replaceAll(" - ", " – ");
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

