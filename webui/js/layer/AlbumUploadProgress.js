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



class AlbumUploadProgress extends Layer
{
    // background: Instance of the Curtain class that lays behind the Layer.
    // When the layer is made visible, then also the background will be shown
    constructor(background)
    {
        super(background, "AlbumUploadProgress")

        this.selectorid = null; // This ID is used as filter to only show uploads of a certain file group if not null

        // Headlines
        this.uploadheadline = new LayerHeadline("Album Files Upload",
            "This list shows the progress of the upload of all files of the selected ablum.");

        // Forms
        this.uploadstable = new UploadTable();

        // Tool Bar
        this.toolbar            = new ToolBar();
        this.cancelbutton       = new TextButton("MusicDB", "Cancel and Discard",
            ()=>{this.onClick_Cancel();},
            "Cancel album upload. Nothing will be changed. Partialy uploaded data will be removed.");
        this.integratebutton    = new TextButton("MusicDB", "Continue",
            ()=>{this.onClick_Integrate();},
            "Go to the integration layer to stores the uploaded files inside the music dicretory. After integration the album can be imported into MusicDB.");
        this.integratebutton.Disable();

        this.toolbar.AddButton(this.cancelbutton);
        this.toolbar.AddSpacer(true); // grow
        this.toolbar.AddButton(this.integratebutton);

        this.ResetUI();
    }



    ResetUI()
    {
        this.RemoveChilds();

        this.uploadstable.Clear();
        this.integratebutton.Disable();

        this.AppendChild(this.uploadheadline);
        this.AppendChild(this.uploadstable);
        this.AppendChild(this.toolbar);
    }



    // ID as specified for task.annotations.selectorid.
    // Only tasks with that ID will be considered in this view
    // null when upload progress of all upload tasks shall be shown
    SetSelectorFilter(selectorid)
    {
        this.selectorid = selectorid;
    }



    onClick_Cancel()
    {
        this.Hide();

        // Trigger removing partially uploaded files and cancel upload tasks
        let taskids = this.uploadstable.GetAllUploadIDs();
        for(let taskid of taskids)
            MusicDB_Call("RemoveUpload", {taskid: taskid});
        this.uploadstable.Clear();
    }

    onClick_Integrate()
    {
        this.Hide();
        albumintegrationlayer.Show();
    }



    // Check if all tasks are in readyforintegration state.
    // If so, enable the integrate-button
    ValidateCompleteness()
    {
        if(this.uploadstable.CheckCompleteness() == true)
            this.integratebutton.Enable();
        else
            this.integratebutton.Disable();
    }



    onMusicDBNotification(fnc, sig, data)
    {
        if(fnc == "MusicDB:Task")
        {
            let taskid = data.taskid;
            let task   = data.task;
            let state  = data.state;

            if(state == "notexisting")
                return;
            if(task.contenttype !== "albumfile")
                return;

            // Only consider tasks of a certain group
            if(this.selectorid != null)
            {
                if(task.annotations?.selectorid !== this.selectorid)
                    return;
            }

            if(sig == "ChunkRequest"
            || sig == "StateUpdate"
            || sig == "InternalError")
                this.uploadstable.UpdateRow(task);

            this.ValidateCompleteness();
            return;
        }
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
    }
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

