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

function LoadFile(filename)
{
    let request = new XMLHttpRequest();
    request.addEventListener("progress", (event)=>{onProgress(filename, event);},   false);
    request.addEventListener("load",     (event)=>{onFileLoaded(filename, event);}, false);
    request.open("GET", filename);
    request.send();
}

function onProgress(filename, event)
{
    if(event.lengthComputable)
        UpdateProgress(filename, event.loaded / event.total);
    else
        UpdateProgress(filename);
}

function onFileLoaded(filename, event)
{
    let data = event.target.responseText;
    let observerconfig = { attributes: true, childList: true, subtree: true };

    if(filename === "WebUI.js")
    {
        let script   = document.createElement("script");
        let observer = new MutationObserver(()=>{onFileIntegrated(filename, script);});
        observer.observe(script, observerconfig);
        script.textContent = data;
        document.body.appendChild(script);
    }
    else if(filename === "WebUI.css")
    {
        let style    = document.createElement("style");
        let observer = new MutationObserver(()=>{onFileIntegrated(filename, style);});
        observer.observe(style, observerconfig);
        style.textContent = data;
        document.documentElement.appendChild(style);
    }
    else if(filename === "WebUI.json")
    {
        SVGCACHE = data;
        onFileIntegrated("WebUI.json");
    }
    else
    {
        window.console?.warn(`Unknown file ${filename} loaded. Will be ignored!`);
    }
}


function onFileIntegrated(filename, htmlnode=null)
{
    FILELOADINGCOUNT += 1;

    if(FILELOADINGCOUNT < 3)
        return;

    // Give the browser some time to load the code
    let timer = setTimeout(()=>
        {
            InitializeWebUI(SVGCACHE);
            SVGCACHE = null; // unload this big string
            RemoveLoadingProgressLayer();
            ExecuteWebUI();  // Now WebUI can take over
        }, 1000);
}



function UpdateProgress(filename, progress=null)
{
    let progressbar = document.getElementById(`${filename}.Progress`);
    if(progress)
        progressbar.value = progress * 100;
}

function CreateLoadingProgressLayer()
{
    let element = document.createElement("div");
    element.style.cssText += "position: absolute; top: 0; left: 0;";
    element.style.cssText += "width: 100vw; height: 100vh; margin: 0; padding: 0;";
    element.style.cssText += "display: flex; flex-direction: column; background: #202020;";
    element.style.cssText += "color: #C0C0C0; font-family: Sans-Serif;";
    element.id = "LoadingProgressLayer";

    function CreateProgressBar(filename)
    {
        let label    = document.createElement("label");
        let progress = document.createElement("progress");
        progress.id  = `${filename}.Progress`;
        progress.max = 100;
        progress.value = 0;
        label.innerText = `${filename}`;

        progress.style.cssText += "width: 40%;";
        label.style.cssText    += "width: 40%; padding-right: 2rem; text-align: right; display: inline-box;";

        let container= document.createElement("div");
        container.style.cssText += "display: flex;";
        container.appendChild(label);
        container.appendChild(progress);
        return container;
    }

    element.appendChild(CreateProgressBar("WebUI.js"));
    element.appendChild(CreateProgressBar("WebUI.css"));
    element.appendChild(CreateProgressBar("WebUI.json"));

    document.body.appendChild(element);
}

function RemoveLoadingProgressLayer()
{
    let element = document.getElementById("LoadingProgressLayer");
    document.body.removeChild(element);
}



window.onload = function ()
{
    CreateLoadingProgressLayer();
    LoadFile("WebUI.css");
    LoadFile("WebUI.json");
    LoadFile("WebUI.js");
}




// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

