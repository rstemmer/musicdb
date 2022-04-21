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

class WebSocketError extends Layer
{
    constructor(background)
    {
        super(background, "WebSocketError");

        this.headline = new SettingsHeadline("Web Socket Error", "This view is shown because there occured an error while trying to connect to the MusicDB server via Web Sockets.");

        this.errormessage = new MessageBarError(`Connecting to the MusicDB WebSocket Server (<tt>${WEBSOCKET_URL}</tt>) failed.`);
        this.errormessage.Show();

        let message = "";
        message += "<h1>Web Socket Error</h1>";
        message += "<p>";
        message += "Connecting to the MusicDB server via Web Sockets failed.";
        message += " Several issues can lead to this error.";
        message += " The following chapters try to guide you to find and solve the issue.";
        message += "</p>";

        message += "<p>";
        message += "If there was a successful connection before, there may be a general error with your internet connection.";
        message += " <b>Please try to reload the whole WebUI first</b> and check if the error occures again";
        message += "</p>";

        message += "<h2>Trust Certificate</h2>";
        message += "<p>";
        message += "After a fresh installation or changing the Web Socket port, this issue is very common.";
        message += " MusicDB uses a SSL secured communication.";
        message += " By default, the encryption uses self signed certificates.";
        message += " The browser does not accept such certificates if the user does not explicitly trust them.";
        message += "</p>";

        message += "<p>";
        message += " To solve this issue just access the Web Socket URL with this browser and confirm that you trust the used certificate.";
        message += "</p>";

        message += "<p>";
        let WSURL = "https" + WEBSOCKET_URL.slice(3);
        message += `<b>Please follow this link:</b> <a href="${WSURL}">${WSURL}</a>`;
        message += "</p>";

        message += "<p>";
        message += "Note that the <tt>wss://</tt> part of the Web Socket URL is replaced by <tt>https</tt>.";
        message += " On success, you should see a welcome-page of the <i>Autobahn</i> framework.";
        message += " Now you can reload the WebUI. The Web Socket connection should now succeed.";
        message += "</p>";

        message += "<h2>Check Configuration</h2>";
        message += "<p>";
        message += "In case you changed the Web Socket port MusicDB shall use, make sure that the configuration is consistent.";
        message += " The port set in the MusicDB configuration (<tt>musicdb.ini</tt>)";
        message += " must be the same configured in <tt>config.js</tt> inside the <tt>webui</tt> directory.";
        let portstart = WEBSOCKET_URL.lastIndexOf(":") + 1;
        let port      = WEBSOCKET_URL.slice(portstart);
        message += ` The port currently defined in <tt>config.js</tt> is <tt>${port}</tt>.`;
        message += "</p>";
        //message += "<p>";
        //message += "";
        //message += "</p>";

        let messagebox = new Element("div", ["Welcome"]);
        messagebox.SetInnerHTML(message);

        // Tool Bar
        this.toolbar   = new ToolBar();
        this.reconnect = new TextButton("Reconnect", "Try Reconnect",
            ()=>{MusicDB.Connect();},
            "Try to reconnect to the MusicDB WebSocket Server.");

        this.toolbar.AddSpacer(true); // grow
        this.toolbar.AddButton(this.reconnect);
        this.toolbar.AddSpacer(true); // grow

        //this.AppendChild(this.headline);
        this.AppendChild(this.errormessage);
        this.AppendChild(messagebox);
        this.AppendChild(this.toolbar);
    }



    onMusicDBNotification(fnc, sig, data)
    {
        this.Hide();
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        this.Hide();
    }

}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

