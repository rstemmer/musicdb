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
    constructor(appname, color)
    {
        this.layer = document.createElement("div");
        this.layer.style.cssText += "position: absolute; top: 0; left: 0;";
        this.layer.style.cssText += "width: 100vw; height: 100vh; margin: 0; padding: 0;";
        this.layer.style.cssText += "display: flex; flex-direction: row; justify-content: space-around";
        this.layer.style.cssText += "background: #202020;";
        this.layer.style.cssText += "font-family: Sans-Serif;";
        this.layer.id = "LoadingProgressLayer";

        this.box = document.createElement("div");
        this.box.style.cssText    += "display: flex; flex-direction: column; justify-content: space-around";
        this.box.style.cssText    += "position: relative";

        this.name = document.createElement("span");
        this.name.innerText = appname;
        this.name.style.cssText    += "letter-spacing: 0.1ch; font-size: 10rem; font-weight: bold;";
        this.name.style.cssText    += "color: #404040;";
        this.name.style.cssText    += "border-bottom: 0.5rem solid;";
        this.name.style.cssText    += "transition: width 0.1s linear;";

        this.bar = this.name.cloneNode(true);
        this.bar.style.cssText   += "position: absolute; overflow: hidden; left: 0;";
        this.bar.style.cssText   += "color: #C0C0C0;";
        this.bar.style.cssText   += "width: 0;";
        this.bar.style.cssText   += `background: ${color}; -webkit-background-clip: text; -webkit-text-fill-color: transparent;`;

        // Put everything together
        this.box.appendChild(this.name);
        this.box.appendChild(this.bar);
        this.layer.appendChild(this.box);
        document.body.appendChild(this.layer);

        this.progresscache = new Object(); // Keep track of all progresses
    }

    CreateProgress(id)
    {
        this.progresscache[id] = 0;
    }

    UpdateProgress(id, progress=null)
    {
        if(typeof progress === "number")
            this.progresscache[id] = progress;
        this.UpdateLoadingProgressLayer();
    }


    UpdateLoadingProgressLayer()
    {
        let maxprogress = 0;
        let currentprogress = 0;
        for(let id in this.progresscache)
        {
            maxprogress += 1;
            let progress = this.progresscache[id];
            if(typeof progress === "number")
                currentprogress += progress;
        }

        let percentage = (currentprogress/maxprogress)*100;
        this.bar.style.width = `${percentage}%`;
    }

    RemoveLoadingProgressLayer()
    {
        document.body.removeChild(this.layer);
    }
}



class ApplicationLoader extends ApplicationLoaderGUI
{
    constructor(appname, color="white")
    {
        super(appname, color);
        this.files = new Array();
        this.data  = new Object(); // Collection of data from data files. Key is the URL
    }


    // For MusicDB's WebUI filename and URL are the same
    // Order of call defines order of integration
    AddFile(filetype, url, name=null)
    {
        let file = new FileLoader(filetype, url, name);

        this.CreateProgress(url);
        file.SetProgressCallback(
            (object)=>
            {
                this.UpdateProgress(object.url, object.progress);
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

