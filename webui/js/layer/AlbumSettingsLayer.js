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
        this.mainheadline = new LayerHeadline("Album Settings",
            "This layer provides all information of an album stored in the MusicDB database.");
        this.tagsheadline = new LayerHeadline("Album Tags",
            "Update the tags associated to this album. Add and remove genre and sub-genre tags.");
        this.artworkheadline = new LayerHeadline("Album Artwork",
            "Upload a new album cover and change the color theme associated to this album.");

        // General Information
        this.currentalbumid = null;

        // Controls
        this.albumsettings  = new AlbumEntrySettingsTable((isvalid)=>{this.onAlbumPathValidation(isvalid);});
        this.artworksettings= new Element("div", ["artworksettings", "flex", "flex-row"]); // color | artwork
        this.colorsettings  = new Element("div", ["colorsettings", "flex", "flex-column"]); // Uploader and color settings
        this.artworkuploader= null;
        this.albumartwork   = null;
        this.genreedit      = null;
        this.subgenreedit   = null;

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



    onAlbumPathValidation(isvalid)
    {
    }



    ResetUI()
    {
        this.RemoveChilds();

        this.genreedit      = new TagListEdit("genre");
        this.subgenreedit   = new TagListEdit("subgenre");

        this.AppendChild(this.mainheadline);
        this.AppendChild(this.albumsettings);
        this.AppendChild(this.tagsheadline);
        this.AppendChild(this.genreedit);
        this.AppendChild(this.subgenreedit);
        this.AppendChild(this.artworkheadline);
        this.AppendChild(this.artworksettings);
        this.AppendChild(this.toolbar);
    }



    onClose()
    {
        this.currentalbumid = null;
        this.Hide();
    }



    UpdateAlbumInformation(MDBArtist, MDBAlbum)
    {
        this.currentalbumid = MDBAlbum.id;

        this.artworkuploader= new ArtworkUploader("album", MDBAlbum.path, MDBAlbum.id);
        this.colorselect    = new ColorSchemeSelection("audio", this.currentalbumid);
        this.colorselect.SetColors(MDBAlbum.bgcolor, MDBAlbum.fgcolor, MDBAlbum.hlcolor);
        this.colorsettings.RemoveChilds();
        this.colorsettings.AppendChild(this.artworkuploader);
        this.colorsettings.AppendChild(this.colorselect);
        this.albumartwork   = new AlbumArtwork(MDBAlbum, "large");
        this.artworksettings.RemoveChilds();
        this.artworksettings.AppendChild(this.colorsettings);
        this.artworksettings.AppendChild(this.albumartwork);

        this.albumsettings.Update(MDBArtist, MDBAlbum);
    }



    UpdateAlbumTags(MDBTags)
    {
        this.genreedit.Update(   "album", this.currentalbumid, MDBTags);
        this.subgenreedit.Update("album", this.currentalbumid, MDBTags);
    }



    onWebSocketClosed()
    {
        this.albumsettings?.tasks?.onConnectionLost();
    }
    onWebSocketError()
    {
        this.albumsettings?.tasks?.onConnectionLost();
    }
    onWatchdogBarks()
    {
        this.albumsettings?.tasks?.onConnectionLost();
    }
    onWebSocketOpen()
    {
        this.albumsettings?.tasks?.onReconnect();
    }



    onMusicDBNotification(fnc, sig, rawdata)
    {
        this.artworkuploader?.onMusicDBNotification(fnc, sig, rawdata);
        this.albumsettings?.onMusicDBNotification(fnc, sig, rawdata);
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        if(fnc == "GetAlbum")
        {
            // Initialize and show layer
            if(sig == "ShowAlbumSettingsLayer")
            {
                this.ResetUI();
                this.UpdateAlbumInformation(args.artist, args.album);
                this.UpdateAlbumTags(args.tags);
                this.Show();
            }

            // If there are news from an album currently shown, continue…
            if(this.currentalbumid === args.album.id)
            {
                // Update layer
                if(sig == "SongRenamed" || sig == "AlbumRenamed")
                    this.albumsettings.Update(args.artist, args.album);
                else if(sig == "UpdateTags")
                    this.UpdateAlbumTags(args.tags);
            }
        }

        this.artworkuploader?.onMusicDBMessage(fnc, sig, args, pass);
        this.albumsettings?.onMusicDBMessage(fnc, sig, args, pass);
    }
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

