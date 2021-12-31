// MusicDB,  a music manager with web-bases UI that focus on music.
// Copyright (C) 2017 - 2021  Ralf Stemmer <ralf.stemmer@gmx.net>
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

class Application
{
    constructor()
    {
        this.notificationhandler = new Array();
        this.messagehandler      = new Array();

        this.manager = new Object();
        this.views   = new Object();
        this.layers  = new Object();

        this.mountonload = new Object();
    }



    AddManager(id, manager)
    {
        this.manager[id] = manager;
        this.AddHandler(manager);
        return manager;
    }
    GetManager(id)
    {
        return this.manager[id];
    }



    // If bodyelementid is given, the view will be append to the element on window load
    AddView(id, view, bodyelementid=null)
    {
        this.views[id] = view;
        this.AddHandler(view);

        if(typeof bodyelementid === "string")
            this.mountonload[bodyelementid] = view;

        return view;
    }
    GetView(id)
    {
        return this.views[id];
    }



    AddLayer(id, layer)
    {
        this.layers[id] = layer;
        this.AddHandler(layer);
        return layer;
    }
    GetLayer(id)
    {
        return this.layers[id];
    }

    ShowLayer(id)
    {
        let layer = this.GetLayer(id);
        if(typeof layer.Show === "function")
            layer.Show();
    }
    HideLayer(id)
    {
        let layer = this.GetLayer(id);
        if(typeof layer.Hide === "function")
            layer.Hide();
    }




    AddHandler(component)
    {
        if(typeof component.onMusicDBNotification === "function")
            this.notificationhandler.push(component);
        if(typeof component.onMusicDBMessage === "function")
            this.messagehandler.push(component);
    }


    ////////////////////
    // Event handling //
    ////////////////////



    onWindowLoad()
    {
        let body = new Element(document.body);

        for(let [id, view] of Object.entries(this.mountonload))
        {
            let mountpoint = new Element(document.getElementById(id));
            mountpoint.AppendChild(view);
        }

        for(let [id, layer] of Object.entries(this.layers))
        {
            body.AppendChild(layer);
        }
    }



    onWebSocketOpen()
    {
        window.console?.log("[WebSocket] Open");
    }

    onWebSocketClosed()
    {
        window.console?.log("[WebSocket] Closed");
    }

    onWebSocketError()
    {
        window.console?.log("[WebSocket] Error");
    }



    onWatchdogBarks()
    {
        window.console?.log("[Watchdog] Barks");
    }



    onMusicDBNotification(fnc, sig, data)
    {
        window.console?.log("%c >> fnc: "+fnc+"; sig: "+sig, "color:#c87a7a");

        for(let component of this.notificationhandler)
            component.onMusicDBNotification(fnc, sig, data);
    }

    onMusicDBMessage(fnc, sig, args, pass)
    {
        window.console?.log("%c >> fnc: "+fnc+"; sig: "+sig, "color:#7a90c8");

        for(let component of this.messagehandler)
            component.onMusicDBMessage(fnc, sig, args, pass);
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

