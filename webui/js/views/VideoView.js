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


class VideoView
{
    constructor()
    {
        this.currentvideoid = -1;

        // Button Array
        this.buttons        = new Array();
        this.buttons.push(new SVGButton("Append", ()=>{this.AddVideoToQueue("last");}));
        this.buttons.push(new SVGButton("Insert", ()=>{this.AddVideoToQueue("next");}));

        // Create Headline
        this.headline       = new MainViewHeadline(this.buttons);

        // Create Video Player
        this.videoplayer    = document.createElement("video");
        this.videoplayer.controls = true;
        this.videoplayer.classList.add("mainview_videoplayer");

        // Settings
        this.settings_timeframe = document.createElement("div");

        this.settings_flags     = document.createElement("div");
        this.settings_flags.classList.add("flex-row");
        this.moodsbox           = document.createElement("div");
        this.propertiesbox      = document.createElement("div");
        this.genretagsbox       = document.createElement("div");
        this.genretagsbox.classList.add("flex-grow");
        this.settings_flags.appendChild(this.moodsbox);
        this.settings_flags.appendChild(this.propertiesbox);
        this.settings_flags.appendChild(this.genretagsbox);

        this.settings_artwork   = document.createElement("div");
        this.settings_artwork.classList.add("flex-row");
        this.colorbox           = document.createElement("div");
        this.thumbnailbox       = document.createElement("div");
        this.thumbnailbox.classList.add("flex-grow");
        this.settings_artwork.appendChild(this.thumbnailbox);
        this.settings_artwork.appendChild(this.colorbox);

        this.settings           = new TabSelect();
        this.settings.AddTab(new SVGIcon("Tags"),      "Flags & Tags",      this.settings_flags, true);
        this.settings.AddTab(new SVGIcon("Artwork"),   "Thumbnail & Color", this.settings_artwork);
        let tftabid = this.settings.AddTab(new SVGIcon("TimeFrame"), "Played Time Frame", this.settings_timeframe);
        // Because of the slider these initialization must take place after putting the elements into the DOM
        this.settings.SetOnShowCallback(tftabid, ()=>{this.timeframeselect.Initialize();});

        // Create Video View
        this.element  = document.createElement("div");
        this.element.classList.add("mainview_container");
        this.element.appendChild(this.headline.GetHTMLElement());
        this.element.appendChild(this.videoplayer);
        this.element.appendChild(this.settings.GetHTMLElement());
    }



    GetHTMLElement()
    {
        return this.element;
    }



    AddVideoToQueue(position)
    {
        MusicDB_Call("AddVideoToQueue", {videoid: this.currentvideoid, position: position});
    }



    UpdateInformation(MDBVideo, MDBArtist, MDBTags)
    {
        // For new videos, some persistent information need to be updated
        if(MDBVideo.id != this.currentvideoid)
        {
            this.currentvideoid = MDBVideo.id;

            // Update Headline
            this.headline.UpdateInformation(MDBVideo, MDBArtist)

            // Update Video
            let poster = EncodeVideoThumbnailPath(MDBVideo.framesdirectory, MDBVideo.thumbnailfile);
            let source = "/musicdb/music/" + MDBVideo.path;
            this.videoplayer.width  = MDBVideo.xresolution;
            this.videoplayer.height = MDBVideo.yresolution;
            this.videoplayer.poster = poster;
            this.videoplayer.src    = source;

            // Create fresh Settings
            this.timeframeselect    = new VideoTimeFrameSelection(this.videoplayer, MDBVideo);
            this.settings_timeframe.innerHTML = "";
            this.settings_timeframe.appendChild(this.timeframeselect.GetHTMLElement());

            this.videoproperties    = new VideoProperties();
            this.propertiesbox.innerHTML = "";
            this.propertiesbox.appendChild(this.videoproperties.GetHTMLElement());
            this.videoproperties.ResetButtons();

            this.videomoods         = new VideoMoods();
            this.moodsbox.innerHTML = "";
            this.moodsbox.appendChild(this.videomoods.GetHTMLElement());

            this.genreedit          = new TagListEdit("genre");
            this.subgenreedit       = new TagListEdit("subgenre");
            this.genretagsbox.innerHTML = "";
            this.genretagsbox.appendChild(this.genreedit.GetHTMLElement());
            this.genretagsbox.appendChild(this.subgenreedit.GetHTMLElement());

            this.colorsettings      = new ColorSchemeSelection("video", this.currentvideoid);
            this.colorbox.innerHTML = "";
            this.colorbox.appendChild(this.colorsettings.GetHTMLElement());

            this.thumbnailsettings  = new ThumbnailSelection(this.videoplayer, MDBVideo);
            this.thumbnailbox.innerHTML = "";
            this.thumbnailbox.appendChild(this.thumbnailsettings.GetHTMLElement());
            this.thumbnailsettings.Initialize();
    
        }

        // For new and already visible videos, all settings need to be synchronized
        this.videoproperties.UpdateButtons(MDBVideo);
        this.videomoods.UpdateButtons(MDBVideo, MDBTags);

        this.genreedit.Update(   "video", this.currentvideoid, MDBTags);
        this.subgenreedit.Update("video", this.currentvideoid, MDBTags);

        this.colorsettings.SetColors(MDBVideo.bgcolor, MDBVideo.fgcolor, MDBVideo.hlcolor);
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        if(fnc == "GetVideo")
        {
            if(sig == "ShowVideo")
            {
                this.UpdateInformation(args.video, args.artist, args.tags);
            }
            else if(sig == "UpdateVideo" || sig == "UpdateTagInput")
            {
                // Only update the video shown in the Video View
                if(args.video.id == this.currentvideoid)
                    this.UpdateInformation(args.video, args.artist, args.tags);
            }
        }
        return;
    }

}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

