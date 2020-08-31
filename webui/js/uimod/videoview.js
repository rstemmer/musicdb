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


class MainViewHeadline
{
    constructor(buttonarray)
    {
        // Info box
        this.infobox        = document.createElement("div");

        // Content Name
        this.contentname    = document.createElement("span");
        this.contentname.classList.add("fgcolor");

        // Artist Name
        this.artistname     = document.createElement("span");
        this.artistname.classList.add("hlcolor");
        this.artistname.classList.add("smallfont");

        // Spacer between Artist and Release Year
        this.spacer         = document.createElement("span");
        this.spacer.classList.add("fgcolor");
        this.spacer.classList.add("smallfont");
        this.spacer.innerText = " — "; // EM DASH

        // Release Year
        this.releaseyear    = document.createElement("span");
        this.releaseyear.classList.add("hlcolor");
        this.releaseyear.classList.add("smallfont");

        // Info Box for Names
        this.infobox.appendChild(this.contentname);
        this.infobox.appendChild(this.artistname);
        this.infobox.appendChild(this.spacer);
        this.infobox.appendChild(this.releaseyear);

        // Button box
        this.buttonbox      = document.createElement("div");
        this.buttonbox.classList.add("flex-row");
        this.buttonbox.classList.add("hovpacity");
        for(let button of buttonarray)
        {
            this.buttonbox.appendChild(button.GetHTMLElement());
        }

        // Full headline
        this.element = document.createElement("div");
        this.element.classList.add("mainview_headline");
        this.element.classList.add("flex-row");
        this.element.appendChild(this.infobox);
        this.element.appendChild(this.buttonbox);
    }

    GetHTMLElement()
    {
        return this.element;
    }



    UpdateInformation(MDBMusic, MDBArtist)
    {
        this.contentname.innerText  = MDBMusic.name;
        this.artistname.innerText   = MDBArtist.name
        this.releaseyear.innerText  = MDBMusic.release;
        this.infobox.title          = MDBMusic.origin;
    }

}



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

        // Settings Box
        this.settingsbox    = document.createElement("div");
        this.settings_timeframe = document.createElement("div");
        this.settings_moods     = document.createElement("div");
        this.settings_properties= document.createElement("div");
        this.settingsbox.appendChild(this.settings_timeframe);
        this.settingsbox.appendChild(this.settings_moods);
        this.settingsbox.appendChild(this.settings_properties);

        // Create Video View
        this.element  = document.createElement("div");
        this.element.classList.add("mainview_container");
        this.element.appendChild(this.headline.GetHTMLElement());
        this.element.appendChild(this.videoplayer);
        this.element.appendChild(this.settingsbox);
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
            // Because of the slider these initialization must take place after putting the elements into the DOM
            this.timeframeselect.Initialize();

            this.videoproperties    = new VideoProperties();
            this.settings_properties.innerHTML = "";
            this.settings_properties.appendChild(this.videoproperties.GetHTMLElement());
            this.videoproperties.ResetButtons();

            this.videomoods         = new VideoMoods();
            this.settings_moods.innerHTML = "";
            this.settings_moods.appendChild(this.videomoods.GetHTMLElement());
    
        }

        // For new and already visible videos, all settings need to be synchronized
        this.videoproperties.UpdateButtons(MDBVideo);
        this.videomoods.UpdateButtons(MDBVideo, MDBTags);
    }

    _OLDUpdateVideoSettings(MDBVideo, MDBVideoTags, initialize)
    {
        let videoid = MDBVideo.id;
        let moodboxid = "VVS_moodbox";
        let propboxid = "VVS_propbox";
        let tagsboxid = "VVS_tagsbox";

        if(initialize == true)
            Videotags_ShowMoodControl(moodboxid, moodboxid);

        Videotags_UpdateMoodControl(moodboxid, MDBVideoTags);
        
        Taginput_Update("VVS_genre_"    + videoid, MDBVideoTags);
        Taginput_Update("VVS_subgenre_" + videoid, MDBVideoTags);
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        if(fnc == "GetVideo")
        {
            if(sig == "ShowVideo")
            {
                let mainviewbox = document.getElementById("MiddleContentBox"); // \_ HACK
                mainviewbox.innerHTML = "";
                mainviewbox.appendChild(videoview.GetHTMLElement());           // /  This should do a Main View Manager

                this.UpdateInformation(args.video, args.artist, args.tags);
            }
            else if(sig == "UpdateVideo" || sig == "UpdateTagInput")
            {
                // Only update the video shown in the Video View
                if(args.video.id == this.currentvideoid)
                    this.UpdateInformation(args.video, args.artist, args.tags);
            }
        }
    }

}

