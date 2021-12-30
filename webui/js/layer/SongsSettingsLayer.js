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



class SongsSettingsLayer extends Layer
{
    // background: Instance of the Curtain class that lays behind the Layer.
    // When the layer is made visible, then also the background will be shown
    constructor(background)
    {
        super(background, "SongsSettingsLayer")

        this.currentalbum = null; // The album ID of the currently shown album songs

        // Headlines
        this.albumheadline = new MainViewHeadline();
        this.mainheadline  = new LayerHeadline("Songs Settings",
            "This layer provides all information of all songs of an album stored in the MusicDB database.");

        // Forms
        this.songfilestable = new SongFilesTableFromDatabase((isvalid)=>{this.onSongFilesValidation(isvalid);});

        // Tool Bar
        this.toolbar     = new ToolBar();
        //this.closebutton = new TextButton("Remove", "Close Layer",
        //    ()=>{this.onClose();},
        //    "Close songs settings.");
        this.closebutton = new TextButton("Remove", "Close and Discard",
            ()=>{this.onClose();},
            "Cancel album import. Nothing will be changed.");
        this.renamebutton = new TextButton("RenameFile", "Update Song",
            ()=>{this.onRename();},
            "Renames the song files and updates the database entries of all edited songs.");

        //this.toolbar.AddSpacer(true); // grow
        this.toolbar.AddButton(this.closebutton);
        this.toolbar.AddSpacer(true); // grow
        this.toolbar.AddButton(this.renamebutton);

        // Initialize UI
        this.ResetUI();
    }


    //let songrenamerequests  = this.songfilestable.GetRenameRequests();

    ResetUI()
    {
        this.RemoveChilds();

        this.AppendChild(this.albumheadline);
        this.AppendChild(this.mainheadline);
        this.AppendChild(this.songfilestable);
        this.AppendChild(this.toolbar);
    }



    onClose()
    {
        this.currentalbum = null;
        this.Hide();
    }

    onRename()
    {
        let albumid            = this.currentalbum.id;
        let albumpath          = this.currentalbum.path;
        let songrenamerequests = this.songfilestable.GetRenameRequests();

        for(let request of songrenamerequests)
        {
            let oldpath  = albumpath + "/" + request.oldname;
            let newpath  = albumpath + "/" + request.newname;
            MusicDB_Request("RenameMusicFile", "ConfirmSongRenaming", {oldpath: oldpath, newpath: newpath});
        }

        MusicDB_Broadcast("GetAlbum", "SongRenamed", {albumid: albumid}); // Tell all clients that the songs of an album got renamed
    }

    onSongFilesValidation(isvalid)
    {
        if(isvalid)
            this.renamebutton.Enable();
        else
            this.renamebutton.Disable();
    }


    UpdateSongsInformation(MDBArtist, MDBAlbum, MDBCDs)
    {
        this.currentalbum = MDBAlbum;
        this.albumheadline.UpdateInformation(MDBAlbum, MDBArtist)

        this.songfilestable.Update(MDBAlbum, MDBCDs);
    }



    //onMusicDBNotification(fnc, sig, rawdata)
    //{
    //}



    onMusicDBMessage(fnc, sig, args, pass)
    {
        if(fnc == "GetAlbum")
        {
            // Initialize and show layer
            if(sig == "ShowSongsSettingsLayer")
            {
                window.console?.log(args);
                this.ResetUI();
                this.UpdateSongsInformation(args.artist, args.album, args.cds);
                this.Show();
            }

            // If there are news from an album currently shown, continue…
            if(this.currentalbum?.id !== args.album.id)
                return;

            // Update layer
            if(sig == "SongRenamed" || sig == "AlbumRenamed")
            {
                this.ResetUI();
                this.UpdateSongsInformation(args.artist, args.album, args.cds);
            }
        }
        else if(fnc == "GetAlbum" && sig == "UpdateTags")
        {
            //if(this.currentalbum.id === args.album.id)
        }
    }
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

