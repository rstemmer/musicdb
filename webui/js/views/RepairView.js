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
    // contenttype: "song", "album"
    constructor(contenttype)
    {
        super("div", ["RepairBox", "flex", "flex-column"]);
        this.contenttype = contenttype;

        this.listbox = new Element("div", ["listbox", "flex", "flex-row"]);
        this.listold = new List("Invalid Paths");
        this.listnew = new List("New Paths");
        this.listold.MakeSelectable();
        this.listnew.MakeSelectable();
        this.listbox.AppendChild(this.listold);
        this.listbox.AppendChild(this.listnew);

        this.removefilebutton = new TextButton("Remove", "Remove File",
            ()=>{this.onButtonClick("RemoveFile");},
            "Remove this file from the Music Directory");
        this.removeentrybutton = new TextButton("Remove", "Remove Database Entry",
            ()=>{this.onButtonClick("RemoveEntry");},
            "Remove this entry from the MusicDB Database.");
        this.renamefilebutton = new TextButton("MusicDB", "Move File",
            ()=>{this.onButtonClick("MoveFile");},
            "Move the new file to the old place where the old file has been.");
        this.updatepathbutton = new TextButton("MusicDB", "Update Path Value",
            ()=>{this.onButtonClick("UpdatePath");},
            "Update only the path value of the MusicDB Database entry to match the new file path.");
        this.updateentrybutton = new TextButton("Import", "Update Song Entry",
            ()=>{this.onButtonClick("UpdateEntry");},
            "Update the old MusicDB Database entry with all information from the new file.");
        this.toolbar = new ToolBar();
        this.toolbar.AddButton(this.removeentrybutton);
        this.toolbar.AddSpacer(true);
        this.toolbar.AddButton(this.updateentrybutton);
        this.toolbar.AddButton(this.updatepathbutton);
        this.toolbar.AddButton(this.renamefilebutton);
        this.toolbar.AddSpacer(true);
        this.toolbar.AddButton(this.removefilebutton);

        this.AppendChild(this.listbox);
        this.AppendChild(this.toolbar);
    }



    Clear()
    {
        this.listold.Clear();
        this.listnew.Clear();
        // Refresh UI
        this.onListEntryClick();
    }



    Update(oldlist, newlist, namekey)
    {
        this.Clear();
        for(let olddata of oldlist)
        {
            let entry = new ListEntry(olddata[namekey], olddata);
            entry.SetClickEventCallback(()=>{this.onListEntryClick();});
            this.listold.AddEntry(entry);
        }
        for(let newdata of newlist)
        {
            let entry = new ListEntry(newdata[namekey], newdata);
            entry.SetClickEventCallback(()=>{this.onListEntryClick();});
            this.listnew.AddEntry(entry);
        }

        // Refresh UI
        this.onListEntryClick();
    }



    onListEntryClick()
    {
        let entriesold = this.listold.GetSelectedEntries();
        let entriesnew = this.listnew.GetSelectedEntries();

        this.removeentrybutton.Enable();
        this.updateentrybutton.Enable();
        this.updatepathbutton.Enable();
        this.renamefilebutton.Enable();
        this.removefilebutton.Enable();
        if(entriesold.length < 1)
        {
            this.removeentrybutton.Disable();
            this.updateentrybutton.Disable();
            this.updatepathbutton.Disable();
            this.renamefilebutton.Disable();
        }
        if(entriesnew.length < 1)
        {
            this.updateentrybutton.Disable();
            this.updatepathbutton.Disable();
            this.renamefilebutton.Disable();
            this.removefilebutton.Disable();
        }
    }



    onButtonClick(action)
    {
        let entryold  = this.listold.GetSelectedEntries()[0]; // \_ Either entry or undefined
        let entrynew  = this.listnew.GetSelectedEntries()[0]; // /
        let dbentry   = entryold?.data;
        let pathentry = entrynew?.data;

        window.console?.log(dbentry);
        window.console?.log(pathentry);

        switch(action)
        {
            case "RemoveFile":
                break;
            case "RemoveEntry":
                if(this.contenttype == "song")
                {
                    MusicDB_Call("RemoveSongFromDatabase", {songid: dbentry.id});
                    this.listold.RemoveEntry(entryold);
                }
                else
                    window.console?.warn(`Content type ${this.contenttype} cannot be removed from database.`);
                break;
            case "MoveFile":
                break;
            case "UpdatePath":
                break;
            case "UpdateEntry":
                break;
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

        this.songrepairbox = new RepairBox("song"); // content type is songs

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
        this.songrepairbox.Update(lostfiles["songs"], newfiles["filteredsongs"], "path");
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        if(fnc == "InitiateFilesystemScan" && sig == "ShowRepairView")
        {
            window.console?.log(args);

            this.songrepairbox.Clear();
            this.ResetUI();
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

