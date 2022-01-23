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

class MDBModeManager
{
    constructor()
    {
        this.mode     = null;    // ! This variable should only be set as response to the server!
        this.entryid  = null;
        this.currentsongid  = -1;
        this.currentalbumid = -1;
        this.currentvideoid = -1;
    }



    GetCurrentMode()
    {
        return this.mode;
    }
    GetCurrentSongID()
    {
        return this.currentsongid;
    }
    GetCurrentAlbumID()
    {
        return this.currentalbumid;
    }
    GetCurrentVideoID()
    {
        return this.currentvideoid;
    }



    SetAudioMode()
    {
        MusicDB_Call("SetVideoStreamState", {state:"pause"});
        MusicDB_Request("SetMDBState", "UpdateMDBState",
            {category:"MusicDB", name:"uimode", value:"audio"});
        return;
    }

    SetVideoMode()
    {
        MusicDB_Call("SetAudioStreamState", {state:"pause"});
        MusicDB_Request("SetMDBState", "UpdateMDBState",
            {category:"MusicDB", name:"uimode", value:"video"});
        return;
    }



    _UpdateWebUI(MDBMusic)
    {
        // Show/Hide video panel
        let videopanel  = document.getElementById("VideoPanel");
        let panels      = document.getElementById("Panels");
        let mainmenu    = WebUI.GetLayer("MainMenu");

        if(this.mode == "audio")
        {
            // Update local HTML
            panels.dataset.panels        = "1";
            videopanel.dataset.visible   = "false";
            if(typeof mainmenu === "object")
                mainmenu.SwitchEntry("modeswitch", "a");

            // Request update from server
            MusicDB_Request("GetAudioStreamState",          "UpdateHUD")
            MusicDB_Request("GetSongQueue",                 "ShowSongQueue");
            MusicDB_Request("GetFilteredArtistsWithAlbums", "ShowArtists");
            // A fresh installed MusicDB may have no queue!
            if(MDBMusic !== null)
                MusicDB_Request("GetAlbum",                 "ShowAlbum", {albumid: MDBMusic.albumid});
        }
        else
        {
            // Update local HTML
            panels.dataset.panels        = "2";
            videopanel.dataset.visible   = "true";
            if(typeof mainmenu === "object")
                mainmenu.SwitchEntry("modeswitch", "b");

            // Request update from server
            MusicDB_Request("GetVideoStreamState",          "UpdateHUD");
            MusicDB_Request("GetVideoQueue",                "ShowVideoQueue");
            MusicDB_Request("GetFilteredArtistsWithVideos", "ShowArtists");
            // A fresh installed MusicDB may have no queue!
            if(MDBMusic !== null)
                MusicDB_Request("GetVideo",                 "ShowVideo", {videoid: MDBMusic.id});
        }

        // Update other elements
        WebUI.GetView("QueueControl").Update();
    }


    onMusicDBMessage(fnc, sig, args, pass)
    {
        if(fnc == "GetMDBState" && sig == "UpdateMDBState")
        {
            if(this.mode != args.MusicDB.uimode)
            {
                this.mode = args.MusicDB.uimode;

                let MDBMusic;
                if(this.mode == "audio")
                    MDBMusic = args.audiostream.currentsong;
                else if(this.mode == "video")
                    MDBMusic = args.videostream.currentvideo;
                else
                    MDBMusic = null;

                this._UpdateWebUI(MDBMusic);
            }
        }
        else if(fnc == "GetAudioStreamState")
        {
            // In rare cases the Queue can get empty.
            if(typeof args.song === "undefined" && typeof args.album === "undefined")
                return;

            this.currentsongid  = args.song.id;

            // New song playing. Update whole album if from different album. Otherwise update just the song.
            if(args.album.id != this.currentalbumid)
                MusicDB_Request("GetAlbum", "ShowAlbum", {albumid: args.album.id});
            else
                MusicDB_Request("GetSong", "UpdateSong", {songid: args.song.id});
        }
        else if(fnc == "GetVideoStreamState")
        {
            this.currentvideoid = args.video.id;
        }
        else if(fnc == "GetAlbum" && sig == "ShowAlbum")
        {
            this.currentalbumid = args.album.id;
        }

        return;
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

