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

        this.data     = null;   // The loaded data is stored in this variable
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
        if(this.type === FileType.Font)
            request.responseType = "arraybuffer";

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
        this.data = event.target.response;

        if(typeof this.loadedcallback === "function")
            this.loadedcallback(this);
    }
}



class ApplicationLoaderGUI
{
    constructor()
    {
        this.layer = document.createElement("div");
        this.layer.style.cssText += "position: absolute; top: 0; left: 0;";
        this.layer.style.cssText += "width: 100vw; height: 100vh; margin: 0; padding: 0;";
        this.layer.style.cssText += "display: flex; flex-direction: column; justify-content: space-around";
        this.layer.style.cssText += "background: #202020;";
        this.layer.style.cssText += "color: #C0C0C0; font-family: Sans-Serif;";
        this.layer.id = "LoadingProgressLayer";
        this.gui = document.createElement("div");

        this.layer.appendChild(this.gui);
        document.body.appendChild(this.layer);
    }

    CreateProgressBar(id, label=null)
    {
        if(label === null)
            label = id;

        let labelelement    = document.createElement("label");
        let progresselement = document.createElement("progress");
        progresselement.id  = id;
        progresselement.max = 100;
        progresselement.value = 0;
        labelelement.innerText = label;

        progresselement.style.cssText += "width: 40%; margin: 0.5rem;";
        labelelement.style.cssText    += "display: flex; flex-direction: column; justify-content: space-around";
        labelelement.style.cssText    += "width: 40%; padding-right: 2rem; text-align: right; display: inline-box;";

        let container= document.createElement("div");
        container.style.cssText += "display: flex;";
        container.appendChild(labelelement);
        container.appendChild(progresselement);
        
        this.gui.appendChild(container);
    }

    UpdateProgressBar(id, progress=null)
    {
        let progressbar = document.getElementById(id);
        if(typeof progress === "number")
            progressbar.value = progress * 100;
    }

    RemoveLoadingProgressLayer()
    {
        document.body.removeChild(this.layer);
    }
}



class ApplicationLoader extends ApplicationLoaderGUI
{
    constructor()
    {
        super();
        this.files = new Array();
        this.data  = new Object(); // Collection of data from data files. Key is the URL
    }


    // For MusicDB's WebUI filename and URL are the same
    // Order of call defines order of integration
    AddFile(filetype, url, name=null)
    {
        let file = new FileLoader(filetype, url, name);

        this.CreateProgressBar(url, name);
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

        this.files.push(file);
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



    AppendTag(tagname, data, callback)
    {
        const observerconfig = { attributes: true, childList: true, subtree: true };

        let tag      = document.createElement(tagname);
        let observer = new MutationObserver(()=>{callback();});
        observer.observe(tag, observerconfig);
        tag.textContent = data;
        document.body.appendChild(tag);
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
        else if(type === FileType.Font)
        {
            let fontface = new FontFace(name, data);
            fontface.load().then(
                (loadedfontface)=>
                {
                    document.fonts.add(loadedfontface);
                    this.onIntegrated(file);
                },
                (error)=>
                {
                    window.console?.error(error);
                });
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



    // callback gets this.data as argument
    SetExecutionCallback(callback)
    {
        this.onexecutecallback = callback;
    }
    Execute()
    {
        this.RemoveLoadingProgressLayer();
        if(typeof this.onexecutecallback === "function")
            this.onexecutecallback(this.data);
    }
}




// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

