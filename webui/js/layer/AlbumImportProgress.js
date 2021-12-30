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



class AlbumImportProgress extends Layer
{
    // background: Instance of the Curtain class that lays behind the Layer.
    // When the layer is made visible, then also the background will be shown
    constructor(background)
    {
        super(background, "AlbumImportProgress")
        // Headline
        this.headline = new LayerHeadline("Album Import Tasks Execution Progress",
            "This is an overview of the Tasks that are executed to import the new album. "+
            "During import, the status of each task will be visualized.");

        // Finish-Messages
        this.successmessage = new MessageBarConfirm("Importing the new album succeeded.");
        this.errormessage   = new MessageBarError("An error occured while importing the new album. (See server logs for detail. Sorry.)");

        // Tool Bar
        this.toolbar     = new ToolBar();
        this.closebutton = new TextButton("Approve", "Close (Change Settings Later)",
            ()=>{this.onClick_Close();},
            "Cancel album import. Nothing will be changed. Tags and colors can be updated later in the Album View");
        this.settingsbutton = new TextButton("Settings", "Change Album Settings",
            ()=>{this.onClick_Settings();},
            "Open Setting layer to set genre tags and update the color scheme or upload a new artwork.");
        this.toolbar.AddSpacer(true); // grow
        this.toolbar.AddButton(this.closebutton);
        this.toolbar.AddSpacer(true); // grow
        this.toolbar.AddButton(this.settingsbutton);

        this.tasks   = null;
        this.albumid = null;
    }



    onClick_Close()
    {
        MusicDB_Request("FindNewContent", "ShowAlbumImport");   // Reload Album Import Settings View
        this.Hide();
    }

    onClick_Settings()
    {
        MusicDB_Request("GetAlbum", "ShowSongsSettingsLayer", {albumid: this.albumid});
        this.Hide();
    }



    // tasks: AlbumImportTasks object
    ExecuteTasks(tasks)
    {
        // Reset UI
        this.RemoveChilds();
        this.closebutton.Disable();
        this.settingsbutton.Disable();
        this.successmessage.Hide();
        this.errormessage.Hide();
        this.errormessage.SetData("messagetype", "error");
        this.albumid = null;

        // Prepare Tasks for being executed
        this.tasks = tasks;
        this.tasks.SetListenSignature("ConfirmAlbumImportTask");
        this.tasks.SetOnFinishCallback((opentasks, finishedtasks)=>{this.onFinish(opentasks, finishedtasks);});

        // Rebuild UI
        this.AppendChild(this.headline);
        this.AppendChild(this.tasks);
        this.AppendChild(this.errormessage);
        this.AppendChild(this.successmessage);
        this.AppendChild(this.toolbar);

        // And Fire
        this.Show();
        this.tasks.ExecuteTasks();
    }



    onFinish(opentasks, finishedtasks)
    {
        if(opentasks.length == 0)
        {
            this.successmessage.Show();
            // It can happen that some tasks failed that are allowed to fail. Then errors are just a warning.
            this.errormessage.SetData("messagetype", "warning");
        }
        else
            this.errormessage.Show();
        this.closebutton.Enable();
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        if(sig == "ConfirmAlbumImportTask")
        {
            window.console?.log(args);
            window.console?.log(pass);
            this.tasks?.onMusicDBMessage(fnc, sig, args, pass);
        }

        if(fnc == "Bounce" && sig == "InformAlbumImportProgressLayer")
        {
            window.console?.log(`Bounce:InformAlbumImportProgressLayer`);
            window.console?.log(args);
            this.albumid = args.albumid;
            this.settingsbutton.Enable();
        }
    }
    onMusicDBNotification(fnc, sig, rawdata)
    {
        this.tasks?.onMusicDBNotification(fnc, sig, rawdata);
    }
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

