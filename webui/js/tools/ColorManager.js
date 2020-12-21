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

class ColorManager
{
    constructor()
    {
        this.fgcolor = "#181819";
        this.hlcolor = "#777799";
        this.bgcolor = "#777799";
    }



    UpdateColor(fgcolor=null, hlcolor=null, bgcolor=null)
    {
        this.fgcolor = fgcolor || this.fgcolor;
        this.hlcolor = hlcolor || this.hlcolor;
        this.bgcolor = bgcolor || this.bgcolor;

        document.documentElement.style.setProperty("--fgcolor", this.fgcolor);
        document.documentElement.style.setProperty("--hlcolor", this.hlcolor);
        document.documentElement.style.setProperty("--bgcolor", this.bgcolor);
        document.documentElement.style.setProperty("--fmcolor", this.hlcolor);
    }



    GetFGColor()
    {
        return this.fgcolor;
    }
    GetHLColor()
    {
        return this.hlcolor;
    }
    GetBGColor()
    {
        return this.bgcolor;
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        if(fnc == "GetVideo" && sig == "ShowVideo")
        {
            this.UpdateColor(args.video.fgcolor, args.video.hlcolor, args.video.bgcolor);
        }
        else if(fnc == "GetAlbum" && sig == "ShowAlbum")
        {
            this.UpdateColor(args.album.fgcolor, args.album.hlcolor, args.album.bgcolor);
        }

        return;
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

