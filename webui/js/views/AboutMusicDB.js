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

// The following two constants were automatically generated during the installation process!
const MUSICDB_VERSION = "7.0.0";
const WEBUI_VERSION = "3.0.0";

class AboutMusicDB
{
    constructor()
    {
        this.major          = parseInt(MUSICDB_VERSION.split(".")[0]);
        this.minor          = parseInt(MUSICDB_VERSION.split(".")[1]);
        this.patch          = parseInt(MUSICDB_VERSION.split(".")[2]);

        this.logo           = document.createElement("img");
        this.logo.src       = "img/mdblogo-dark.svg";

        this.headline       = this._CreateHeadline("h1", "MusicDB");

        // Version Information
        this.versionheadline= this._CreateHeadline("h2", "Version");
        this.versions       = new Grid(3, 3);
        this.versions.InsertText(0, 0, "MusicDB");
        this.versions.InsertText(1, 0, MUSICDB_VERSION);
        this.versions.InsertText(0, 1, "WebUI");
        this.versions.InsertText(1, 1, WEBUI_VERSION);

        this.button         = document.createElement("button");
        this.button.innerText= "Check for Updates";
        this.button.title   = "Compares the VERSION file on GitHub with the Installed MusicDB Version";
        this.button.onclick = ()=>{this.CheckForUpdate();};

        this.versions.MergeRow(2);
        this.versions.InsertElement(0, 2, this.button);

        // Online Information
        this.linksheadline  = this._CreateHeadline("h2", "Links");
        this.links          = new Grid(2, 6);
        this.links.InsertText(0, 0, "Developer");
        this.links.InsertLink(1, 0, "Ralf Stemmer", "https://github.com/rstemmer", "_blank");
        this.links.InsertText(0, 1, "Website");
        this.links.InsertLink(1, 1, "rstemmer.github.io/musicdb", "https://rstemmer.github.io/musicdb/", "_blank");
        this.links.InsertText(0, 2, "Documentation");
        this.links.InsertLink(1, 2, "rstemmer.github.io/musicdb/build/html/index.html", "https://rstemmer.github.io/musicdb/build/html/index.html", "_blank");
        this.links.InsertText(0, 3, "Source Code");
        this.links.InsertLink(1, 3, "github.com/rstemmer/musicdb", "https://github.com/rstemmer/musicdb", "_blank");
        this.links.InsertText(0, 4, "Bug Reports");
        this.links.InsertLink(1, 4, "github.com/rstemmer/musicdb/issues", "https://github.com/rstemmer/musicdb/issues", "_blank");
        this.links.InsertText(0, 5, "Twitter");
        this.links.InsertLink(1, 5, "@MusicDBProject", "https://twitter.com/musicdbproject", "_blank");


        // Create Video View
        this.element  = document.createElement("div");
        this.element.classList.add("AboutMusicDB");
        this.element.appendChild(this.logo);
        this.element.appendChild(this.headline);
        this.element.appendChild(this.versionheadline);
        this.element.appendChild(this.versions.GetHTMLElement());
        //this.element.appendChild(this.button);
        this.element.appendChild(this.linksheadline);
        this.element.appendChild(this.links.GetHTMLElement());
    }



    _CreateHeadline(style, text)
    {
        let headline           = document.createElement(style);
        let headlinetext       = document.createElement("span");
        headlinetext.innerText = text;
        headline.appendChild(headlinetext);
        return headline;
    }

    GetHTMLElement()
    {
        return this.element;
    }



    CheckForUpdate()
    {
        let request = new XMLHttpRequest();
        request.open("GET", "https://raw.githubusercontent.com/rstemmer/musicdb/master/VERSION", true /*Async*/);
        request.send(null);
        request.onreadystatechange = ()=>
            {
                if(request.readyState === 4 && request.status === 200)
                {
                    let type = request.getResponseHeader("Content-Type");
                    if(type.indexOf("text") !== 1)
                    {
                        this.onMasterVersionFileReceived(request.responseText);
                    }
                }
            }
        return;
    }

    onMasterVersionFileReceived(versionfile)
    {
        let firstline     = versionfile.split("\n")[0];
        let versionnumber = firstline.split(" ")[0];
        let major         = parseInt(versionnumber.split(".")[0]);
        let minor         = parseInt(versionnumber.split(".")[1]);
        let patch         = parseInt(versionnumber.split(".")[2]);

        let updaterequired = false;
        if(this.major < major)
            updaterequired = true;
        else if(this.major == major)
        {
            if(this.minor < minor)
                updaterequired = true;
            else if(this.minor == minor)
            {
                if(this.patch < patch)
                    updaterequired = true;
            }
        }

        let latestversion = document.createElement("span");
        latestversion.innerText = versionnumber;
        latestversion.classList.add("latestversion");
        latestversion.dataset.updaterequired = updaterequired;

        let message = document.createElement("div")
        message.classList.add("versionmessage");
        message.dataset.updaterequired = updaterequired;
        if(updaterequired)
            message.innerText = "Update Recommended";
        else
            message.innerText = "Latest Version Installed";

        // Show latest version and hide "check for update" button
        this.versions.InsertElement(2, 0, latestversion);
        this.versions.InsertElement(0, 2, message);
    }

    onMusicDBMessage(fnc, sig, args, pass)
    {
        return;
    }

}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

