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


class AlbumImportLayer extends Layer
{
    // background: Instance of the Curtain class that lays behind the Layer.
    // When the layer is made visible, then also the background will be shown
    constructor(background, id)
    {
        super(background, id)

        this.albumsettingstable = new AlbumSettingsTable();
        this.songfilestable     = new SongFilesTable();

        this.toolbar            = new ToolBar();
        this.cancelbutton       = new TextButton("MusicDB", "Cancel",
            ()=>{this.onClick_Cancel();},
            "Cancel album import. Nothing will be changed. ");
        this.renamebutton       = new TextButton("MusicDB", "Rename",
            ()=>{this.onClick_Rename();},
            "Apply changes and rename files and directories accordingly.");

        this.toolbar.AddButton(this.cancelbutton);
        this.toolbar.AddSpacer(true); // grow
        this.toolbar.AddButton(this.renamebutton);

        this.AppendChild(this.albumsettingstable);
        this.AppendChild(this.songfilestable);
        this.AppendChild(this.toolbar);
    }



    onClick_Cancel()
    {
        this.Hide();
    }

    onClick_Rename()
    {
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        if(fnc == "FindAlbumSongFiles" && sig == "ShowAlbumSongFiles")
        {
            window.console?.log(args);
            let albumpath = args[0].path.split("/").slice(0,2).join("/");
            this.albumsettingstable.Update(
                args[0].artistname,
                args[0].albumname,
                args[0].releaseyear,
                args[0].origin,
                args[0].hasartwork,
                args[0].haslyrics,
                albumpath);
            this.songfilestable.Update(args);
        }
    }
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

