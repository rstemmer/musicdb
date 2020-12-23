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

class MDBModeManager
{
    constructor()
    {
        this.mode     = null;    // ! This variable should only be set as response to the server!
        this.mainmenu = null;
        this.entryid  = null;
    }



    GetCurrentMode()
    {
        return this.mode;
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



    SetMainMenuHandler(mainmenu, entryid)
    {
        window.console && console.log("Entry ID: " + entryid);
        this.mainmenu = mainmenu;
        this.entryid  = entryid;
    }



    _UpdateWebUI(MDBMusic)
    {
        // Show/Hide video panel
        let videopanel  = document.getElementById("VideoPanel");
        let panels      = document.getElementById("Panels");

        if(this.mode == "audio")
        {
            // Update local HTML
            panels.dataset.panels        = "1";
            videopanel.dataset.visible   = "false";
            if(this.mainmenu)
                this.mainmenu.ForceEntryState(this.entryid, "a");

            // Update view
            mainviewmanager.MountView(albumview);

            // Request update from server
            MusicDB_Request("GetAudioStreamState",          "UpdateHUD")
            MusicDB_Request("GetSongQueue",                 "ShowSongQueue");
            MusicDB_Request("GetFilteredArtistsWithAlbums", "ShowArtists");
            // A fresh installes MusicDB may have no queue!
            if(MDBMusic !== null)
                MusicDB_Request("GetAlbum",                 "ShowAlbum", {albumid: MDBMusic.albumid});
        }
        else
        {
            // Update local HTML
            panels.dataset.panels        = "2";
            videopanel.dataset.visible   = "true";
            if(this.mainmenu)
                this.mainmenu.ForceEntryState(this.entryid, "b");

            // Update view
            mainviewmanager.MountView(videoview);

            // Request update from server
            MusicDB_Request("GetVideoStreamState",          "UpdateHUD");
            MusicDB_Request("GetVideoQueue",                "ShowVideoQueue");
            MusicDB_Request("GetFilteredArtistsWithVideos", "ShowArtists");
            // A fresh installes MusicDB may have no queue!
            if(MDBMusic !== null)
                MusicDB_Request("GetVideo",                 "ShowVideo", {videoid: MDBMusic.id});
        }


        // Update other elements
        queuecontrolview.Update();
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

        return;
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

