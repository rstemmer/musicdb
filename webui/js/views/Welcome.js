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
        let headline = new SettingsHeadline("MusicDB", 
            "This view is shown because there is no song or video queue avaliable.\n"+
            "Usually because MusicDB is fresh installed.");

        super("Welcome", headline, new MusicDBLogo);
        this.AddCSSClass("Welcome");

        let message_welcome = new MessageBarConfirm("MusicDB installation succeeded")
        message_welcome.Show();
        this.column1.AppendChild(message_welcome);

        let message = "";
        message += "<h1>Welcome to MusicDB</h1>";
        message += "<p>";
        message += "This information is shown because there is no music to play in the queue.";
        message += " Usually the random song selection algorithm adds music to the queue if music is available.";
        message += " This is of course not the case when you start MusicDB for the first time.";
        message += "</p>";

        message += "<p>";
        message += "If you start MusicDB for the first time, this is OK.";
        message += " <b>You have installed MusicDB sucessfully.</b>";
        message += " Now you only have to add content to the database.";
        message += " Just follow the instruction in the <a target=\"_blank\" href=\"https://rstemmer.github.io/musicdb/build/html/usage/music.html\">documentation</a> to add music to the database.";
        message += " You can use the Settings (see the menu at the top right corner) to import existing music or upload new.";
        message += " For importing and uploading new music you can also click on the button on the right.";
        message += " You can also use the Settings to create genre and sub-genre tags.";
        message += "</p>";

        message += "<p>";
        message += " After adding new music to the database for the first time, you have to restart the MusicDB Server.";
        message += " <br><tt>sudo systemctl restart musicdb</tt>";
        message += "</p>";

        message += "<p>";
        message += "In case you see this view with a previously fully functional installation,";
        message += " there may be something broken with your setup.";
        message += " You can make the logs more verbose by setting the <tt>[log]->loglevel</tt> settings in the <tt>/etc/musicdb.ini</tt> file to <tt>DEBUG</tt>.";
        message += " Then restart the MusicDB server.";
        message += " In case of questions just create an <a target=\"_blank\" href=\"https://github.com/rstemmer/musicdb/issues\">Issue at GitHub.com</a>.";
        message += "</p>";

        this.toolbar      = new ToolBar();
        this.importbutton = new TextButton("Import", "Upload and/or Import",
            ()=>
            {
                MusicDB.Request("FindNewContent", "ShowAlbumImport");
            },
            "Show the settings view to upload new albums and/or import existing albums.");

        this.toolbar.AddSpacer(true); // grow
        this.toolbar.AddButton(this.importbutton);
        this.toolbar.AddSpacer(true); // grow

        let messagebox = new Element("div");
        messagebox.SetInnerHTML(message);
        this.column1.AppendChild(messagebox);
        this.column2.AppendChild(this.toolbar);
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        return;
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

