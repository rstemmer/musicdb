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
    constructor(labeltext, tooltip)
    {
        super("label", ["FileSelect", "flex-row"]);

        this.input = document.createElement("input")
        this.input.type     = "file";
        this.input.onchange = (event)=>{this.onFileSelected(event);};
        this.icon  = new SVGIcon("VideoFile");  // TODO: Move to constructor
        this.text  = document.createElement("span");
        this.text.innerText = labeltext;

        this.element.classList.add("flex-row");
        this.element.title = tooltip;
        this.element.appendChild(this.icon.GetHTMLElement());
        this.element.appendChild(this.text);
        this.element.appendChild(this.input);
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

        // Start Upload (TODO: Move to dedicated button)
        uploadmanager.UploadFile("video", fileinfos);

        // Update Label
        let newlabel = `${name} <span class="hlcolor">${size}&#8239;MiB</span>`;
        this.text.innerHTML = newlabel;
    }
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

