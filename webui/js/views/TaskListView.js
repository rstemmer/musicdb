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
        super("TaskListView", "Open and Running MusicDB Tasks",
            "A list of tasks that are currently processed by the MusicDB server. Tasks can be cancled or further processing steps triggered.");

        this.tasktable = new TaskTable();

        this.AppendChild(this.tasktable);
    }



    UpdateView(tasks)
    {
        this.tasktable.Update(tasks);
        return;
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        if(fnc == "GetCurrentTasks" && sig == "ShowCurrentTasks")
        {
            window.console?.log(args);
            this.UpdateView(args);
        }
        return;
    }

    onMusicDBNotification(fnc, sig, rawdata)
    {
        return;
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

