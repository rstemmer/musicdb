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

const TASKTABLEHEADLINE = ["Type", "Status", "Start Time", "Last Update", "Actions"];
const TT_TYPE_COLUMN    = 0;
const TT_STATUS_COLUMN  = 1;
const TT_START_COLUMN   = 2;
const TT_UPDATE_COLUMN  = 3;
const TT_ACTIONS_COLUMN = 4;



class TaskTableRowBase extends TableRow
{
    constructor()
    {
        super(TASKTABLEHEADLINE.length, ["TaskTableRow"]);
    }
}


class TaskTableHeadline extends TaskTableRowBase
{
    constructor()
    {
        super();
        this.AddCSSClass("TableHeadline");

        for(let cellnum in TASKTABLEHEADLINE)
        {
            let headline = new Element("span");
            headline.SetInnerText(TASKTABLEHEADLINE[cellnum]);
            this.SetContent(cellnum, headline);
        }
    }
}


class TaskTableRow extends TaskTableRowBase
{
    // validationstatuscallback if a function called whenever data is validated.
    // It gets one argument (boolean) that, if true, tells that all data in this table is valid.
    constructor(task)
    {
        super();
        this.Update(task);
    }



    Update(task)
    {
        const contenticonmap = {video:     "VideoFile",
                                artwork:   "ArtworkFile",
                                albumfile: "AlbumFile",
                                any:       "MusicDB"};

        let taskid    = task.id;
        let mimetype  = task.mimetype;    // audio/*, video/*, image/*, …
        let content   = task.contenttype; // artwork, video, albumfile
        let taskstate = task.state;
        let inittime  = task.initializationtime;
        let updatetime= task.updatetime;

        let statuselement = new TaskStatusText(taskstate);

        let contentelement = new Element("div", ["flex", "flex-row", "flex-middle"]);
        let contenticon    = new SVGIcon(contenticonmap[content]);
        let contentname    = new Element("span");
        contenticon.SetTooltip(`Task ID: ${taskid}`);
        contentname.SetInnerText(content);
        contentelement.AppendChild(contenticon);
        contentelement.AppendChild(contentname);

        let starttimeelement = new Element("span");
        starttimeelement.SetInnerText(new Date(inittime * 1000).toLocaleString());

        let updatetimeelement = new Element("span");
        let updatetimetext    = new Date(updatetime * 1000).toLocaleString();
        let currenttime       = Math.floor(Date.now() / 1000);
        let timediff          = currenttime - updatetime; // How long ago is the last update?
        let age               = Math.floor(timediff / 60);; // in full minutes

        if(age > 10) // older than 10 minute
            updatetimeelement = new StatusText(`${age} min ago`, "warn") // Narrow no-break space
        else
            updatetimeelement = new StatusText(`${age} min ago`, "good")

        let buttonbox = new ButtonBox();
        if(content == "albumfile" && taskstate == "readyforintegration")
            buttonbox.AddButton(new SVGButton("Integrate", ()=>{this.onIntegrateAlbumFile(task);}, "Integrate this file into the Music Directory."));
        buttonbox.AddButton(new SVGButton("Remove", ()=>{this.onRemoveTask(task);}, "Remove task and delete temporary data."));

        // Set Cell Content
        this.SetContent(TT_TYPE_COLUMN   , contentelement);
        this.SetContent(TT_STATUS_COLUMN , statuselement);
        this.SetContent(TT_START_COLUMN  , starttimeelement);
        this.SetContent(TT_UPDATE_COLUMN    , updatetimeelement);
        this.SetContent(TT_ACTIONS_COLUMN, buttonbox);
    }



    onRemoveTask(task)
    {
        this.Hide(); // be responsive and already hide even if the task got not yet removed.
        MusicDB.Call("RemoveUpload", {taskid: task.id});
    }

    onIntegrateAlbumFile(task)
    {
        let albumintegrationlayer = WebUI.GetLayer("AlbumIntegration");
        albumintegrationlayer.ResetUI();
        albumintegrationlayer.Integrate(task);
        albumintegrationlayer.Show();
    }
}



class TaskTable extends Table
{
    constructor()
    {
        super(["TaskTable"]);

        this.tasks = new Object();

        // Table
        this.headlinerow = new TaskTableHeadline();
        this.AddRow(this.headlinerow);
    }



    AddNewTask(task)
    {
        let row = new TaskTableRow(task);
        this.AddRow(row);
        this.tasks[task.id] = row;
    }

    RemoveTask(task)
    {
        let taskid = task.id;
        this.RemoveRow(this.tasks[taskid]);
        delete this.tasks[taskid];
    }



    GetTaskIDs()
    {
        return Object.keys(this.tasks);
    }



    UpdateTask(task)
    {
        let taskid = task.id;
        let state  = task.state;

        if(state === "remove")
            this.RemoveTask(task);
        else if(!(taskid in this.tasks))
            this.AddNewTask(task);
        else
            this.tasks[taskid].Update(task);
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

