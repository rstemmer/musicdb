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

class RepairView extends MainSettingsView
{
    constructor()
    {
        let title = "Repair Database";
        let descr = "Find lost connections between files and database entries and repair them.\n"+
            "Database entried can break when a file gets renamed in the file system so that the path stored in the database is no longer valid.\n"+
            " Renaming a file in the file system is a considered use-case and this view is made to reassign the corresponding database entry to the renamed file.";
        super("TaskListView", title, descr);
        let headline = new SettingsHeadline(title, descr);

        this.ResetUI();
    }



    ResetUI()
    {
        this.RemoveChilds();

        this.AppendChild(this.headline);
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        if(fnc == "InitiateFilesystemScan" && sig == "ShowRepairView")
        {
            window.console?.log(args);
        }
        return;
    }

    onMusicDBNotification(fnc, sig, data)
    {
        if(fnc == "MusicDB:Task" && sig == "StatusUpdate")
        {
            let state = data["state"];
            if(state == "fsscancomplete")
                window.console?.log(data);
        }
        return;
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

