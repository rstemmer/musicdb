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
        super("AlbumImport", "Upload and Import new Albums", "Upload new albums into the Music Director and/or Import new albums form the Music Directory into the MusicDB Music Database.");

        this.directoryupload = new AlbumDirectorySelect("Select Album Directory", "Select an album directory from the local computer to start the upload process.");
        this.AppendChild(this.directoryupload);

        this.importheadline = new SettingsHeadline("New Albums Inside Music Directory",
            "This is a list of albums found inside the Music Directory that have not yet been imported into the MusicDB Music Database.");
        this.albumlist = new List("New Album Directories");
        this.AppendChild(this.importheadline);
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
        WebUI.ShowLayer("AlbumImport"); // Hand over to the overlay
        MusicDB_Request("FindAlbumSongFiles", "ShowAlbumImportLayer", {albumpath:albumpath});
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

