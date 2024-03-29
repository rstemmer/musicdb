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

class MusicDBHUD extends Element
{
    constructor()
    {
        super("div", ["MusicDBHUD", "frame", "flex-row"]);
        this.artworkbox    = document.createElement("div");
        this.musicinfobox  = document.createElement("div");
        this.albuminfobox  = document.createElement("div");
        this.artistinfobox = document.createElement("div");

        this.songicon      = new SVGIcon("Song");
        this.videoicon     = new SVGIcon("Video");
        this.albumicon     = new SVGIcon("Album");
        this.artisticon    = new SVGIcon("Artist");

        this._CreateElement();

        this.currentsongid = -1;
        this.currentvideoid= -1;
        this.mode          = "unknown"; // can be "audio", "video", "unknown"
        this.music         = null;
        this.tags          = null;
    }


    _CreateElement()
    {

        // Setting some defaults
        this.musicinfobox.classList.add( "InformationBoxElement");
        this.albuminfobox.classList.add( "InformationBoxElement");
        this.artistinfobox.classList.add("InformationBoxElement");

        // Artwork box
        this.artworkbox.classList.add("ArtworkBox");

        // Music information box
        let infobox     = document.createElement("div");
        infobox.classList.add("InformationBox");
        infobox.appendChild(this.musicinfobox);
        infobox.appendChild(this.albuminfobox);
        infobox.appendChild(this.artistinfobox);

        // Genre boxes
        let  genrebox    = document.createElement("div");
        this.maingenre   = document.createElement("div");
        this.subgenre    = document.createElement("div");
        genrebox.classList.add("GenreBox");
        this.maingenre.classList.add("hlcolor");
        this.subgenre.classList.add("hlcolor");
        genrebox.appendChild(this.maingenre);
        genrebox.appendChild(this.subgenre);

        // Mood and Property boxes
        this.moodbox     = document.createElement("div");
        this.propbox     = document.createElement("div");
        this.moodbox.classList.add("hlcolor");
        this.propbox.classList.add("hlcolor");

        // Compose final element
        this.element.appendChild(this.artworkbox);
        this.element.appendChild(infobox);
        this.element.appendChild(genrebox);
        this.element.appendChild(this.moodbox);
        this.element.appendChild(this.propbox);

        return;
    }



    _CreateInfoElement(icon, text)
    {
        let textelement = document.createElement("span");
        textelement.textContent = text;

        let infoelement = document.createElement("div");
        infoelement.appendChild(icon.GetHTMLElement());
        infoelement.appendChild(textelement);

        return infoelement;
    }



    SetAlbumArtwork(MDBAlbum)
    {
        let imgpath = EncodeArtworkPath(MDBAlbum.artworkpath);
        let albumid = MDBAlbum.id;

        this.artworkbox.dataset.musictype = "audio";
        this.artworkbox.innerHTML         = "";
        let  artwork = new AlbumArtwork(MDBAlbum, "medium");
        this.artworkbox.appendChild(artwork.GetHTMLElement());
        return;
    }

    SetVideoArtwork(MDBVideo)
    {
        let imgpath = EncodeVideoThumbnailPath(MDBVideo.framesdirectory, MDBVideo.thumbnailfile);
        let videoid = MDBVideo.id;

        this.artworkbox.dataset.musictype = "video";
        this.artworkbox.innerHTML         = "";
        let  artwork = new VideoArtwork(MDBVideo, "medium");
        this.artworkbox.appendChild(artwork.GetHTMLElement());
        return;
    }



    SetSongInformation(MDBSong, MDBAlbum, MDBArtist)
    {
        this.musicinfobox.innerHTML = "";
        this.musicinfobox.appendChild(this._CreateInfoElement(this.songicon, MDBSong.name));
        this.musicinfobox.onclick       = ()=>
            {
            }

        this.albuminfobox.style.display = "block";
        this.albuminfobox.innerHTML = "";
        this.albuminfobox.appendChild(this._CreateInfoElement(this.albumicon, MDBAlbum.name));
        this.albuminfobox.onclick       = ()=>
            {
                MusicDB.Request("GetAlbum", "ShowAlbum", {albumid:MDBAlbum.id});
            }

        this.artistinfobox.innerHTML = "";
        this.artistinfobox.appendChild(this._CreateInfoElement(this.artisticon, MDBArtist.name));
        this.artistinfobox.onclick      = ()=>
            {
                WebUI.GetView("Artists").ScrollToArtist(MDBArtist.id);
            }

        return;
    }

    SetVideoInformation(MDBVideo, MDBArtist)
    {
        this.musicinfobox.innerHTML = "";
        this.musicinfobox.appendChild(this._CreateInfoElement(this.videoicon, MDBVideo.name));
        this.musicinfobox.onclick       = ()=>
            {
                MusicDB.Request("GetVideo", "ShowVideo", {videoid:MDBVideo.id});
            }

        this.albuminfobox.style.display = "none";
        this.albuminfobox.innerHTML = "";
        this.albuminfobox.appendChild(this._CreateInfoElement(this.albumicon, "⸻"));
        this.albuminfobox.onclick       = ()=>
            {
            }

        this.artistinfobox.innerHTML = "";
        this.artistinfobox.appendChild(this._CreateInfoElement(this.artisticon, MDBArtist.name));
        this.artistinfobox.onclick      = ()=>
            {
                WebUI.GetView("Artists").ScrollToArtist(MDBArtist.id);
            }

        return;
    }



    UpdateHUDForSong(MDBSong, MDBAlbum, MDBArtist, MDBSongTags, reset)
    {
        this.music = MDBSong;
        this.tags  = MDBSongTags;

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
    }

    UpdateHUDForVideo(MDBVideo, MDBArtist, MDBVideoTags, reset)
    {
        this.music = MDBVideo;
        this.tags  = MDBVideoTags;

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
    }



    onMusicDBNotification(fnc, sig, rawdata)
    {
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        // Song Part
        if(fnc == "GetAudioStreamState")
        {
            // A fresh installes MusicDB may have no queue!
            if(args.song == null)
                return; // Nothing to do here

            let reset = this.currentsongid != args.song.id; // Reset like/dislike for new songs

            // New song playing?
            if(sig == "UpdateStreamState" && this.currentsongid != args.song.id)
            {
                this.currentsongid = args.song.id;
                this.UpdateHUDForSong(args.song, args.album, args.artist, args.songtags, reset);
            }

            if(sig == "UpdateHUD")
            {
                this.currentsongid = args.song.id;

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
            // A fresh installes MusicDB may have no queue!
            if(args.video == null)
                return; // Nothing to do here

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

        if(fnc == "GetTags")
        {
            if(pass != null && pass.origin == "MoodSettings")
            {
                // Update Mood-Flags
                if(this.mode == "video")
                {
                    this.moods = new VideoMoods();
                }
                else
                {
                    this.moods = new SongMoods();
                }
                this.moodbox.innerHTML = "";
                this.moodbox.appendChild(this.moods.GetHTMLElement());
                this.moods.UpdateButtons(this.music, this.tags);
            }
        }
    }
}




// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

