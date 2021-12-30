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

        this.currentalbumid = null; // The album ID of the currently shown album songs

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
        this.closebutton = new TextButton("Remove", "Cancel and Discard",
            ()=>{this.onClose();},
            "Cancel album import. Nothing will be changed.");
        this.renamebutton = new TextButton("RenameFile", "Update Song",
            ()=>{this.onClose();},
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
        this.currentalbumid = null;
        this.Hide();
    }

    onSongFilesValidation(isvalid)
    {
    }


    UpdateSongsInformation(MDBArtist, MDBAlbum, MDBCDs)
    {
        this.currentalbumid = MDBAlbum.id;
        this.albumheadline.UpdateInformation(MDBAlbum, MDBArtist)

        this.songfilestable.Update(MDBAlbum, MDBCDs);
    }



    //onMusicDBNotification(fnc, sig, rawdata)
    //{
    //}



    onMusicDBMessage(fnc, sig, args, pass)
    {
        if(fnc == "GetAlbum" && sig == "ShowSongsSettingsLayer")
        {
            window.console?.log(args);
            this.ResetUI();
            this.UpdateSongsInformation(args.artist, args.album, args.cds);
            this.Show();
        }
        else if(fnc == "GetAlbum" && sig == "AlbumRenamed")
        {
            //if(this.currentalbumid === args.album.id)
        }
        else if(fnc == "GetAlbum" && sig == "UpdateTags")
        {
            //if(this.currentalbumid === args.album.id)
        }
    }
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

