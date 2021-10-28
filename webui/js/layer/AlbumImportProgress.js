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
    constructor(background, id)
    {
        super(background, id)
        // Headline
        this.headline = new LayerHeadline("Album Import Tasks Execution Progress",
            "This is an overview of the Tasks that are executed to import the new album. "+
            "During import, the status of each task will be visualized.");

        // Finish-Messages
        this.successmessage = new MessageBarConfirm("Importing the new album succeeded");
        this.errormessage   = new MessageBarError("An error occured while importing the new album");
        this.successmessage.HideCloseButton();
        this.errormessage.HideCloseButton();

        // Tool Bar
        this.toolbar     = new ToolBar();
        this.closebutton = new TextButton("MusicDB", "Close",
            ()=>{this.onClick_Close();},
            "Cancel album import. Nothing will be changed.");
        this.toolbar.AddSpacer(true); // grow
        this.toolbar.AddButton(this.closebutton);
        this.toolbar.AddSpacer(true); // grow

        this.tasks = null;
    }



    onClick_Close()
    {
        this.Hide();
    }



    onExecutionFinished(success=true)
    {
        if(success)
            this.successmessage.Show();
        else
            this.errormessage.Show();
        this.closebutton.Enable();
    }



    // tasks: AlbumImportTasks object
    ExecuteTasks(tasks)
    {
        // Reset UI
        this.RemoveChilds();
        this.closebutton.Disable();
        this.successmessage.Hide();
        this.errormessage.Hide();

        // Prepare Tasks for being executed
        this.tasks = tasks;
        this.tasks.SetListenSignature("ConfirmAlbumImportTask");
        this.tasks.SetOnFinishCallback((opentasks, finishedtasks)=>{this.onFinish(opentasks, finishedtasks);});

        // Rebuild UI
        this.AppendChild(this.headline);
        this.AppendChild(this.tasks);
        this.AppendChild(this.successmessage);
        this.AppendChild(this.errormessage);
        this.AppendChild(this.toolbar);

        // And Fire
        this.Show();
        this.tasks.ExecuteTasks();
    }



    onFinish(opentasks, finishedtasks)
    {
        if(opentasks.length == 0)
            this.successmessage.Show();
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
    }
    onMusicDBNotification(fnc, sig, rawdata)
    {
        this.tasks?.onMusicDBNotification(fnc, sig, rawdata);
    }
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

