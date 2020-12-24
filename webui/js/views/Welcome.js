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

class Welcome extends MainView2
{
    constructor()
    {
        let headline = new MainViewHeadline(null)
        headline.UpdateRawInformation("MusicDB", "", "First Run", "");
        super("Welcome", headline, new MusicDBLogo);

        let nosongswarning = new MessageBarWarning("There is no Music in the Queue");
        nosongswarning.Show();
        this.column1.appendChild(nosongswarning.GetHTMLElement());

        let message = "";
        message += "<h1>Welcome to MusicDB</h1>";
        message += "<p>";
        message += "This information is shown because there is no music to play in the queue.";
        message += "</p>";
        message += "<p>";
        message += "If you start MusicDB for the first time, this is OK. ";
        message += "Just follow the instruction in the <a target=\"_blank\" href=\"https://rstemmer.github.io/musicdb/build/html/usage/music.html\">documentation</a> to add music to the database.";
        message += "</p>";

        let messagebox = document.createElement("div");
        messagebox.innerHTML = message;
        this.column1.appendChild(messagebox);
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        return;
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

