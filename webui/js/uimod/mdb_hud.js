
"use strict";

class MusicDBHUD
{
    constructor()
    {
        this.artworkimg    = document.createElement("img");
        this.musicinfobox  = document.createElement("div");
        this.albuminfobox  = document.createElement("div");
        this.artistinfobox = document.createElement("div");

        this.songicon      = new SVGIcon("Song");
        this.videoicon     = new SVGIcon("Video");
        this.albumicon     = new SVGIcon("Album");
        this.artisticon    = new SVGIcon("Artist");

        this.element       = this._CreateElement();

        this.currentsongid = -1;
        this.currentvideoid= -1;
        this.mode          = "unknown"; // can be "audio", "video", "unknown"
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
        this.maingenre   = document.createElement("div");
        this.subgenre    = document.createElement("div");
        this.maingenre.id    = "GenreHUD";
        this.subgenre.id     = "SubgenreHUD";
        this.maingenre.classList.add("hlcolor");
        this.subgenre.classList.add("hlcolor");
        genrebox.appendChild(this.maingenre);
        genrebox.appendChild(this.subgenre);

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

        return;
    }



    UpdateHUDForSong(MDBSong, MDBAlbum, MDBArtist, MDBSongTags, reset)
    {
        this.SetAlbumArtwork(MDBAlbum);
        this.SetSongInformation(MDBSong, MDBAlbum, MDBArtist);

        Songtags_UpdateMoodControl("MainMoodControl", MDBSongTags);
        if(reset == true)
            Songproperties_ShowControl("PropertyHUD", "MainPropertyControl");
        Songproperties_UpdateControl("MainPropertyControl", MDBSong, reset); // reset like/dislike state
        Taginput_Show("GenreHUD",    "MainSongGenreView",    MDBSong.id, MDBSongTags, "Genre",    "Song");
        Taginput_Show("SubgenreHUD", "MainSongSubgenreView", MDBSong.id, MDBSongTags, "Subgenre", "Song");

        UpdateStyle();    // Update new tags
    }

    UpdateHUDForVideo(MDBVideo, MDBArtist, MDBVideoTags, reset)
    {
        this.SetVideoArtwork(MDBVideo);
        this.SetVideoInformation(MDBVideo, MDBArtist);

        Videotags_UpdateMoodControl("MainMoodControl", MDBVideoTags);
        if(reset == true)
            Videoproperties_ShowControl("PropertyHUD", "MainPropertyControl");
        Videoproperties_UpdateControl("MainPropertyControl", MDBVideo, reset); // reset like/dislike state
        //Taginput_Show("GenreHUD",    "MainSongGenreView",    MDBVideo.id, MDBVideoTags, "Genre",    "Video");
        //Taginput_Show("SubgenreHUD", "MainSongSubgenreView", MDBVideo.id, MDBVideoTags, "Subgenre", "Video");

        // TODO: Just for text, move to better place
        this.maingenre.innerHTML = "";
        this.maingenrelist = new TagListView();
        this.maingenre.appendChild(this.maingenrelist.GetHTMLElement());
        this.maingenrelist.Update("video", MDBVideo.videoid, MDBVideoTags.genres);

        this.subgenre.innerHTML = "";
        this.subgenrelist = new TagListView();
        this.subgenre.appendChild(this.subgenrelist.GetHTMLElement());
        this.subgenrelist.Update("video", MDBVideo.videoid, MDBVideoTags.subgenres);

        UpdateStyle();    // Update new tags
    }



    onMusicDBNotification(fnc, sig, rawdata)
    {
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        // Song Part
        if(fnc == "GetAudioStreamState")
        {
            let reset = this.currentsongid != args.song.id; // Reset like/dislike for new songs

            // New song playing?
            if(sig == "UpdateStreamState" && this.currentsongid != args.song.id)
            {
                this.currentsongid = args.song.id;
                this.UpdateHUDForSong(args.song, args.album, args.artist, args.songtags, reset);
            }

            if(sig == "UpdateHUD")
            {
                // UpdateHUD can imply a mode switch
                if(this.mode != "audio")
                {
                    this.mode = "audio";
                    reset     = true;
                }

                this.UpdateHUDForSong(args.song, args.album, args.artist, args.songtags, reset);
            }
        }
        else if(fnc == "GetSong")
        {
            if(args.song.id == this.currentsongid)
            {
                this.UpdateHUDForSong(args.song, args.album, args.artist, args.tags, false /*no reset*/);
            }
        }

        // Video Part
        else if(fnc == "GetVideoStreamState")
        {
            let reset = this.currentvideoid != args.video.id; // Reset like/dislike for new songs

            if(sig == "UpdateStreamState" && this.currentvideoid != args.video.id)
            {
                this.currentvideoid = args.video.id;
            }

            if(sig == "UpdateHUD")
            {
                // UpdateHUD can imply a mode switch
                if(this.mode != "video")
                {
                    this.mode = "video";
                    reset     = true;
                }

                this.UpdateHUDForVideo(args.video, args.artist, args.videotags, reset)
            }
        }
        else if(fnc == "GetVideo")
        {
            if(args.video.id == this.currentvideoid)
            {
                this.UpdateHUDForVideo(args.video, args.artist, args.videotags, false /*no reset*/)
            }
        }
    }
}




// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

