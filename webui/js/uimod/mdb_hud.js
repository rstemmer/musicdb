
"use strict";

class SVGIcon
{
    constructor(path, groupid)
    {
        this.icon      = document.createElement("object");
        this.icon.type = "image/svg+xml";
        this.icon.data = path;
        this.groupid   = groupid;
    }

    GetHTMLElement()
    {
        return this.icon;
    }

    SetColor(color)
    {
        if(this.icon.contentDocument == null)
        {
             // image not yet loaded
            this.icon.addEventListener("load",()=>
                {
                    let content = this.icon.contentDocument;
                    content.getElementById(this.groupid).setAttribute("fill", color);
                }, false);
            return;
        }

        let svg = this.icon.contentDocument.getElementById(this.groupid)
        if(svg == null)
            return;

        if(typeof svg.setAttribute === "function")
        {
            svg.setAttribute("fill",   color);
            svg.setAttribute("stroke", color);
        }

        //this._SetChildsColor(svg, color);
        return;
    }

    _SetChildsColor(parentnode, color)
    {
        if(!parentnode.hasChildNodes())
            return;

        let childnodes = parentnode.childNodes;
        for(let child of childnodes)
        {
            if(typeof child.setAttribute === "function")
            {
                child.setAttribute("fill",   color);
                child.setAttribute("stroke", color);
            }
            this._SetChildsColor(child, color);
        }
        return;
    }
}


class MusicDBHUD
{
    constructor()
    {
        this.artworkimg    = document.createElement("img");
        this.musicinfobox  = document.createElement("div");
        this.albuminfobox  = document.createElement("div");
        this.artistinfobox = document.createElement("div");

        this.songicon      = new SVGIcon("img/icons/Song.svg",   "Song");
        this.videoicon     = new SVGIcon("img/icons/Song.svg",   "Song");
        this.albumicon     = new SVGIcon("img/icons/Album.svg",  "Album");
        this.artisticon    = new SVGIcon("img/icons/Artist.svg", "Artist");

        this.element       = this._CreateElement();

        this.currentsongid = -1;
    }

    GetHTMLElement()
    {
        return this.element;
    }

    _CreateElement()
    {

        // Setting some defaults
        this.artworkimg.id   = "MDBHUD_AlbumCover";
        this.artworkimg.src  = "pics/TouchIcon.png";  // Default artwork

        this.musicinfobox.classList.add("mdbhud_infoelementbox");
        this.albuminfobox.classList.add("mdbhud_infoelementbox");
        this.artistinfobox.classList.add("mdbhud_infoelementbox");

        // Artwork box
        let artworkbox  = document.createElement("div");
        artworkbox.id   = "MDBHUD_AlbumBox";
        artworkbox.appendChild(this.artworkimg);

        // Music information box
        let infobox     = document.createElement("div");
        infobox.id      = "MDBHUD_InformationBox";
        infobox.appendChild(this.musicinfobox);
        infobox.appendChild(this.albuminfobox);
        infobox.appendChild(this.artistinfobox);

        // Genre boxes
        let genrebox    = document.createElement("div");
        let maingenre   = document.createElement("div");
        let subgenre    = document.createElement("div");
        maingenre.id    = "GenreHUD";
        subgenre.id     = "SubgenreHUD";
        maingenre.classList.add("hlcolor");
        subgenre.classList.add("hlcolor");
        genrebox.appendChild(maingenre);
        genrebox.appendChild(subgenre);

        // Mood and Property boxes
        let moodbox     = document.createElement("div");
        let propbox     = document.createElement("div");
        moodbox.id      = "MoodHUD";
        propbox.id      = "PropertyHUD";
        moodbox.classList.add("hlcolor");
        propbox.classList.add("hlcolor");

        // Compose final element
        let container   = document.createElement("div");
        container.id    = "MusicDBHUD";
        container.appendChild(artworkbox);
        container.appendChild(infobox);
        container.appendChild(genrebox);
        container.appendChild(moodbox);
        container.appendChild(propbox);

        return container;
    }



