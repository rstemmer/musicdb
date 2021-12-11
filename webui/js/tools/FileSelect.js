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

class FileSelect extends Element
{
    // content type: "video", "artwork"
    // annotations: an object with initial annotations
    constructor(labeltext, tooltip, icon, contenttype, accept, annotations=null)
    {
        super("label", ["FileSelect", "flex-row"]);

        this.input = document.createElement("input")
        this.input.type     = "file";
        this.input.accept   = accept;
        this.input.onchange = (event)=>{this.onFileSelected(event);};
        this.icon  = icon;
        this.text  = new Element("span");
        this.text.SetInnerText(labeltext);

        this.contenttype = contenttype;
        this.annotations = annotations;

        this.AddCSSClass("flex-row");
        this.SetTooltip(tooltip);

        this.AppendChild(this.icon);
        this.AppendChild(this.text);
        this.AppendChild(this.input);
    }



    onFileSelected(event)
    {
        let fileinfos = event.target.files[0];
        let name = fileinfos.name;
        let size = Math.ceil(fileinfos.size / (1024*1024)); // in MiB
        let type = fileinfos.type;
        let date = new Date(fileinfos.lastModified);

        window.console && console.log(fileinfos);
        window.console && console.log(name);
        window.console && console.log(size);
        window.console && console.log(type);
        window.console && console.log(date);

        // Start Upload
        uploadmanager.UploadFile(this.contenttype, fileinfos, this.annotations);

        // Update Label
        let newlabel = `${name}&nbsp;<span class="hlcolor">${size}&#8239;MiB</span>`;
        this.text.SetInnerHTML(newlabel);
    }
}



class DirectorySelect extends FileSelect
{
    constructor(labeltext, tooltip, icon, contenttype, accept, annotations=null)
    {
        super(labeltext, tooltip, icon, contenttype, accept, annotations);
        this.input.webkitdirectory = true;
    }



    onFileSelected(event)
    {
        let files = event.target.files;
        window.console?.log(files);

        // Calculate the sum of all file sized to get the total upload size
        let size  = 0;
        let count = 0;
        for(let file of files)
        {
            size  += Math.ceil(file.size / (1024*1024)); // in MiB
            count += 1;
        }

        // TODO: In Firefox, there is an object webkitRelativePath that holds "dirname/filename".
        // This can be used to annotate a potential album name.

        // Update Label
        let newlabel = `${count} Files <span class="hlcolor">${size}&#8239;MiB</span>`;
        this.text.SetInnerHTML(newlabel);

        // Trigger Upload
        for(let fileinfos of files)
        {
            uploadmanager.UploadFile(this.contenttype, fileinfos, this.annotations);
        }
    }
}



class VideoFileSelect extends FileSelect
{
    constructor(labeltext, tooltip)
    {
        super(labeltext, tooltip, new SVGIcon("VideoFile"), "video", "video/*");
    }
}



class ArtworkFileSelect extends FileSelect
{
    // Optional initial annotations. MusicDB requires a "musictype", "musicpath" and "musicid" for artworks
    constructor(labeltext, tooltip, initialannotations=null)
    {
        super(labeltext, tooltip, new SVGIcon("ArtworkFile"), "artwork", "image/*", initialannotations);
    }
}



class AlbumDirectorySelect extends DirectorySelect
{
    constructor(labeltext, tooltip)
    {
        super(labeltext, tooltip, new SVGIcon("MusicDB"), "album", "*");
    }
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

