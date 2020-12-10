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

class FlagBar
{
    constructor(MDBMusic, moods, alignment="right")
    {
        this.element = document.createElement("div");
        this.element.classList.add("FlagBar");
        this.element.classList.add("flex-row");
        this.element.classList.add("smallfont");
        this.element.classList.add("hlcolor");

        if(alignment == "right")
        {
            this._AddMoodFlags(moods);
            this._AddProperties(MDBMusic);
            this._AddBarGraph(MDBMusic);
        }
        else
        {
            this._AddBarGraph(MDBMusic);
            this._AddProperties(MDBMusic);
            this._AddMoodFlags(moods);
        }
    }



    GetHTMLElement()
    {
        return this.element
    }


    // aka MDBTag
    _CreateMoodFlag({name, id, icon, icontype, color})
    {
        let flag = document.createElement("div");
        /*
         * mood.icontype:
         *      1: Unicode Character
         *      2: HTML code
         *      3: png \_ not yet specified in detail
         *      4: svg /
         *
         * mood.color: HTML color code or null
         */
        switch(icontype)
        {
            case 1:
                flag.innerText = icon;
                if(typeof color === "string")
                    flag.style.color = color;
                break;
        }
        flag.title = name;
        return flag;
    }



    _AddBarGraph(MDBMusic)
    {
        // Set Ratio Bar
        let likes    = MDBMusic.likes;
        let dislikes = MDBMusic.dislikes;
        let ratio;  // in %
        if(likes + dislikes == 0)
            ratio = null;
        else
            ratio = (likes / (likes + dislikes)) * 100;

        let ratiobar = new RatioBar(ratio);
        ratiobar.SetTooltip(`${likes} / ${dislikes}`);

        this.element.appendChild(ratiobar.GetHTMLElement());
        return;
    }

    _AddProperties(MDBMusic)
    {
        // Set Property Flags
        let icon;
        if(MDBMusic.favorite == 1)
        {
            icon = new SVGIcon("Favorite")
            icon.SetTooltip("Favorite");
            icon.SetColor("var(--color-gold)");
            this.element.appendChild(icon.GetHTMLElement());
        }
        if(MDBMusic.liverecording == 1)
        {
            icon = new SVGIcon("LiveRecording")
            icon.SetTooltip("Live Recording");
            this.element.appendChild(icon.GetHTMLElement());
        }
        if(MDBMusic.badaudio == 1)
        {
            icon = new SVGIcon("BadAudio")
            icon.SetTooltip("Bad Audio");
            icon.SetColor("var(--color-red)");
            this.element.appendChild(icon.GetHTMLElement());
        }
        if(MDBMusic.lyricsvideo == 1)
        {
            icon = new SVGIcon("LyricsVideo")
            icon.SetTooltip("Lyrics Video");
            this.element.appendChild(icon.GetHTMLElement());
        }
        return;
    }

    _AddMoodFlags(moods)
    {
        // Set Mood Flags
        // Iterate over all existing mood IDs and check which of them was set for this song
        let allmoods = tagmanager.GetMoods();
        let moodids  = moods.map(mood => mood.id); // List of IDs of set moods for this song
        for(let mood of allmoods)
        {
            if(moodids.indexOf(mood.id) >= 0 && mood.icon != null)
            {
                let flagelement = this._CreateMoodFlag(mood);
                this.element.appendChild(flagelement);
            }
        }
        return;
    }



}




// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