    _CreateInfoElement(icon, text)
    {
        let textelement = document.createElement("span");
        textelement.textContent = text;

        let infoelement = document.createElement("div");
        infoelement.classList.add("mdbhud_infoelement");
        infoelement.appendChild(icon.GetHTMLElement());
        infoelement.appendChild(textelement);

        return infoelement;
    }



    UpdateIconColor()
    {
        let color = GetHLColor();
        this.songicon.SetColor(color);
        this.videoicon.SetColor(color);
        this.albumicon.SetColor(color);
        this.artisticon.SetColor(color);
    }



    SetAlbumArtwork(MDBAlbum)
    {
        let imgpath = EncodeArtworkPath(MDBAlbum.artworkpath);
        let albumid = MDBAlbum.id;

        this.artworkimg.src     = imgpath;
        this.artworkimg.onclick = ()=>
            {
                MusicDB_Request("GetAlbum", "ShowAlbum", {albumid: albumid});
            }
        return;
    }

    SetVideoArtwork(MDBVideo)
    {
        let imgpath = EncodeVideoThumbnailPath(MDBVideo.framesdirectory, MDBVideo.thumbnailfile);
        let videoid = MDBVideo.id;

        this.artworkimg.src     = imgpath;
        this.artworkimg.onclick = ()=>
            {
                MusicDB_Request("GetVideo", "ShowVideo", {videoid: videoid});
            }
        return;
    }



    SetSongInformation(MDBSong, MDBAlbum, MDBArtist)
    {
        this.musicinfobox.innerHTML = "";
        this.musicinfobox.appendChild(this._CreateInfoElement(this.songicon, MDBSong.name));
        this.musicinfobox.onclick       = ()=>
            {
            }

        this.albuminfobox.innerHTML = "";
        this.albuminfobox.appendChild(this._CreateInfoElement(this.albumicon, MDBAlbum.name));
        this.albuminfobox.onclick       = ()=>
            {
                MusicDB_Request("GetAlbum", "ShowAlbum", {albumid:MDBAlbum.id});
            }

        this.artistinfobox.innerHTML = "";
        this.artistinfobox.appendChild(this._CreateInfoElement(this.artisticon, MDBArtist.name));
        this.artistinfobox.onclick      = ()=>
            {
                ScrollToArtist(MDBArtist.id);
            }

        this.UpdateIconColor();
        return;
    }

    SetVideoInformation(MDBVideo, MDBArtist)
    {
        this.musicinfobox.innerHTML = "";
        this.musicinfobox.appendChild(this._CreateInfoElement(this.videoicon, MDBVideo.name));
        this.musicinfobox.onclick       = ()=>
            {
                MusicDB_Request("GetVideo", "ShowVideo", {videoid:MDBVideo.id});
            }

        this.albuminfobox.innerHTML = "";
        this.albuminfobox.appendChild(this._CreateInfoElement(this.albumicon, "⸻"));
        this.albuminfobox.onclick       = ()=>
            {
            }

        this.artistinfobox.innerHTML = "";
        this.artistinfobox.appendChild(this._CreateInfoElement(this.artisticon, MDBArtist.name));
        this.artistinfobox.onclick      = ()=>
            {
                ScrollToArtist(MDBArtist.id);
            }

        this.UpdateIconColor();
        return;
    }



    onMusicDBNotification(fnc, sig, rawdata)
    {
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        if(fnc == "GetAudioStreamState")
        {
            // New song playing?
            if(sig == "UpdateStreamState" && this.currentsongid != args.song.id)
                this.currentsongid = args.song.id;

            if(sig == "UpdateStreamState" || sig == "UpdateHUD")
            {
                this.SetAlbumArtwork(args.album);
                this.SetSongInformation(args.song, args.album, args.artist);
            }
        }
        else if(fnc == "GetSong")
        {
            if(args.song.id == this.currentsongid)
            {
                this.SetAlbumArtwork(args.album);
                this.SetSongInformation(args.song, args.album, args.artist);
            }
        }
        else if(fnc == "GetVideoStreamState" && sig == "UpdateHUD")
        {
            this.SetVideoArtwork(args.video);
            this.SetVideoInformation(args.video, args.artist);
        }
    }
}




// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

