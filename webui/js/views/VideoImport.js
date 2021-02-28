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

class VideoImport extends MainSettingsView
{
    constructor()
    {
        super("VideoImport", "Upload New Videos", "Upload video files to import them into the MusicDB database. Uploaded files are listed in the table within this section.");

        // Upload Section
        this.upload      = new VideoFileSelect("Select Video File", "Select a video file from the local computer");
        this.uploadtable = uploadmanager.GetVideoUploadsTable();
        this.importtable = new VideoImportTable();
        this.element.appendChild(this.upload.GetHTMLElement());
        this.element.appendChild(this.uploadtable.GetHTMLElement());

        // Import Section
        let importheadline = new SettingsHeadline("Import Existing Videos", "Import videos that have bin found in the music collection but is not yet available in the database.");
        this.element.appendChild(importheadline.GetHTMLElement());
        this.element.appendChild(this.importtable.GetHTMLElement());
    }



    UpdateView(newvideopaths)
    {
        if(newvideopaths != null)
            this.importtable.Update(newvideopaths);
        return;
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        if(fnc == "FindNewContent" && sig == "ShowVideoImport")
        {
            window.console && console.log(args.videos);
            this.UpdateView(args.videos);
        }
        return;
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

