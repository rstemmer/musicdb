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



class AlbumIntegrationProgress extends Layer
{
    // background: Instance of the Curtain class that lays behind the Layer.
    // When the layer is made visible, then also the background will be shown
    constructor(background)
    {
        super(background, "AlbumIntegrationProgress")
        // Headline
        this.headline = new LayerHeadline("Album Integration Tasks Execution Progress",
            "This is an overview of the files that will be copied into the Music Directory.");

        // Finish-Messages
        this.successmessage = new MessageBarConfirm("Copying the new album succeeded");
        this.errormessage   = new MessageBarError("An error occured while copying the new album");

        // Tool Bar
        this.toolbar     = new ToolBar();
        this.closebutton = new TextButton("Approve", "Close (Import later)",
            ()=>{this.onClick_Close();},
            "Close album integration layer. Import Album later.");
        this.importbutton = new TextButton("Import", "Continue with Import",
            ()=>{this.onClick_Import();},
            "Show the Album Import form for importing the uploaded album.");
        this.toolbar.AddSpacer(true); // grow
        this.toolbar.AddButton(this.closebutton);
        this.toolbar.AddButton(this.importbutton);

        this.tasks     = null;
        this.albumpath = null;
    }



    ResetUI()
    {
        this.RemoveChilds();

        this.closebutton.Disable();
        this.importbutton.Disable();
        this.successmessage.Hide();
        this.errormessage.Hide();

        this.AppendChild(this.headline);
        this.AppendChild(this.tasks);
        this.AppendChild(this.successmessage);
        this.AppendChild(this.errormessage);
        this.AppendChild(this.toolbar);
    }



    onClick_Close()
    {
        MusicDB_Request("FindNewContent", "ShowAlbumImport");   // Reload Album Import Settings View
        this.Hide();
    }

    onClick_Import()
    {
        // album path must be given via ExecuteTasks from the Integration layer
        if(typeof this.albumpath !== "string")
        {
            window.console?.warn("Cannot trigger import, no album path was known");
            return;
        }

        albumimportlayer.Show(); // Hand over to the overlay
        this.Hide();

        MusicDB_Request("FindAlbumSongFiles", "ShowAlbumImportLayer", {albumpath:this.albumpath});
    }



    // Required to trigger the import process
    SetAlbumPath(albumpath)
    {
        this.albumpath = albumpath;
    }


    // tasks: Album Integration Tasks object (type: BatchExecution)
    ExecuteTasks(tasks)
    {
        // Prepare Tasks for being executed
        this.tasks = tasks;
        this.tasks.SetListenSignature("ConfirmAlbumIntegrationTask");
        this.tasks.SetOnFinishCallback((opentasks, finishedtasks)=>{this.onFinish(opentasks, finishedtasks);});

        // Reset UI
        this.ResetUI();

        // And Fire
        this.Show();
        this.tasks.ExecuteTasks();
    }



    onFinish(opentasks, finishedtasks)
    {
        if(opentasks.length == 0)
        {
            this.successmessage.Show();
            this.importbutton.Enable();
            this.closebutton.Enable();
        }
        else
        {
            this.errormessage.Show();
            this.importbutton.Disable();
            this.closebutton.Enable();
        }
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        if(sig == "ConfirmAlbumIntegrationTask")
        {
            this.tasks?.onMusicDBMessage(fnc, sig, args, pass);
        }
    }
    onMusicDBNotification(fnc, sig, rawdata)
    {
        this.tasks?.onMusicDBNotification(fnc, sig, rawdata);
    }
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

