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


// TODO:
// This class could have a base class BatchExecution to make the code reusable.
// Then the status element logic should be optional.

class AlbumImportTasks extends Element
{
    constructor()
    {
        super("div", ["AlbumImportTaks"]);
        this.tasks  = new Array();
        this.idseed = 1;
        this.currenttask = null;
        this.finishedtasks = new Array();
    }



    // taskfunction and resultevalfunction
    // must be a function that returns a new status as handled by StatusElementBase.SetStatus
    //
    // taskfunction gets an argument webtaskid that can be used as pass argument to a request with a certain signature.
    // resultsevalfunction gets the typical fnc,sif,args,pass arguments to evaluate if the tasks was successful
    AddTask(htmllabel, taskfunction, resultevalfunction)
    {
        let task = new Object();
        task["webuitaskid"]   = this.idseed++;
        task["statuselement"] = new StatusHTMLText(htmllabel, "open");
        task["taskfunction"]  = taskfunction;
        task["resultevalfunction"] = resultevalfunction;

        this.tasks.push(task);
        this.AppendChild(task["statuselement"]);
    }



    SetListenSignature(signature)
    {
        this.listensignature = signature;
    }



    Clear()
    {
        this.tasks = new Array();
        this.RemoveChilds();
    }



    ExecuteTasks()
    {
        if(this.tasks.length <= 0)
            return;

        this.currenttask = this.tasks[0];
        this.tasks       = this.tasks.splice(1);

        let state = "unknown";
        if(typeof this.currenttask["taskfunction"] === "function")
            state = this.currenttask["taskfunction"](this.currenttask["webuitaskid"]);
        this.currenttask["statuselement"].SetState(state);
    }



    onExecutionFinished(fnc, sig, args, pass)
    {
        if(pass?.webuitaskid != this.currenttask["webuitaskid"])
        {
            window.console?.error("onExecutionFinished event unexpected task was triggered.");
            return;
        }

        let state = "unknown";
        if(typeof this.currenttask["resultevalfunction"] === "function")
            state = this.currenttask["resultevalfunction"](fnc, sig, args, pass);

        this.currenttask["statuselement"].SetState(state);

        // This task has now finished. Continue with the next task.
        this.finishedtasks.push(this.currenttask);
        this.ExecuteTasks();
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        if(sig == this.listensignature)
        {
            this.onExecutionFinished(fnc, sig, args, pass);
        }
    }
}



class AlbumImportLayer extends Layer
{
    // background: Instance of the Curtain class that lays behind the Layer.
    // When the layer is made visible, then also the background will be shown
    constructor(background, id)
    {
        super(background, id)

        this.oldartistdirectoryname = null;
        this.oldalbumdirectoryname  = null;

        // Forms
        this.albumsettingstable = new AlbumSettingsTable((isvalid)=>{this.onAlbumSettingsValidation(isvalid);});
        this.songfilestable     = new SongFilesTable((isvalid)=>{this.onSongsSettingsValidation(isvalid);});
        this.tasks              = new AlbumImportTasks();
        this.tasks.SetListenSignature("ConfirmAlbumImportTask");

        // Tool Bar
        this.toolbar            = new ToolBar();
        this.cancelbutton       = new TextButton("MusicDB", "Cancel",
            ()=>{this.onClick_Cancel();},
            "Cancel album import. Nothing will be changed. ");
        this.renamebutton       = new TextButton("MusicDB", "Rename",
            ()=>{this.onClick_Rename();},
            "Apply changes and rename files and directories accordingly.");

        this.toolbar.AddButton(this.cancelbutton);
        this.toolbar.AddSpacer(true); // grow
        this.toolbar.AddButton(this.renamebutton);

        this.AppendChild(this.albumsettingstable);
        this.AppendChild(this.songfilestable);
        this.AppendChild(this.tasks);
        this.AppendChild(this.toolbar);
    }



    onClick_Cancel()
    {
        this.Hide();
    }

    onClick_Rename()
    {
        this.tasks.ExecuteTasks();
    }



