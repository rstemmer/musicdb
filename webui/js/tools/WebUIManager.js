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

class WebUIManager
{
    constructor()
    {
    }



    onWebSocketOpen()
    {
        MusicDB.Request("LoadWebUIConfiguration", "SetupWebUI");
        return;
    }



    onWebSocketClosed()
    {
        WebUI.GetLayer("WebSocketClosed").Show();
        return;
    }



    onWebSocketError()
    {
        WebUI.GetLayer("WebSocketError").Show();
        return;
    }



    onWatchdogBarks()
    {
        return;
    }



    onMusicDBNotification(fnc, sig, rawdata)
    {
        if(fnc == "MusicDB:AudioStream")
        {
            if(sig == "onStatusChanged")
            {
                MusicDB.Request("GetAudioStreamState", "UpdateStreamState");
            }
        }
        else if(fnc == "MusicDB:VideoStream")
        {
            if(sig == "onStatusChanged")
            {
                MusicDB.Request("GetVideoStreamState", "UpdateStreamState");
            }
            else if(sig == "onStreamNextVideo")
            {
                MusicDB.Request("GetVideoStreamState", "UpdateHUD");
            }
        }
        else if(fnc == "MusicDB:SongQueue")
        {
            if(sig == "onSongChanged")
            {
                MusicDB.Request("GetAudioStreamState", "UpdateStreamState");
            }
            else if(sig == "onSongQueueChanged")
            {
                MusicDB.Request("GetSongQueue", "ShowSongQueue");
            }
        }
        else if (fnc == "MusicDB:VideoQueue")
        {
            if(sig == "onVideoChanged")
            {
                MusicDB.Request("GetAudioStreamState", "UpdateStreamState");
            }
            else if(sig == "onVideoQueueChanged")
            {
                MusicDB.Request("GetVideoQueue", "ShowVideoQueue");
            }
        }

        return;
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        // Handle Messages form the server
        if(fnc == "LoadWebUIConfiguration" && sig == "SetupWebUI")
        {
            configuration = args;

            if(configuration.debug.blurartwork == true)
                document.documentElement.style.setProperty("--artworkfilter", "blur(5px)");

            MusicDB.Request("GetMDBState", "InitializeWebUI");
        }
        else if(sig == "UpdateConfig")
        {
            configuration = args;
        }
        else if(fnc == "GetMDBState" && sig == "InitializeWebUI")
        {
            if(args.audiostream.currentsong == null && args.videostream.currentvideo == null)
            {
                // All queues empty -> fresh install
                mainviewmanager.ShowWelcome();
            }

            let uimode = args.MusicDB.uimode;
            MusicDB.Request("GetArtists",  "UpdateArtistsCache");
            MusicDB.Request("GetTags",     "UpdateTagsCache");
            MusicDB.Request("GetMDBState", "UpdateMDBState");
            if(uimode == "audio")
            {
                MusicDB.Request("GetAudioStreamState",   "UpdateStreamState");
                MusicDB.Request("GetSongQueue",          "ShowSongQueue"); // Force Queue Update
            }
            else if(uimode == "video")
            {
                MusicDB.Request("GetVideoStreamState",   "UpdateStreamState");
                MusicDB.Request("GetVideoQueue",         "ShowVideoQueue"); // Force Queue Update
            }
        }
        else if(fnc=="sys:refresh" && sig == "UpdateCaches")    // TODO: Update (make uimode conform)
        {
            MusicDB.Request("GetTags",    "UpdateTagsCache");
            MusicDB.Request("GetArtists", "UpdateArtistsCache");
            MusicDB.Request("GetFilteredArtistsWithAlbums", "ShowArtists"); // Update artist view
        }

        return;
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

