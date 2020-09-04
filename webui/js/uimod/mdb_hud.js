
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
        this.moodbox     = document.createElement("div");
        this.propbox     = document.createElement("div");
        this.moodbox.id      = "MoodHUD";
        this.propbox.id      = "PropertyHUD";
        this.moodbox.classList.add("hlcolor");
        this.propbox.classList.add("hlcolor");

        // Compose final element
        let container   = document.createElement("div");
        container.id    = "MusicDBHUD";
        container.appendChild(artworkbox);
        container.appendChild(infobox);
        container.appendChild(genrebox);
        container.appendChild(this.moodbox);
        container.appendChild(this.propbox);

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
                artistsview.ScrollToArtist(MDBArtist.id);
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
                artistsview.ScrollToArtist(MDBArtist.id);
            }

        return;
    }



    UpdateHUDForSong(MDBSong, MDBAlbum, MDBArtist, MDBSongTags, reset)
    {
        this.SetAlbumArtwork(MDBAlbum);
        this.SetSongInformation(MDBSong, MDBAlbum, MDBArtist);

        // Update Properties and Moods
        if(reset == true)
        {
            this.moods = new SongMoods();
            this.moodbox.innerHTML = "";
            this.moodbox.appendChild(this.moods.GetHTMLElement());

            this.props = new SongProperties();
            this.props.ResetButtons();
            this.propbox.innerHTML = "";
            this.propbox.appendChild(this.props.GetHTMLElement());
        }
        this.moods.UpdateButtons(MDBSong, MDBSongTags);
        this.props.UpdateButtons(MDBSong);

        // Update Tags
        this.maingenre.innerHTML = "";
        this.maingenrelist = new TagListView();
        this.maingenre.appendChild(this.maingenrelist.GetHTMLElement());
        this.maingenrelist.Update("audio", MDBSong.id, MDBSongTags.genres);

        this.subgenre.innerHTML = "";
        this.subgenrelist = new TagListView();
        this.subgenre.appendChild(this.subgenrelist.GetHTMLElement());
        this.subgenrelist.Update("audio", MDBSong.id, MDBSongTags.subgenres);

        UpdateStyle();    // Update new tags
    }

    UpdateHUDForVideo(MDBVideo, MDBArtist, MDBVideoTags, reset)
    {
        this.SetVideoArtwork(MDBVideo);
        this.SetVideoInformation(MDBVideo, MDBArtist);

        // Update Properties and Moods
        if(reset == true)
        {
            this.moods = new VideoMoods();
            this.moodbox.innerHTML = "";
            this.moodbox.appendChild(this.moods.GetHTMLElement());

            this.props = new VideoProperties();
            this.props.ResetButtons();
            this.propbox.innerHTML = "";
            this.propbox.appendChild(this.props.GetHTMLElement());
        }
        this.moods.UpdateButtons(MDBVideo, MDBVideoTags);
        this.props.UpdateButtons(MDBVideo);

        // Update Tags
        this.maingenre.innerHTML = "";
        this.maingenrelist = new TagListView();
        this.maingenre.appendChild(this.maingenrelist.GetHTMLElement());
        this.maingenrelist.Update("video", MDBVideo.id, MDBVideoTags.genres);

        this.subgenre.innerHTML = "";
        this.subgenrelist = new TagListView();
        this.subgenre.appendChild(this.subgenrelist.GetHTMLElement());
        this.subgenrelist.Update("video", MDBVideo.id, MDBVideoTags.subgenres);

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
            this.currentvideoid = args.video.id;

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
                this.UpdateHUDForVideo(args.video, args.artist, args.tags, false /*no reset*/)
            }
        }
    }
}




// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

