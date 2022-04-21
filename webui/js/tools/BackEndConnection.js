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

"use strict";

class Watchdog
{
    constructor(timeoutcallback, interval)
    {
        this.ontimeout = timeoutcallback;
        this.interval  = interval;
        this.enabled   = false;
        this.timer     = null;
    }



    Enable(interval = null)
    {
        if(interval !== null)
            this.interval = interval;

        this.Start();
        this.enabled = true
    }

    Disable()
    {
        this.Stop();
        this.enabled = false;
    }

    Start()
    {
        if(this.enabled !== true)
            return false;

        this.timer = setTimeout(()=>{this.onTimeout();}, this.interval);
    }

    Stop()
    {
        if(this.timer !== null)
            clearTimeout(this.timer);
    }

    Reset()
    {
        this.Start();
    }

    onTimeout()
    {
        this.ontimeout?.();
    }
}




class BackEndConnection
{
    constructor(url)
    {
        this.socket    = null;
        this.url       = url;
        this.apikey    = null;
        this.callbacks = new Object();
        this.watchdog  = new Watchdog(()=>{this.onWatchdog();}, 3000); // Default 3s timeout
    }


    // Configuration Interface

    ConfigureWatchdog(enable, interval=null)
    {
        if(enable === true)
            this.watchdog.Enable(interval);
        else
            this.watchdog.Disable();
    }

    ConfigureReconnects(numretries=3)
    {
    }

    ConfigureAPIKey(apikey)
    {
        this.apikey = apikey;
    }

    /*
     * Event Names:
     *  connect:        When connected to the back end
     *  disconnect:     When disconnected from the back end without error
     *  message:        On received message
     *  notification:   On received notification
     *  error:          On error. Implies disconnection from server
     *  watchdog:       On timeout of the watch dog
     */
    SetCallbackForEvent(eventname, callbackfunction)
    {
        const availablenames = ["connect", "disconnect", "message", "notification", "error", "watchdog"];
        if(availablenames.indexOf(eventname) < 0)
        {
            window.console?.warn(`Event name ${eventname} not valid!`);
            return false;
        }

        this.callbacks[eventname] = callbackfunction;
        return true;
    }



    // High Level Interface

    Connect()
    {
        this.Disconnect();

        this.socket = new WebSocket(this.url);
        this.socket.onopen    = ()=>{this.onConnect();};
        this.socket.onclose   = (arg)=>{this.onDisconnect(arg);};
        this.socket.onerror   = (arg)=>{this.onError(arg);};
        this.socket.onmessage = (arg)=>{this.onMessage(arg);};
    }

    Disconnect()
    {
        if(this.socket !== null)
            this.socket.close();
    }



    Call(fncname, args=null)
    {
        return this.SendPacket("call", fncname);
    }

    Request(fncname, fncsig, args=null, pass=null)
    {
        return this.SendPacket("request", fncname, fncsig, args, pass);
    }

    Broadcast(fncname, fncsig, args=null, pass=null)
    {
        return this.SendPacket("broadcast", fncname, fncsig, args, pass);
    }



    // Low Level Interface

    SendPacket(method, fncname, fncsig=null, args=null, pass=null)
    {
        let packet = this.CreatePacket(method, fncname, fncsig, args, pass);

        window.console?.log("%c << fnc:"+packet.fncname+"; sig: "+packet.fncsig, "color:#9cc87a");
        try
        {
            this.socket.send(packet);
        }
        catch(error)
        {
            window.console?.error("Sending packet failed!");
            window.console?.log(error);
            window.console?.log(packet);
            return false;
        }
        return true;
    }

    CreatePacket(method, fncname, fncsig=null, args=null, pass=null)
    {
        let packet = new Object();
        packet["method"]    = method;
        packet["fncname"]   = fncname;
        packet["fncsig"]    = fncsig;
        packet["arguments"] = args;
        packet["pass"]      = pass;
        packet["key"]       = this.apikey;
        return JSON.stringify(packet);
    }



    // Event Handler

    onConnect()
    {
        window.console?.log("WebSocket connection opened");
        this.watchdog.Start();
        this.callbacks.connect?.();
    }

    onDisconnect(e)
    {
        window.console?.log("WebSocket connection closed");
        window.console?.log(e);
        this.watchdog.Stop();
        this.callbacks.disconnect?.(e);
    }

    onError(e)
    {
        window.console?.log("WebSocket connection failed");
        window.console?.log(e);
        this.watchdog.Stop();
        this.callbacks.error?.(e);
    }

    onMessage(e)
    {
        window.console?.log(e);
        this.watchdog.Reset();

        let packet  = JSON.parse(e.data);
        let method  = packet.method;
        let fncname = packet.fncname;
        let fncsig  = packet.fncsig;
        let args    = packet.arguments;
        let pass    = packet.pass;

        if(method === "notification")
            this.callbacks.notification?.(fncname, fncsig, args);
        else
            this.callbacks.message?.(fncname, fncsig, args, pass);
    }

    onWatchdog()
    {
        window.console?.log("WebSocket watchdog timeout");
        this.callbacks.watchdog?.();
        this.Connect(); // Try to reconnect
    }

}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

