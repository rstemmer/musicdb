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



class AlbumSettingsLayer extends Layer
{
    // background: Instance of the Curtain class that lays behind the Layer.
    // When the layer is made visible, then also the background will be shown
    constructor(background)
    {
        super(background, "AlbumSettingsLayer")

        // Headlines
        this.headline = new LayerHeadline("Album Settings",
            "This layer provides all information of an album stored in the MusicDB database.");

        // General Information
        this.currentalbumid = null;

        // Tool Bar
        this.toolbar     = new ToolBar();
        this.closebutton = new TextButton("Remove", "Close Layer",
            ()=>{this.onClose();},
            "Close album settings. Changes that have not been save will be discard.");

        this.toolbar.AddSpacer(true); // grow
        this.toolbar.AddButton(this.closebutton);
        this.toolbar.AddSpacer(true); // grow

        // Initialize UI
        this.ResetUI();
    }



    ResetUI()
    {
        this.RemoveChilds();

        this.AppendChild(this.headline);
        this.AppendChild(this.toolbar);
    }



    onClose()
    {
        this.Hide();
    }



    UpdateAlbumInformation(MDBAlbum)
    {
        this.currentalbumid = MDBAlbum.id;
    }



    UpdateAlbumTags(MDBTags)
    {
    }



    onMusicDBNotification(fnc, sig, rawdata)
    {
        this.artworkuploader?.onMusicDBNotification(fnc, sig, rawdata);
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        if(fnc == "GetAlbum" && sig == "ShowAlbumSettingsLayer")
        {
            this.ResetUI();
            this.UpdateAlbumInformation(args.album);
            this.UpdateAlbumTags(args.tags);
            this.Show();
        }
        else if(fnc == "GetAlbum" && sig == "UpdateTags")
        {
            if(this.currentalbumid === args.album.id)
                this.UpdateAlbumTags(args.tags);
        }

        this.artworkuploader?.onMusicDBMessage(fnc, sig, args, pass);
    }
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

