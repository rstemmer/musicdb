
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



    _UpdateWebUI()
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

            // Request update from server
            MusicDB_Request("GetAudioStreamState",          "UpdateHUD")
            MusicDB_Request("GetSongQueue",                 "ShowSongQueue");
            MusicDB_Request("GetFilteredArtistsWithAlbums", "ShowArtists");
        }
        else
        {
            // Update local HTML
            panels.dataset.panels        = "2";
            videopanel.dataset.visible   = "true";
            if(this.mainmenu)
                this.mainmenu.ForceEntryState(this.entryid, "b");

            // Request update from server
            MusicDB_Request("GetVideoStreamState",          "UpdateHUD");
            MusicDB_Request("GetVideoQueue",                "ShowVideoQueue");
            MusicDB_Request("GetFilteredArtistsWithVideos", "ShowArtists");
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
                this._UpdateWebUI();
            }
        }

        return;
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

