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

class BackEndConnection
{
    constructor(url)
    {
        this.socket = null;
        this.url    = url;
        this.apikey = null;
    }


    // Configuration Interface

    ConfigureWatchdog(enable, interval=null)
    {
    }

    ConfigureReconnects(numretries=3)
    {
    }

    ConfigureAPIKey(apikey)
    {
        this.apikey = apikey;
    }


    // High Level Interface

    Connect()
    {
    }

    Disconnect()
    {
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
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

