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



class AlbumIntegrationLayer extends Layer
{
    // background: Instance of the Curtain class that lays behind the Layer.
    // When the layer is made visible, then also the background will be shown
    constructor(background, id)
    {
        super(background, id)

        // Headlines
        this.albumheadline = new LayerHeadline("Album Directory Settings",
            "These settings can be used to initialize the naming of the Album and to define to which Artist the Album belongs. "+
            "These settings can also be updated after the upload is complete. "+ 
            "After integrating the uploaded album, the path follows the MusicDB Naming Scheme for Albums: "+
            "\"{ArtistName}/{ReleaseYear} - {AlbumName}\"");

        // Forms
        this.albumsettingstable = new AlbumSettingsTable((isvalid)=>{this.onAlbumSettingsValidation(isvalid);});

        // Tool Bar
        this.toolbar            = new ToolBar();
        this.cancelbutton       = new TextButton("MusicDB", "Cancel and Discard",
            ()=>{this.onClick_Cancel();},
            "Cancel album integration. Nothing will be changed inside the Music directory. Uploaded data will be removed.");
        this.integratebutton    = new TextButton("MusicDB", "Integrate Album",
            ()=>{this.onClick_Integrate();},
            "Apply some renaming and stores the uploaded files inside the Music dicretory. After integration the album can be imported into MusicDB.");

        this.toolbar.AddButton(this.cancelbutton);
        this.toolbar.AddSpacer(true); // grow
        this.toolbar.AddButton(this.integratebutton);

        this.ResetUI();
    }



    ResetUI()
    {
        this.RemoveChilds();
        this.AppendChild(this.albumheadline);
        this.AppendChild(this.albumsettingstable);
        this.AppendChild(this.toolbar);
    }



    onClick_Cancel()
    {
        this.Hide();
    }

    onClick_Integrate()
    {
        this.Hide();
    }



    onAlbumSettingsValidation(isvalid)
    {
        //this.PrepareImportTasks();

        if(isvalid)
            this.integratebutton.Enable();
        else
            this.integratebutton.Disable();
    }



    onMusicDBNotification(fnc, sig, rawdata)
    {
        if(fnc == "MusicDB:Task")
        {
            let task  = rawdata.task;
            let state = rawdata.state;

            if(state == "notexisting")
                return;
            //if(this.listenontaskid !== task.id)
            //    return;
            // FIXME: May be a different file than a song file
            // FIXME: Check if this belongs to the expected album
            if(state == "readyforintegration")
            {
                window.console?.log("Updating integration album settings table");
                let artistname  = task.annotations.artist;
                let albumname   = task.annotations.album;
                let releaseyear = task.annotations.releaseyear;
                this.albumsettingstable.Update(artistname, albumname, releaseyear);
            }

            if(sig == "StateUpdate")
                return;
            else if(sig == "InternalError")
                return;
        }
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
    }
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

