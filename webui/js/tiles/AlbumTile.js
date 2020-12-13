
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

/*
 *
 * Requirements:
 *   - JQuery
 *   - albumtile.css
 * Show:
 * Functions:
 * Callbacks:
 * Recommended Paths:
 * Trigger: (fnc -> sig)
 *   - GetAlbum -> ShowAlbum
 *
 */

function CreateAlbumTile(MDBAlbum)
{
    return _CreateAlbumTile(MDBAlbum, "medium");
}
function CreateSmallAlbumTile(MDBAlbum)
{
    return _CreateAlbumTile(MDBAlbum, "small");
}

// valid sizes: medium, small
function _CreateAlbumTile(MDBAlbum, size)
{
    var html        = "";
    var imgpath     = EncodeArtworkPath(MDBAlbum.artworkpath, "150x150");
    var albumid     = MDBAlbum.id;
    var albumname   = OptimizeAlbumName(MDBAlbum.name);
    var albumrelease= MDBAlbum.release;
    var albumrequest= "MusicDB_Request(\'GetAlbum\', \'ShowAlbum\', {albumid:"+albumid+"});";
    var datawidth   = "data-size=\"" + size + "\"";

    html += "<div";
    html += " class=\"AT_albumentry\"";
    html += " " + datawidth;
    html += " onClick=\"" + albumrequest + "\"";
    html += ">";

    // Cover
    html += "<div title=\"Show this Album\" class=\"AT_albumcover\" " + datawidth + ">";
    html += "<img src=\"" + imgpath + "\">";
    html += "</div>";
    
    html += "<div class=\"AT_albummetadata\">";
    if(size != "small")
        html += "<span class=\"AT_albumrelease hlcolor smallfont\">" + albumrelease + "</span>";
    html += "<span class=\"AT_albumname fgcolor smallfont\" title=\""+albumname+"\">" + albumname + "</span>";
    html += "</div>";

    html += "</div>";

    return html;
}


function OptimizeAlbumName(albumname)
{
    var name = albumname;

    // Remove "notes"
    var startofnote = name.indexOf("(", 1); // do not recognive an albumname starting with ( as note
    if(startofnote > 0)
    {
        name = name.substring(0, startofnote);
    }

    // Remove suffixed
    name = _RemoveSuffix(name, " - EP");
    name = _RemoveSuffix(name, " - Single");

    // Remove edition-Info: " - * Edition"
    var startofedition = name.search(/\s-\s\D*\sEdition/);
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
    var startofsuffix = albumname.indexOf(suffix);
    if(startofsuffix > 0)
    {
        albumname = albumname.substring(0, startofsuffix);
    }
    return albumname;
}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

