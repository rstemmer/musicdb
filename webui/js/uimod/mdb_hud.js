
"use strict";


class MusicDBHUD
{
    constructor()
    {
        this.artworkimg = document.createElement("img");
        this.musicinfo  = this._CreateInfoElement("MDBHUD_Musicname");
        this.albuminfo  = this._CreateInfoElement("MDBHUD_Albumname");
        this.artistinfo = this._CreateInfoElement("MDBHUD_Artistname");

        this.element    = this._CreateElement();

        this.currentsongid  = -1;
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

        // Artwork box
        let artworkbox  = document.createElement("div");
        artworkbox.id   = "MDBHUD_AlbumBox";
        artworkbox.appendChild(this.artworkimg);

        // Music information box
        let infobox     = document.createElement("div");
        infobox.id      = "MDBHUD_InformationBox";
        infobox.appendChild(this.musicinfo);
        infobox.appendChild(this.albuminfo);
        infobox.appendChild(this.artistinfo);

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

    _CreateInfoElement(elementid)
    {
        let infoelement = document.createElement("div");
        infoelement.id  = elementid;
        infoelement.dataset.type = "unknown";
        infoelement.classList.add("mdbhud_infoelement");
        return infoelement;
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
        this.musicinfo.dataset.type  = "audio";
        this.musicinfo.textContent   = MDBSong.name;
        this.musicinfo.onclick       = ()=>
            {
            }

        this.albuminfo.dataset.type  = "audio";
        this.albuminfo.textContent   = MDBAlbum.name;
        this.albuminfo.onclick       = ()=>
            {
                MusicDB_Request("GetAlbum", "ShowAlbum", {albumid:MDBAlbum.id});
            }

        this.artistinfo.dataset.type = "audio";
        this.artistinfo.textContent  = MDBArtist.name;
        this.artistinfo.onclick      = ()=>
            {
                ScrollToArtist(MDBArtist.id);
            }
        return;
    }

    SetVideoInformation(MDBVideo, MDBArtist)
    {
        this.musicinfo.dataset.type  = "video";
        this.musicinfo.textContent   = MDBVideo.name;
        this.musicinfo.onclick       = ()=>
            {
                MusicDB_Request("GetVideo", "ShowVideo", {videoid:MDBVideo.id});
            }

        this.albuminfo.dataset.type  = "video";
        this.albuminfo.textContent   = "⸻";
        this.albuminfo.onclick       = ()=>
            {
            }

        this.artistinfo.dataset.type = "audio";
        this.artistinfo.textContent  = MDBArtist.name;
        this.artistinfo.onclick      = ()=>
            {
                ScrollToArtist(MDBArtist.id);
            }
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

