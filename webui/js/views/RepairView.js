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
        this.updateentrybutton = new TextButton("Repair", "Update Song Entry",
            ()=>{this.onButtonClick("UpdateEntry");},
            "Update the old MusicDB Database entry with all information from the new file.");
        this.importfilebutton = new TextButton("Import", "Import File",
            ()=>{this.onButtonClick("ImportFile");},
            "Import this file into the MusicDB Database. It will be add to the existing Album.");
        this.toolbar = new ToolBar();
        this.toolbar.AddButton(this.removeentrybutton);
        this.toolbar.AddSpacer(true);
        this.toolbar.AddButton(this.updateentrybutton);
        this.toolbar.AddButton(this.renamefilebutton);
        this.toolbar.AddSpacer(true);
        this.toolbar.AddButton(this.importfilebutton);
        //this.toolbar.AddButton(this.removefilebutton);

        this.message_differentroot = new MessageBarWarning("Selected entries have different root directories!");
        this.message_differenttype = new MessageBarInfo("Selected entries have different file formats!");
        this.message_invalidname   = new MessageBarError("Invalid file name!");
        this.message_samechecksum  = new MessageBarConfirm("The new file has the exact same content the missing file had.");

        this.namediff = null;
        if(contenttype == "song")
            this.namediff = new SongFileNameDiff();

        this.AppendChild(this.listbox);
        this.AppendChild(this.message_differentroot);
        this.AppendChild(this.message_differenttype);
        this.AppendChild(this.message_invalidname);
        this.AppendChild(this.message_samechecksum);
        this.AppendChild(this.namediff);
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
        this.renamefilebutton.Enable();
        this.removefilebutton.Enable();
        this.importfilebutton.Enable();

        if(entriesold.length === 1 && entriesnew.length === 1)
        {
            // Check if the entries are in the same album directory
            let slicelength = 0;
            if(this.contenttype == "song")
                slicelength = 2;
            else if(this.contenttype == "album" || this.contenttype == "video")
                slicelength = 1;

            let oldpath = entriesold[0].data.path;
            let newpath = entriesnew[0].data.path;
            let oldroot = oldpath.split("/").slice(0, slicelength).join("/");
            let newroot = newpath.split("/").slice(0, slicelength).join("/");

            if(oldroot !== newroot)
            {
                this.updateentrybutton.Disable();
                this.renamefilebutton.Disable();

                this.message_differentroot.Show();
            }
            else
            {
                this.message_differentroot.Hide();
            }

            // Check if both entries have the same file type
            if(this.contenttype == "song" || this.contenttype == "video")
            {
                let oldtype = oldpath.split(".").slice(-1)[0]
                let newtype = newpath.split(".").slice(-1)[0]
                if(oldtype !== newtype)
                {
                    this.renamefilebutton.Disable();
                    this.message_differenttype.Show();
                }
                else
                {
                    this.message_differenttype.Hide();
                }

                let oldchecksum = entriesold[0].data.checksum;
                let newchecksum = entriesnew[0].data.checksum;
                if(oldchecksum === newchecksum)
                {
                    this.message_samechecksum.Show();
                }
                else
                {
                    this.message_samechecksum.Hide();
                }

            }
        }
        else
        {
            this.message_differentroot.Hide();
            this.message_differenttype.Hide();
        }

        // Handle old list entry
        let oldname = null;
        if(entriesold.length === 1)
        {
            let oldpath = entriesold[0].data.path;
            let oldfile = oldpath.split("/").slice(-1)[0];
            window.console?.log(oldfile);
            if(this.contenttype == "song")
                oldname = new SongFileName(oldfile);
        }
        else
        {
            this.removeentrybutton.Disable();
            this.updateentrybutton.Disable();
            this.renamefilebutton.Disable();
        }

        // Handle new list entry
        let newname = null;
        if(entriesnew.length === 1)
        {
            let newpath = entriesnew[0].data.path;
            let newfile = newpath.split("/").slice(-1)[0];
            window.console?.log(newfile);
            if(this.contenttype == "song")
            {
                newname = new SongFileName(newfile);
                // Check Parts
                let cdnumerror = newname.CheckCDNumber();
                let trackerror = newname.CheckTrackNumber();
                let nameerror  = newname.CheckSongName();

                // Compose Error Message
                let errors = "";
                if(cdnumerror)
                    errors += `${cdnumerror} `;
                if(trackerror)
                    errors += `${trackerror} `;
                if(nameerror)
                    errors += `${nameerror}`;

                // Set Error is existing
                if(errors.length > 0)
                {
                    this.message_invalidname.UpdateMessage(`Invalid file name: ${errors}`);
                    this.message_invalidname.Show();
                    this.importfilebutton.Disable();
                    this.updateentrybutton.Disable();
                }
                else
                    this.message_invalidname.Hide();
            }
        }
        else
        {
            this.message_invalidname.Hide();

            this.updateentrybutton.Disable();
            this.renamefilebutton.Disable();
            this.removefilebutton.Disable();
            this.importfilebutton.Disable();
        }

        // Update name difference information
        this.namediff.UpdateDiff(oldname, newname);
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
                    MusicDB_Call("RemoveSongEntry", {songid: dbentry.id});
                    this.listold.RemoveEntry(entryold);
                }
                else
                    window.console?.warn(`Content type ${this.contenttype} cannot be removed from database.`);
                break;

            case "MoveFile":
                // Move file from new path to the old one
                // So the new path should be the old one stored in the music database
                let oldpath = dbentry.path;
                let newpath = pathentry.path;
                if(this.contenttype == "song")
                {
                    MusicDB_Call("RenameMusicFile", {oldpath: newpath, newpath: oldpath});
                    this.listold.RemoveEntry(entryold);
                    this.listnew.RemoveEntry(entrynew);
                }
                else if(this.contenttype == "album")
                {
                    MusicDB_Call("RenameAlbumDirectory", {oldpath: newpath, newpath: oldpath});
                    this.listold.RemoveEntry(entryold);
                    this.listnew.RemoveEntry(entrynew);
                }
                else
                    window.console?.warn(`Files of content type ${this.contenttype} cannot be moved.`);
                break;

            case "ImportFile":
                if(this.contenttype == "song")
                {
                    MusicDB_Call("CreateSongEntry", {newpath: pathentry.path});
                    this.listnew.RemoveEntry(entrynew);
                }
                else
                    window.console?.warn(`Content type ${this.contenttype} cannot be imported.`);
                break;

            case "UpdateEntry":
                if(this.contenttype == "song")
                {
                    MusicDB_Call("UpdateSongEntry", {songid: dbentry.id, newpath: pathentry.path});
                    this.listold.RemoveEntry(entryold);
                    this.listnew.RemoveEntry(entrynew);
                }
                else
                    window.console?.warn(`Content type ${this.contenttype} cannot be updated.`);
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

