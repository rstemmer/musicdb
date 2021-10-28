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

class AlbumImport extends MainSettingsView
{
    constructor()
    {
        super("AlbumImport", "Import new Albums", "Import new found albums into the MusicDB Music Database. To find new albums, they must be uploaded into the Music Directory managed by MusicDB.");

        this.directoryupload = new AlbumDirectorySelect("Select Album Directory", "Select an album directory from the local computer");
        this.AppendChild(this.directoryupload);

        this.albumlist = new List();
        this.AppendChild(this.albumlist);
    }



    UpdateView(newalbumpaths)
    {
        if(newalbumpaths == null)
            return;

        this.albumlist.Clear();
        for(let newalbum of newalbumpaths)
        {
            window.console?.log(newalbum);
            let entry = new ListEntry();
            entry.SetInnerText(newalbum.path);
            entry.SetClickEventCallback((event)=>{this.ImportAlbum(newalbum.path);});
            this.albumlist.AddEntry(entry);
        }
        return;
    }



    ImportAlbum(albumpath)
    {
        albumimportlayer.Show(); // Hand over to the overlay
        MusicDB_Request("FindAlbumSongFiles", "ShowAlbumSongFiles", {albumpath:albumpath});
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        if(fnc == "FindNewContent" && sig == "ShowAlbumImport")
        {
            this.UpdateView(args.albums);
        }
        return;
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

