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

const TASKTABLEHEADLINE = ["Type", "Status", "Start time", "Running time", "Actions"];
const TT_TYPE_COLUMN    = 0;
const TT_STATUS_COLUMN  = 1;
const TT_START_COLUMN   = 2;
const TT_AGE_COLUMN     = 3;
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
                                albumfile: "AlbumFile"};

        let taskid    = task.id;
        let mimetype  = task.mimetype;    // audio/*, video/*, image/*, …
        let content   = task.contenttype; // artwork, video, albumfile
        let taskstate = task.state;

        let statuselement = new TaskStatusText(taskstate);
        let contenticon   = new SVGIcon(contenticonmap[content]);
        contenticon.SetTooltip(`Task ID: ${taskid}`);

        // Set Cell Content
        this.SetContent(TT_TYPE_COLUMN   , contenticon);
        this.SetContent(TT_STATUS_COLUMN , statuselement);
        //this.SetContent(TT_START_COLUMN  , this.);
        //this.SetContent(TT_AGE_COLUMN    , this.);
        //this.SetContent(TT_ACTIONS_COLUMN, this.);
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



    Update(tasks)
    {
        let alltasks = [...tasks.albumfiles, ...tasks.videos, ...tasks.artworks];
        for(let task of alltasks)
            this.UpdateTask(task);
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

