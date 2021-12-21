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

class TaskListView extends MainSettingsView
{
    constructor()
    {
        let title = "Open and Running MusicDB Tasks";
        let descr = "A list of tasks that are currently processed by the MusicDB server. Tasks can be cancled or further processing steps triggered.";
        super("TaskListView", title, descr);
        let headline = new SettingsHeadline(title, descr);

        this.ResetUI();
    }



    ResetUI()
    {
        this.RemoveChilds();

        this.tasktable     = new TaskTable();
        this.taskgroups    = new Object();
        this.taskcache     = new Object();
        this.groupelements = new Object();

        this.AppendChild(this.headline);
        this.AppendChild(this.tasktable);
    }



    // Group Type: for now only "album"
    CreateNewGroup(groupid, grouptype)
    {
        if(grouptype != "album")
            return;

        // Headline
        let headline = new SettingsHeadline(`Temporary Album`,
            `The following table lists all open tasks for the temporaty album with the ID ${groupid}`);

        // Tool bar for remove and integrate
        let removebutton    = new SVGButton("Remove", ()=>{this.onRemoveGroup(groupid);},
            "Remove all tasks and delete all temporary data of this temporary album.");
        let integratebutton = new SVGButton("MusicDB", ()=>{this.onIntegrateGroup(groupid);},
            "Try to integrate all files of this temprary album into the Music Directory.");

        let toolbar = new ToolBar();
        toolbar.AddButton(new ToolGroup([integratebutton]));
        toolbar.AddSpacer(true /*expand*/);
        toolbar.AddButton(new ToolGroup([removebutton]));

        // Table
        let newtable = new TaskTable();
        this.taskgroups[groupid] = newtable;

        // Append to view
        this.AppendChild(headline);
        this.AppendChild(newtable);
        this.AppendChild(toolbar);

        this.groupelements[groupid] = new Object();
        this.groupelements[groupid].headline = headline;
        this.groupelements[groupid].table    = newtable;
        this.groupelements[groupid].toolbar  = toolbar;
    }



    onRemoveGroup(groupid)
    {
        let taskids = this.taskgroups[groupid].GetTaskIDs();
        for(let taskid of taskids)
            MusicDB_Call("RemoveUpload", {taskid: taskid});
    }

    onIntegrateGroup(groupid)
    {
        let taskids = this.taskgroups[groupid].GetTaskIDs();
        albumintegrationlayer.ResetUI();
        for(let taskid of taskids)
        {
            let task = this.taskcache[taskid];
            if(task.state == "readyforintegration")
                albumintegrationlayer.Integrate(task);
        }
        albumintegrationlayer.Show();
    }



    UpdateTaskGroups(task)
    {
        let groupid = task.annotations.groupid;

        if(typeof groupid !== "string")
            return;

        if(!(groupid in this.taskgroups))
        {
            if(task.state == "remove") // When the task shall be removed anyway, just ignore it
                return;

            if(task.contenttype === "albumfile")
                this.CreateNewGroup(groupid, "album");
            else
                return;
        }

        this.taskgroups[groupid].UpdateTask(task);

        // Remove empty groups
        let taskids = this.taskgroups[groupid].GetTaskIDs();
        if(taskids.length === 0)
        {
            this.RemoveChild(this.groupelements[groupid].headline);
            this.RemoveChild(this.groupelements[groupid].table   );
            this.RemoveChild(this.groupelements[groupid].toolbar );
            delete this.groupelements[groupid];
        }
    }



    UpdateTask(task)
    {
        // Update UI
        this.tasktable.UpdateTask(task);
        this.UpdateTaskGroups(task);

        // Cache task
        let taskid = task.id;
        let state  = task.state;
        if(state == "remove" && (taskid in this.taskcache))
            delete this.taskcache[taskid];
        else
            this.taskcache[taskid] = task;
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        if(fnc == "GetCurrentTasks" && sig == "ShowCurrentTasks")
        {
            this.ResetUI();
            let alltasks = [...args.albumfiles, ...args.videos, ...args.artworks];
            for(let task of alltasks)
                this.UpdateTask(task);
        }
        return;
    }

    onMusicDBNotification(fnc, sig, data)
    {
        if(fnc == "MusicDB:Task" && sig == "StateUpdate")
        {
            this.UpdateTask(data.task);
        }
        return;
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