function _VV_CreateVideoSettings(MDBVideo, MDBVideoTags)
{
    let videoid = MDBVideo.id;
    let html = "";
    let moodboxid = "VVS_moodbox_" + videoid;
    let propboxid = "VVS_propbox_" + videoid;
    let tagsboxid = "VVS_tagsbox_" + videoid;
    let bgcolor   = MDBVideo.bgcolor || "#000000";
    let hlcolor   = MDBVideo.hlcolor || "#000000";    
    let fgcolor   = MDBVideo.fgcolor || "#000000";

    // Moods and Properties
    html += "<div class=\"VV_videosettings_row\">";
    html += "    <div id=\""+moodboxid+"\" class=\"VVS_moodbox hlcolor\">"
    html += "    </div>";
    html += "    <div id=\""+propboxid+"\" class=\"VVS_propbox hlcolor\">";
    html += "    </div>";
    html += "</div>";

    // Genres and Sub-genres
    html += "<div class=\"VV_videosettings_row\">";
    html += "    <div id=\""+tagsboxid+"\" class=\"VVS_tagsbox\">";
    html += Taginput_Create("VVS_genre_"    + videoid, videoid, "Genre",    "Video");
    html += Taginput_Create("VVS_subgenre_" + videoid, videoid, "Subgenre", "Video");
    html += "    </div>";
    html += "</div>";

    // Colors
    html += "<div class=\"VV_videosettings_row\">";
    html += "   <span class=\"ABVSettingName\">Background:</span>";
    html += CreateColorInput("CI_BGColor", bgcolor, 
        "_VV_onColorSave("+videoid+", \'CI_BGColor\');",
        _VV_onColorChange
        );
    
    html += "   <span class=\"ABVSettingName\">Foreground:</span>";
    html += CreateColorInput("CI_FGColor", fgcolor, 
        "_VV_onColorSave("+videoid+", \'CI_FGColor\');",
        _VV_onColorChange
        );
    
    html += "   <span class=\"ABVSettingName\">Highlight:</span>";
    html += CreateColorInput("CI_HLColor", hlcolor, 
        "_VV_onColorSave("+videoid+", \'CI_HLColor\');",
        _VV_onColorChange
        );
    html += "</div>";

    // Begin/End Time Selection
    html += "<div class=\"VV_videosettings_row\" id=\"BeginEndSelection\">";
    html += "</div>";
    return html;
}



function UpdateVideoSettings(MDBVideo, MDBVideoTags, initialize)
{
    let videoid = MDBVideo.id;
    let moodboxid = "VVS_moodbox_" + videoid;
    let propboxid = "VVS_propbox_" + videoid;
    let tagsboxid = "VVS_tagsbox_" + videoid;

    if(initialize == true)
        Videotags_ShowMoodControl(moodboxid, moodboxid);

    Videotags_UpdateMoodControl(moodboxid, MDBVideoTags);
    
    if(initialize == true)
        Videoproperties_ShowControl(propboxid, propboxid);

    Videoproperties_UpdateControl(propboxid, MDBVideo, initialize); // true: initialize and reset like/dislike buttons

    Taginput_Update("VVS_genre_"    + videoid, MDBVideoTags);
    Taginput_Update("VVS_subgenre_" + videoid, MDBVideoTags);
}



function _VV_onColorSave(videoid, elementid)
{
    var color = $("#"+elementid).val();

    // Do not send bullshit even if the server could handle it
    if(color == "#NANNANNAN")
        return;
    if(color == null || color == "null")
        return;

    // this is the NULL-Color. It would be so fucking bad designe-style that I will never use it
    if(color == "#000000")
        return;

    var colorname = "";
    if(elementid == "CI_BGColor")
        colorname = "bgcolor";
    else if(elementid == "CI_FGColor")
        colorname = "fgcolor";
    else if(elementid == "CI_HLColor")
        colorname = "hlcolor";
    else
        return;

    MusicDB_Call("SetVideoColor", {videoid:videoid, colorname:colorname, color:color});
}



function _VV_onColorChange(elementid, color)
{
    if(elementid == "CI_BGColor")
    {
        $(".bgcolor").css("background-color", color);
    }
    else if(elementid == "CI_FGColor")
    {
        $(".fgcolor").css("color", color);
    }
    else if(elementid == "CI_HLColor")
    {
        $(".hlcolor").css("color", color);
        $(".fmcolor").css("border-color", color);
    }
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

