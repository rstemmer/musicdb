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

class RepairBox extends Element
{
    constructor()
    {
        super("div", ["RepairBox", "flex", "flex-column"]);

        this.listbox = new Element("div", ["listbox", "flex", "flex-row"]);
        this.listold = new List();
        this.listnew = new List();
        this.listbox.AppendChild(this.listold);
        this.listbox.AppendChild(this.listnew);

        this.repairbutton = new TextButton("MusicDB", "Repair",
            ()=>{return;},
            "Todo");
        this.toolbar = new ToolBar();
        this.toolbar.AddSpacer(true);
        this.toolbar.AddButton(this.repairbutton);
        this.toolbar.AddSpacer(true);

        this.AppendChild(this.listbox);
        this.AppendChild(this.toolbar);
    }

    Update(oldlist, newlist, namekey)
    {
        this.listold.Clear();
        for(let olddata of oldlist)
        {
            let entry = new ListEntry();
            entry.SetInnerText(olddata[namekey]);
            entry.SetClickEventCallback((event)=>{return;});
            this.listold.AddEntry(entry);
        }
        for(let newdata of newlist)
        {
            let entry = new ListEntry();
            entry.SetInnerText(newdata[namekey]);
            entry.SetClickEventCallback((event)=>{return;});
            this.listnew.AddEntry(entry);
        }
    }
}



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

        this.songrepairbox = new RepairBox();

        this.ResetUI();
    }



    ResetUI()
    {
        this.RemoveChilds();

        this.AppendChild(this.headline);
        this.AppendChild(this.songrepairbox);
    }



    UpdateLostFilesList(lostfiles, newfiles)
    {
        this.songrepairbox.Update(lostfiles["songs"], newfiles["songs"], "path");
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
        if(fnc == "MusicDB:Task" && sig == "StateUpdate")
        {
            let task  = data["task"];
            let state = task["state"];
            if(state == "fsscancomplete")
            {
                let annotations = task["annotations"];
                let lostpaths   = annotations["lostpaths"];
                let newpaths    = annotations["newpaths"];
                window.console?.log(data);
                this.UpdateLostFilesList(lostpaths, newpaths);
                this.ResetUI();
            }
        }
        return;
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

