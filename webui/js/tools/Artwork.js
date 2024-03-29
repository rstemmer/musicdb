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


class Artwork extends Draggable
{
    // size: "small", "medium"
    constructor(size, classes=[])
    {
        super("div", ["Artwork", ...classes]);
        this.imageelement             = document.createElement("img");
        this.imageelement.draggable   = false;
        super.AppendChild(this.imageelement);
        this.element.onclick          = ()=>{this.onClick();};
        this.element.dataset.size     = size;
    }



    ConfigDraggable(musictype, musicid, droptask)
    {
        super.ConfigDraggable(musictype, musicid, droptask, "artwork");
    }



    // This method should be implemented by a derived class
    onClick()
    {
        window.console && console.warning("This method should have been implemented by a derived class!");
    }
}



class MusicDBLogo extends Artwork
{
    constructor()
    {
        super("large", ["AlbumArtwork"]);
        this.imageelement.src = "img/mdblogo-light.svg";
    }

    onClick()
    {
        event.preventDefault();
    }
}



class AlbumArtwork extends Artwork
{
    constructor(MDBAlbum, size)
    {
        super(size, ["AlbumArtwork"]);

        if(MDBAlbum != null)
        {
            this.albumid     = MDBAlbum.id;
            this.artworkpath = MDBAlbum.artworkpath;
        }
        else
        {
            this.albumid     = null;
            this.artworkpath = "default.jpg";
        }

        if(document.body?.clientWidth < 2500)
        {
            if(size == "small" || size == "medium")
                this.dimension = "150x150";
            else if(size == "large")
                this.dimension = "500x500";
            else
                this.dimension = "500x500"; // default to high resolution
        }
        else // 4K
        {
            if(size == "small")
                this.dimension = "150x150";
            else if(size == "medium")
                this.dimension = "200x200";
            else if(size == "large")
                this.dimension = "1000x1000";
            else
                this.dimension = "1000x1000"; // default to high resolution
        }

        this.imgpath          = EncodeArtworkPath(this.artworkpath, this.dimension);
        this.imageelement.src = this.imgpath;
    }



    onClick()
    {
        event.preventDefault();
        //event.stopPropagation();
        // The onClick event must be propagated to the Search Result Preview
        // so that the preview recognizes an action an can close itself.

        if(this.albumid != null)
            MusicDB.Request("GetAlbum", "ShowAlbum", {albumid: this.albumid});
    }
}



class VideoArtwork extends Artwork
{
    constructor(MDBVideo, size)
    {
        super(size, ["VideoArtwork"]);
        
        this.videoid = MDBVideo.id;

        if(size == "small" || size == "medium")
        {
            this.anipath = EncodeVideoThumbnailPath(MDBVideo.framesdirectory, MDBVideo.previewfile,   150, 83);
            this.imgpath = EncodeVideoThumbnailPath(MDBVideo.framesdirectory, MDBVideo.thumbnailfile, 150, 83);
        }
        this.imageelement.src         = this.imgpath;
        this.imageelement.onmouseover = ()=>{this.imageelement.src = this.anipath;};
        this.imageelement.onmouseout  = ()=>{this.imageelement.src = this.imgpath;};
    }



    onClick()
    {
        event.preventDefault();
        event.stopPropagation();
        MusicDB.Request("GetVideo", "ShowVideo", {videoid: this.videoid});
    }
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