    onAlbumSettingsValidation(isvalid)
    {
        this.ValidateForm();
    }
    onSongsSettingsValidation(isvalid)
    {
        this.ValidateForm();
    }
    ValidateForm()
    {
        let albumvalid = this.albumsettingstable.CheckIfValid();
        let songsvalid = this.songfilestable.CheckIfValid();

        this.PrepareImportTasks();

        if(albumvalid && songsvalid)
            this.renamebutton.Enable();
        else
            this.renamebutton.Disable();
    }



    PrepareImportTasks()
    {
        this.tasks.Clear();

        // Song Renaming Tasks
        let songrenamerequests  = this.songfilestable.GetRenameRequests();
        let albumdirectoryname  = this.oldalbumdirectoryname;
        let olddirectory        = this.oldartistdirectoryname + "/" + albumdirectoryname;

        // Rename all song files
        for(let songrenamerequest of songrenamerequests)
        {
            let oldpath  = olddirectory + "/" + songrenamerequest.oldname;
            let newpath  = olddirectory + "/" + songrenamerequest.newname;
            let htmldiff = songrenamerequest.htmldiff;

            this.tasks.AddTask(`Rename Song:&nbsp;${htmldiff}`,
                (webuitaskid)=>{
                    MusicDB_Request("RenameMusicFile", "ConfirmAlbumImportTask",
                        {oldpath: oldpath, newpath: newpath},
                        {webuitaskid: webuitaskid});
                    return "active";},
                (fnc, sig, args, pass)=>{
                    if(args === true) return "good";
                    else              return "bad";
                }
                );
        }

        // Rename album directory if needed
        let albumrenamerequest = this.albumsettingstable.GetAlbumRenameRequest();
        if(albumrenamerequest != null)
        {
            let oldalbumpath = this.oldartistdirectoryname + "/" + albumrenamerequest.oldname;
            let newalbumpath = this.oldartistdirectoryname + "/" + albumrenamerequest.newname;
            let htmldiff     = albumrenamerequest.htmldiff;
            this.tasks.AddTask(`Rename Album:&nbsp;${htmldiff}`,
                (webuitaskid)=>{
                    MusicDB_Request("RenameAlbumDirectory", "ConfirmAlbumImportTask",
                        {oldpath: oldalbumpath, newpath: newalbumpath},
                        {webuitaskid: webuitaskid});
                    return "active";},
                (fnc, sig, args, pass)=>{
                    if(args === true) return "good";
                    else              return "bad";
                }
                );

            // Update album directory to the new expected name
            albumdirectoryname = albumrenamerequest.newname;
        }

        // Change artist directory if needed
        let artistrenamerequest = this.albumsettingstable.GetArtistRenameRequest();
        if(artistrenamerequest != null)
        {
            let oldartistpath = artistrenamerequest.oldname;
            let newartistpath = artistrenamerequest.newname;
            let oldalbumpath  = oldartistpath + "/" + albumdirectoryname;
            let htmldiff      = artistrenamerequest.htmldiff;
            this.tasks.AddTask(`Change Artist:&nbsp;${htmldiff}`,
                (webuitaskid)=>{
                    MusicDB_Request("ChangeArtistDirectory", "ConfirmAlbumImportTask",
                        {oldalbumpath: oldalbumpath, newartistdirectory: newartistpath},
                        {webuitaskid: webuitaskid});
                    return "active";},
                (fnc, sig, args, pass)=>{
                    if(args === true) return "good";
                    else              return "bad";
                }
                );
        }
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        if(fnc == "FindAlbumSongFiles" && sig == "ShowAlbumSongFiles")
        {
            window.console?.log(args);
            this.oldartistdirectoryname = args[0].path.split("/")[0];
            this.oldalbumdirectoryname  = args[0].path.split("/")[1];
            let albumpath = this.oldartistdirectoryname + "/" + this.oldalbumdirectoryname;

            this.albumsettingstable.Update(
                args[0].artistname,
                args[0].albumname,
                args[0].releaseyear,
                args[0].origin,
                args[0].hasartwork,
                args[0].haslyrics,
                albumpath);
            this.songfilestable.Update(args);
            this.ValidateForm();
        }
        if(sig == "ConfirmAlbumImportTask")
        {
            window.console?.log(args);
            window.console?.log(pass);
            this.tasks.onMusicDBMessage(fnc, sig, args, pass);
        }
    }
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

