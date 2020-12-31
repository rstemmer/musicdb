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
        super("VideoImport", "Upload and Import Videos");

        this.upload      = new FileSelect("Select Video", "Tooltip");
        this.uploadtable = new UploadTable();
        this.importtable = new VideoImportTable();
        this.element.appendChild(this.upload.GetHTMLElement());
        this.element.appendChild(this.uploadtable.GetHTMLElement());
        this.element.appendChild(this.importtable.GetHTMLElement());

        this.highlightupload = ""; // TODO: Highlight latest upload
    }



    UpdateView(newvideopaths, newvideouploads)
    {
        if(newvideopaths != null)
            this.importtable.Update(newvideopaths);
        if(newvideouploads != null)
            this.uploadtable.Update(newvideouploads);
        return;
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        if(fnc == "FindNewContent" && sig == "ShowVideoImport")
        {
            window.console && console.log(args.videos);
            this.UpdateView(args.videos, null);
        }
        else if(fnc == "GetUploads" && sig == "ShowUploads")
        {
            window.console && console.log(args);
            window.console && console.log(pass);
            if(pass != null)
                this.highlightupload = pass.lastuploadid;

            this.UpdateView(null, args.videos);
        }
        return;
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

