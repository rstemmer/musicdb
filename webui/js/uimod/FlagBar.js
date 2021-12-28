// MusicDB,  a music manager with web-bases UI that focus on music.
// Copyright (C) 2017 - 2021  Ralf Stemmer <ralf.stemmer@gmx.net>
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

class FlagBar extends Element
{
    constructor(MDBMusic, moods, alignment="right")
    {
        super("div", ["FlagBar", "flex-row", "smallfont", "hlcolor"]);

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

        let ratiobar = new RatioBar(ratio, `${likes} / ${dislikes}`);

        this.AppendChild(ratiobar);
        return;
    }

    _AddProperties(MDBMusic)
    {
        // Set Property Flags
        let icon;
        if(MDBMusic.favorite == 1)
        {
            icon = new SVGIcon("Favorite2")
            icon.SetTooltip("Favorite");
            icon.SetColor("var(--color-gold)");
            this.AppendChild(icon);
        }
        if(MDBMusic.liverecording == 1)
        {
            icon = new SVGIcon("LiveRecording")
            icon.SetTooltip("Live Recording");
            this.AppendChild(icon);
        }
        if(MDBMusic.badaudio == 1)
        {
            icon = new SVGIcon("BadFile")
            icon.SetTooltip("Bad Audio");
            icon.SetColor("var(--color-red)");
            this.AppendChild(icon);
        }
        if(MDBMusic.lyricsvideo == 1)
        {
            icon = new SVGIcon("LyricsVideo")
            icon.SetTooltip("Lyrics Video");
            this.AppendChild(icon);
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
                this.AppendChild(flagelement);
            }
        }
        return;
    }



}




// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

