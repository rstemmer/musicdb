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


/*

// PLAYGROUND
let streamplayer        = new Element("audio");
streamplayer.GetHTMLElement().controls   = true;
streamplayer.GetHTMLElement().src        = "http://127.0.0.1:8000/stream";
mainmenu.AddSection("Stream Player", streamplayer);
//

*/

class AudioStreamPlayer extends Element
{
    constructor()
    {
        super("audio", ["AudioStreamPlayer"]);
        this.element.controls = "controls";
        this.element.preload  = "none";
        this.configuredurl    = null
    }



    Configure(url, username, password)
    {
        // If username and password are give, attach them to the URL
        if(username.length > 0 && password.length > 0)
            url = `${username}:${password}@${url}`;

        // Check if the URL changed. If not, return without touching the audio element
        if(this.configuredurl == url)
            return;

        // Update stream URL
        this.element.src   = url;
        this.configuredurl = url;
        return;
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        if(fnc == "LoadWebUIConfiguration" || sig == "UpdateConfig")
        {
            this.Configure(args.Stream.url, args.Stream.username, args.Stream.password);
        }

        return;
    }

}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

