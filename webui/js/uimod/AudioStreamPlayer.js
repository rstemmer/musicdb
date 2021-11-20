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


class AudioStreamPlayer extends AudioPlayer
{
    constructor()
    {
        super(null, ["AudioStreamPlayer"]);
        this.configuredurl = null
    }



    Configure(url, username, password)
    {
        // If username and password are give, attach them to the URL
        if(username.length > 0 && password.length > 0)
        {
            // The format is ${Protocol}://${Username}:${Password}@${Address}
            // So first the protocol must be separated from the URL
            let protocol = url.substring(0, url.indexOf(":"));
            let address  = url.substring(url.indexOf(":")+3); // Skip "://"
            password = encodeURIComponent(password);
            username = encodeURIComponent(username);
            address  = encodeURI(address);

            url = `${protocol}://${username}:${password}@${address}`;
        }
        else
        {
            url = encodeURI(url);
        }

        // Check if the URL changed. If not, return without touching the audio element
        if(this.configuredurl == url)
            return;

        // Update stream URL
        this.SetSource(url);
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

