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



class AlbumIntegrationLayer extends Layer
{
    // background: Instance of the Curtain class that lays behind the Layer.
    // When the layer is made visible, then also the background will be shown
    constructor(background)
    {
        super(background, "AlbumIntegrationLayer")

        this.selectorid = null;    // This ID is used as filter to only show uploads of a certain file group if not null

        // Headlines
        this.albumheadline = new LayerHeadline("Album Directory Settings",
            "These settings can be used to initialize the naming of the Album and to define to which Artist the Album belongs. "+
            "These settings can also be updated after the upload is complete.\n"+
            "After integrating the uploaded album, the path follows the MusicDB Naming Scheme for Albums: "+
            "\"{ArtistName}/{ReleaseYear} - {AlbumName}\"");
        this.tasksheadline = new LayerHeadline("Integration Tasks Overview",
            "This is an overview of the files that will be copied into the Music Directory when the Integration process gets started. "+
            "During integration, the status of each task will be visualized.");

        // Forms
        this.albumsettingstable = new AlbumSettingsTable((isvalid)=>{this.onAlbumSettingsValidation(isvalid);});

        // Data
        this.tasks              = new BatchExecution();
        this.albumfiles         = new Array();

        // Tool Bar
        this.toolbar            = new ToolBar();
        this.cancelbutton       = new TextButton("Remove", "Cancel and Remove",
            ()=>{this.onClick_Cancel();},
            "Cancel album integration. Nothing will be changed inside the Music directory. Uploaded data will be removed.");
        this.integratebutton    = new TextButton("NextLayer", "Integrate Album",
            ()=>{this.onClick_Integrate();},
            "Apply some renaming and stores the uploaded files inside the Music dicretory. After integration the album can be imported into MusicDB.");

        this.toolbar.AddButton(this.cancelbutton);
        this.toolbar.AddSpacer(true); // grow
        this.toolbar.AddButton(this.integratebutton);

        this.ResetUI();
    }



    ResetUI()
    {
        this.RemoveChilds();

        this.tasks.Clear();
        this.albumfiles = new Array();

        this.AppendChild(this.albumheadline);
        this.AppendChild(this.albumsettingstable);
        this.AppendChild(this.tasksheadline);
        this.AppendChild(this.tasks);
        this.AppendChild(this.toolbar);
    }



    // ID as specified for task.annotations.selectorid.
    // null when upload progress of all upload tasks shall be shown
    SetSelectorFilter(selectorid)
    {
        this.selectorid = selectorid;
    }



    onClick_Cancel()
    {
        this.Hide();

        // Trigger removing uploaded files
        for(let albumfile of this.albumfiles)
        {
            let taskid = albumfile.id;
            MusicDB_Call("RemoveUpload", {taskid: taskid});
        }
        this.ResetUI();
    }

    onClick_Integrate()
    {
        let albumpath = this.GetAlbumPath();
        albumintegrationprogress.SetAlbumPath(albumpath);
        albumintegrationprogress.ExecuteTasks(this.tasks); // Will also Show the layer
        this.Hide();
    }



    onAlbumSettingsValidation(isvalid)
    {
        this.PrepareIntegrationTasks();

        if(isvalid)
            this.integratebutton.Enable();
        else
            this.integratebutton.Disable();
    }



    GetAlbumPath()
    {
        let albumdirectory  = this.albumsettingstable.GetAlbumDirectoryName();
        let artistdirectory = this.albumsettingstable.GetArtistDirectoryName();
        let albumpath       = artistdirectory + "/" + albumdirectory;
        return albumpath;
    }



    PrepareIntegrationTasks()
    {
        this.tasks.Clear();

        let albumpath = this.GetAlbumPath();

        for(let albumfile of this.albumfiles)
        {
            let albumfileid = albumfile.id;
            let musicpath   = albumpath + "/" + albumfile.sourcefilename;

            this.tasks.AddTask(`New File: ${musicpath}`,
                (webuitaskid)=>{
                    MusicDB_Request("IntegrateContent", "ConfirmAlbumIntegrationTask",
                        {taskid: albumfileid, musicpath: musicpath},
                        {webuitaskid: webuitaskid});
                    return "active";
                },
                (fnc, sig, args, pass)=>{
                    if(args == null)
                        return "bad";
                    else
                        return "active";
                },
                (fnc, sig, rawdata)=>{
                    if(fnc != "MusicDB:Task")
                        return null;

                    if(sig == "InternalError")
                    {
                        window.console?.warn(`Integrating album file failed with error: "${rawdata["message"]}"`)
                        return "bad";
                    }
                    if(sig == "StateUpdate")
                    {
                        if(rawdata["state"] == "integrationfailed")
                            return "bad";
                        else if(rawdata["state"] == "readyforimport")
                            return "good";
                    }
                    return "active";
                });
        }
    }



    onMusicDBNotification(fnc, sig, rawdata)
    {
        if(fnc == "MusicDB:Task")
        {
            let task  = rawdata.task;
            let state = rawdata.state;

            if(state == "notexisting")
                return;

            // Only consider tasks of a certain group
            if(this.selectorid != null)
            {
                if(task.annotations?.selectorid !== this.selectorid)
                    return;
            }

            // FIXME: May be a different file than a song file
            // FIXME: Check if this belongs to the expected album
            if(state == "readyforintegration")
            {
                this.albumfiles.push(task);
                let artistname  = task.annotations.artist;
                let albumname   = task.annotations.album;
                let releaseyear = task.annotations.releaseyear;

                // If there are valid artist and album names, update the settings table
                window.console?.log("Updating integration album settings table");
                if(typeof artistname === "string" || typeof albumname === "string")
                    this.albumsettingstable.Update(artistname, albumname, releaseyear);

                this.PrepareIntegrationTasks();
            }

            if(sig == "StateUpdate")
                return;
            else if(sig == "InternalError")
                return;
        }
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
    }
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

