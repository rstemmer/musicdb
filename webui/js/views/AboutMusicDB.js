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
        this.logo           = document.createElement("img");
        this.logo.src       = "img/mdblogo-dark.svg";

        this.headline       = this._CreateHeadline("h1", "MusicDB");

        // Version Information
        this.versionheadline= this._CreateHeadline("h2", "Version");
        this.versions       = new Grid(2, 2);
        this.versions.InsertText(0, 0, "MusicDB");
        this.versions.InsertText(1, 0, MUSICDB_VERSION);
        this.versions.InsertText(0, 1, "WebUI");
        this.versions.InsertText(1, 1, WEBUI_VERSION);

        this.button         = document.createElement("button");
        this.button.innerText= "Check for Updates";
        this.button.title   = "Compares the VERSION file on GitHub with the Installed MusicDB Version";
        this.button.onclick = ()=>{this.CheckForUpdate();};

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
        this.element.appendChild(this.button);
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
        request.open("GET", "http://127.0.0.1/musicdb/webui/moderator.html", true /*Async*/);
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
        window.console && console.log(versionfile);
        versionfile  = "";
        versionfile += "7.0.0 - SEE CHANGELOG";
        versionfile += "6.0.0 - SEE CHANGELOG";
        versionfile += "5.2.2 - [artwork] Fixed wrong interpretation of relative path arguments";
    }

    onMusicDBMessage(fnc, sig, args, pass)
    {
        return;
    }

}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

