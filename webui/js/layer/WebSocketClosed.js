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



class WebSocketClosed extends Layer
{
    // background: Instance of the Curtain class that lays behind the Layer.
    // When the layer is made visible, then also the background will be shown
    constructor(background)
    {
        super(background, "WebSocketClosed")

        // Headlines
        this.headline = new LayerHeadline("WebSocket Connection Closed",
            "The connection to the MusicDB WebSocket Server has been closed.");
        this.message  = new MessageBarInfo("Connection to the MusicDB WebSocket Server has been closed.");
        this.message.Show();

        // Tool Bar
        this.toolbar   = new ToolBar();
        this.reconnect = new TextButton("Reconnect", "Reconnect",
            ()=>{ConnectToMusicDB();},
            "Cancel album upload. Nothing will be changed. Partialy uploaded data will be removed.");

        this.toolbar.AddSpacer(true); // grow
        this.toolbar.AddButton(this.reconnect);
        this.toolbar.AddSpacer(true); // grow

        //this.AppendChild(this.headline);
        this.AppendChild(this.message);
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

