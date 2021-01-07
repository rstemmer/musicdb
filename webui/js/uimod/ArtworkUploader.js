// MusicDB,  a music manager with web-bases UI that focus on music.
// Copyright (C) 2017-2021  Ralf Stemmer <ralf.stemmer@gmx.net>
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


class ArtworkUploader extends Element
{
    constructor(artistname, albumname, albumid)
    {
        super("div", ["ArtworkUploader", "flex-column", "flex-grow"]);

        let annotations = new Object();
        annotations["artistname"] = artistname;
        annotations["albumname" ] = albumname;
        annotations["albumid"   ] = albumid;

        this.fileselect = new ArtworkFileSelect("Select Artwork File", "Select an artwork file (.jpg) form your local computer.", annotations);
        let  statustext = new StatusText(); // Empty UploadStatusText as place holder
        this.element.appendChild(this.fileselect.GetHTMLElement());
        this.element.appendChild(statustext.GetHTMLElement());
    }



    UpdateUploadStatus(uploadstatus)
    {
        this.element.innerHTML = "";
        this.element.appendChild(this.fileselect.GetHTMLElement());
        let  statustext = new UploadStatusText(uploadstatus);
        this.element.appendChild(statustext.GetHTMLElement());
    }
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

