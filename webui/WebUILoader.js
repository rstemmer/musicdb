// MusicDB,  a music manager with web-bases UI that focus on music.
// Copyright (C) 2017 - 2022  Ralf Stemmer <ralf.stemmer@gmx.net>
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


let SVGCACHE = null;
let FILELOADINGCOUNT = 0;

const FileType = {"Script":1, "Style":2, "Font":3, "Data":4};

class FileLoader
{
    // filetype must be an entry from FileType
    constructor(filetype, url, name=null)
    {
        this.type = filetype;
        this.url  = url;
        if(name)
            this.name = name;
        else
            this.name = url;

        this.data = null;   // The loaded data is stored in this variable
        this.progress = null;   // The current loading progress. [0.0 .. 1.0]

        this.progresscallback = null;
        this.loadedcallback   = null;
    }

    Load()
    {
        this.progress = 0.0;

        let request = new XMLHttpRequest();
        request.addEventListener("progress", (event)=>{this.onProgress(event);},   false);
        request.addEventListener("load",     (event)=>{this.onFileLoaded(event);}, false);
        request.open("GET", this.url);
        request.send();
    }


    SetProgressCallback(callback)
    {
        this.progresscallback = callback;
    }
    SetLoadedCallback(callback)
    {
        this.loadedcallback = callback;
    }



    onProgress(event)
    {
        if(event.lengthComputable)
            this.progress = event.loaded / event.total;
        if(typeof this.progresscallback === "function")
            this.progresscallback(this);
    }

    onFileLoaded(event)
    {
        this.data = event.target.responseText;
        if(typeof this.loadedcallback === "function")
            this.loadedcallback(this);
    }
}



class ApplicationLoaderGUI
{
    constructor()
    {
        this.gui = document.createElement("div");
        this.gui.style.cssText += "position: absolute; top: 0; left: 0;";
        this.gui.style.cssText += "width: 100vw; height: 100vh; margin: 0; padding: 0;";
        this.gui.style.cssText += "display: flex; flex-direction: column; background: #202020;";
        this.gui.style.cssText += "color: #C0C0C0; font-family: Sans-Serif;";
        this.gui.id = "LoadingProgressLayer";
        document.body.appendChild(this.gui);
    }

    CreateProgressBar(id, label=null)
    {
        if(label === null)
            label = id;

        let labelelement    = document.createElement("label");
        let progresselement = document.createElement("progress");
        progresselement.id  = `${filename}.Progress`;
        progresselement.max = 100;
        progresselement.value = 0;
        labelelement.innerText = `${filename}`;

        progresselement.style.cssText += "width: 40%;";
        labelelement.style.cssText    += "width: 40%; padding-right: 2rem; text-align: right; display: inline-box;";

        let container= document.createElement("div");
        container.style.cssText += "display: flex;";
        container.appendChild(labelelement);
        container.appendChild(progresselement);
        
        this.gui.appendChild(container);
    }

    UpdateProgressBar(id, progress=null)
    {
        let progressbar = document.getElementById(`${id}`);
        if(typeof progress === "number")
            progressbar.value = progress * 100;
    }

    RemoveLoadingProgressLayer()
    {
        document.body.removeChild(this.gui);
    }
}



class ApplicationLoader
{
    constructor()
    {
        super();
    }

    AppendTag(tagname, data, callback)
    {
        const observerconfig = { attributes: true, childList: true, subtree: true };

        let tag      = document.createElement(tagname);
        let observer = new MutationObserver(()=>{callback();});
        observer.observe(tag, observerconfig);
        tag.textContent = data;
        document.body.appendChild(tag);
    }
}



class WebUILoader extends ApplicationLoader, ApplicationLoaderGUI
{
    constructor()
    {
        super();
        this.files = new Array();
        this.data  = new Object(); // Collection of data from data files. Key is the URL
    }


    // For MusicDB's WebUI filename and URL are the same
    // Order of call defines order of integration
    AddFile(filetype, url)
    {
        let file = new FileLoader(filetype, url);

        this.CreateProgressBar(url);
        file.SetProgressCallback(
            (object)=>
            {
                this.UpdateProgressBar(object.url, object.progress);
            }
        );
        file.SetLoadedCallback(
            (object)=>
            {
                this.onLoaded(object);
            }
        );

        this.files.append(file);
    }


    Load()
    {
        for(let file of this.files)
            file.Load();
    }

    onLoaded(file)
    {
        // Check if all files have been loaded.
        // Return if not
        for(let file of this.files)
            if(file.data === null)
                return;

        // All files have been loaded.
        // Now it's time to integrate them
        this.IntegrateNextFile();
    }



    IntegrateNextFile()
    {
        let file = this.files.shift(); // pop first element
        let name = file.name;
        let type = file.type;
        let data = file.data;

        if(type === FileType.Data)
        {
            this.data[name] = data;
            this.onIntegrated(file);
        }
        else if(type === FileType.Script)
        {
            this.AppendTag("script", data, ()=>{this.onIntegrated(file);});
        }
        else if(type === FileType.Style)
        {
            this.AppendTag("style", data, ()=>{this.onIntegrated(file);});
        }
        else
        {
            window.console?.warn(`Unknown file ${name} loaded. Will be ignored!`);
            this.onIntegrated(file);
        }
    }

    onIntegrated(file)
    {
        if(this.files.length > 0)
        {
            this.IntegrateNextFile();
            return;
        }

        let timer = setTimeout(()=>{this.Execute();}, 1000);
    }



    Execute()
    {
        InitializeWebUI(this.data["WebUI.json"]);
        this.RemoveLoadingProgressLayer();
        ExecuteWebUI();  // Now WebUI can take over
    }
}



window.onload = function ()
{
    let webuiloader = new WebUILoader();
    // The order of AddFile calls defined the order of integrating its content
    webuiloader.AddFile(FileType.Data,   "WebUI.json");
    webuiloader.AddFile(FileType.Style,  "WebUI.css");
    webuiloader.AddFile(FileType.Script, "WebUI.js");
    webuiloader.Load();
}




// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

