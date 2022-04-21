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

        this.filesystemelement;
        this.renameiconname;
        if(contenttype == "song" || contenttype == "video")
        {
            this.filesystemelement = "File";
            this.renameiconname    = "RenameFile"
        }
        else
        {
            this.filesystemelement = "Directory";
            this.renameiconname    = "RenameFolder"
        }

        this.databaseelement;
        if(contenttype == "song")
            this.databaseelement = "Song";
        else if(contenttype == "video")
            this.databaseelement = "Vide";
        else if(contenttype == "album")
            this.databaseelement = "Album";
        else if(contenttype == "artist")
            this.databaseelement = "Artist";


        this.removefilebutton = new TextButton("Remove", `Delete ${this.filesystemelement}`,
            ()=>{this.onButtonClick("RemoveFile");},
            `Delete this ${this.filesystemelement} from the Music Directory`);

        this.removeentrybutton = new TextButton("Remove", `Delete Database Entry`,
            ()=>{this.onButtonClick("RemoveEntry");},
            `Delete this ${this.databaseelement} entry from the MusicDB Database.`);

        this.renamefilebutton = new TextButton(this.renameiconname, `Rename ${this.filesystemelement}`,
            ()=>{this.onButtonClick("MoveFile");},
            `Rename the new ${this.filesystemelement} to the old name where the old ${this.filesystemelement} has been.`);

        this.updateentrybutton = new TextButton("Repair", `Update ${this.databaseelement} Entry`,
            ()=>{this.onButtonClick("UpdateEntry");},
            `Update the old MusicDB Database entry with all information from the new ${this.filesystemelement}.`);

        this.changeartistbutton = new TextButton("Repair", `Change ${this.databaseelement} Artist`,
            ()=>{this.onButtonClick("ChangeArtist");},
            `Change the artist associated to the ${this.databaseelement}.`);

        this.importfilebutton = new TextButton("Import", `Import ${this.databaseelement}`,
            ()=>{this.onButtonClick("ImportFile");},
            `Import this ${this.filesystemelement} as new ${this.databaseelement} into the MusicDB Database.`);

        this.toolbar = new ToolBar();
        this.toolbar.AddButton(this.removeentrybutton);
        this.toolbar.AddSpacer(true);
        this.toolbar.AddButton(this.updateentrybutton);
        if(contenttype == "album")
            this.toolbar.AddButton(this.changeartistbutton);
        this.toolbar.AddButton(this.renamefilebutton);
        this.toolbar.AddSpacer(true);
        if(contenttype != "artist")
            this.toolbar.AddButton(this.importfilebutton);
        //this.toolbar.AddButton(this.removefilebutton);

        this.message_differentroot = new MessageBarWarning("Selected entries have different root directories!");
        this.message_differenttype = new MessageBarInfo("Selected entries have different file formats!");
        this.message_invalidname   = new MessageBarError(`Invalid ${this.filesystemelement} name!`);
        this.message_samechecksum  = new MessageBarConfirm("The new file has the exact same content the missing file had.");
        this.message_samename      = new MessageBarConfirm(`The new ${this.filesystemelement} has the exact same name the missing ${this.filesystemelement} had.`);

        this.namediff = null;
        if(contenttype == "song")
            this.namediff = new SongFileNameDiff();
        else if(contenttype == "album")
            this.namediff = new AlbumDirectoryNameDiff();
        else if(contenttype == "artist")
            this.namediff = new ArtistDirectoryNameDiff();

        this.AppendChild(this.listbox);
        this.AppendChild(this.message_differentroot);
        this.AppendChild(this.message_differenttype);
        this.AppendChild(this.message_invalidname);
        this.AppendChild(this.message_samechecksum);
        this.AppendChild(this.message_samename);
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

        this.changeartistbutton.Enable();
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
            let oldfile = oldpath.split("/")[slicelength];
            let newfile = newpath.split("/")[slicelength];

            if(oldroot !== newroot)
            {
                if(this.contenttype !== "album" || newfile !== oldfile) // Allow changing album artist
                    this.changeartistbutton.Disable();
                this.updateentrybutton.Disable();
                this.renamefilebutton.Disable();

                this.message_differentroot.Show();
            }
            else
            {
                this.message_differentroot.Hide();
            }

            if(oldfile === newfile)
                this.message_samename.Show()
            else
                this.message_samename.Hide()

            // Check if both entries have the same file type or check sum
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
            this.message_samechecksum.Hide();
            this.message_samename.Hide()
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
            else if(this.contenttype == "album")
                oldname = new AlbumDirectoryName(oldfile);
            else if(this.contenttype == "artist")
                oldname = new ArtistDirectoryName(oldfile);
        }
        else
        {
            this.removeentrybutton.Disable();
            this.updateentrybutton.Disable();
            this.changeartistbutton.Disable();
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
                    this.changeartistbutton.Disable();
                }
                else
                    this.message_invalidname.Hide();
            }
            else if(this.contenttype == "album")
            {
                newname = new AlbumDirectoryName(newfile);
                // Check Parts
                let yearerror = newname.CheckReleaseYear();
                let nameerror = newname.CheckAlbumName();

                // Compose Error Message
                let errors = "";
                if(yearerror)
                    errors += `${yearerror} `;
                if(nameerror)
                    errors += `${nameerror}`;

                // Set Error is existing
                if(errors.length > 0)
                {
                    this.message_invalidname.UpdateMessage(`Invalid directory name: ${errors}`);
                    this.message_invalidname.Show();
                    this.importfilebutton.Disable();
                    this.updateentrybutton.Disable();
                    this.changeartistbutton.Disable();
                }
                else
                    this.message_invalidname.Hide();
            }
            else if(this.contenttype == "artist")
            {
                newname = new ArtistDirectoryName(newfile);
                // Check Parts
                let nameerror = newname.CheckArtistName();

                // Compose Error Message
                let errors = "";
                if(nameerror)
                    errors += `${nameerror}`;

                // Set Error is existing
                if(errors.length > 0)
                {
                    this.message_invalidname.UpdateMessage(`Invalid directory name: ${errors}`);
                    this.message_invalidname.Show();
                    this.importfilebutton.Disable();
                    this.updateentrybutton.Disable();
                    this.changeartistbutton.Disable();
                }
                else
                    this.message_invalidname.Hide();
            }
        }
        else
        {
            this.message_invalidname.Hide();

            this.updateentrybutton.Disable();
            this.changeartistbutton.Disable();
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
                    MusicDB.Call("RemoveSongEntry", {songid: dbentry.id});
                else if(this.contenttype == "album")
                    MusicDB.Call("RemoveAlbumEntry", {albumid: dbentry.id});
                else if(this.contenttype == "artist")
                    MusicDB.Call("RemoveArtistEntry", {artistid: dbentry.id});
                else
                    window.console?.warn(`${this.databaseelement} ${this.filesystemelement} cannot be removed from database.`);

                this.listold.RemoveEntry(entryold);
                break;

            case "MoveFile":
                // Move file from new path to the old one
                // So the new path should be the old one stored in the music database
                let oldpath = dbentry.path;
                let newpath = pathentry.path;

                if(this.contenttype == "song")
                    MusicDB.Call("RenameMusicFile", {oldpath: newpath, newpath: oldpath});
                else if(this.contenttype == "album")
                    MusicDB.Call("RenameAlbumDirectory", {oldpath: newpath, newpath: oldpath});
                else if(this.contenttype == "artist")
                    MusicDB.Call("RenameArtistDirectory", {oldpath: newpath, newpath: oldpath});
                else
                    window.console?.warn(`${this.databaseelement} ${this.filesystemelement} cannot be moved.`);

                this.listold.RemoveEntry(entryold);
                this.listnew.RemoveEntry(entrynew);
                break;

            case "ImportFile":
                if(this.contenttype == "song")
                    MusicDB.Call("CreateSongEntry", {newpath: pathentry.path});
                else if(this.contenttype == "album")
                {
                    WebUI.ShowLayer("AlbumImport"); // Hand over to the overlay
                    MusicDB.Request("FindAlbumSongFiles", "ShowAlbumImportLayer", {albumpath:pathentry.path});
                }
                else
                    window.console?.warn(`${this.databaseelement} ${this.filesystemelement} cannot be impored.`);

                this.listnew.RemoveEntry(entrynew);
                break;

            case "UpdateEntry":
                if(this.contenttype == "song")
                    MusicDB.Call("UpdateSongEntry", {songid: dbentry.id, newpath: pathentry.path});
                else if(this.contenttype == "album")
                    MusicDB.Call("UpdateAlbumEntry", {albumid: dbentry.id, newpath: pathentry.path});
                else if(this.contenttype == "artist")
                    MusicDB.Call("UpdateArtistEntry", {artistid: dbentry.id, newpath: pathentry.path});
                else
                    window.console?.warn(`${this.databaseelement} ${this.filesystemelement} cannot be updated.`);

                this.listold.RemoveEntry(entryold);
                this.listnew.RemoveEntry(entrynew);
                break;

            case "ChangeArtist":
                if(this.contenttype == "album")
                {
                    let newartistdir = pathentry.path.split("/")[0];
                    MusicDB.Call("ChangeArtistDirectory", {oldalbumpath: dbentry.path, newartistdirectory: newartistdir});
                }
                else
                    window.console?.warn(`${this.databaseelement} ${this.filesystemelement} cannot be updated.`);

                this.listold.RemoveEntry(entryold);
                this.listnew.RemoveEntry(entrynew);
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
            "Database entries can break when a file gets renamed in the file system so that the path stored in the database is no longer valid.\n"+
            " Renaming a file in the file system is a considered use-case and this view is made to reassign the corresponding database entry to the renamed file.\n"+
            " Keep in mind that only files and directories are listed that can be managed by MusicDB (Read/Write access),"+
            " and that are reasonable artist and album directories.";
        super("TaskListView", title, descr);
        let headline = new SettingsHeadline(title, descr);

        this.message_loading = new MessageBarProcessing("Scanning file system and database …");
        this.message_scanfailed = new MessageBarError("Scanning file system and database failed! See MusicDB log files for details. Sorry.");
        this.songrepairbox   = new RepairBox("song");   // content type is songs
        this.albumrepairbox  = new RepairBox("album");  // content type is album
        this.artistrepairbox = new RepairBox("artist"); // content type is artist

        this.ResetUI();
    }



    onViewMounted()
    {
        this.message_loading.Show();
    }



    ResetUI()
    {
        this.RemoveChilds();

        this.AppendChild(this.headline);
        this.AppendChild(this.message_loading);
        this.AppendChild(this.message_scanfailed);
        this.AppendChild(this.songrepairbox);
        this.AppendChild(this.albumrepairbox);
        this.AppendChild(this.artistrepairbox);
    }



    UpdateLostFilesLists(lostfiles, newfiles)
    {
        this.songrepairbox.Update(lostfiles["songs"], newfiles["filteredsongs"], "path");
        this.albumrepairbox.Update(lostfiles["albums"], newfiles["albums"], "path");
        this.artistrepairbox.Update(lostfiles["artists"], newfiles["artists"], "path");
    }

    ClearLostFilesLists()
    {
        this.songrepairbox.Clear();
        this.albumrepairbox.Clear();
        this.artistrepairbox.Clear();
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        if(fnc == "InitiateFilesystemScan" && sig == "ShowRepairView")
        {
            window.console?.log(args);

            this.ClearLostFilesLists();
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
                this.UpdateLostFilesLists(lostpaths, newpaths);
                this.ResetUI();
                this.message_loading.Hide();
                this.message_scanfailed.Hide();
            }
            else if(state == "fsscanfailed")
            {
                this.ResetUI();
                this.message_loading.Hide();
                this.message_scanfailed.Show();
            }
        }
        return;
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

