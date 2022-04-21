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


// BatchExecution extends StatusList but it can also be used
// without making use of the visual components.
class BatchExecution extends StatusList
{
    constructor()
    {
        super();
        this.tasks         = new Array();
        this.idseed        = 1;
        this.currenttask   = null;
        this.finishedtasks = new Array();
        this.connected     = false; // Indicate if connection to MusicDB server is established
    }



    // taskfunction and resultevalfunction, notificationfunction
    // must be a function that returns a new status as handled by StatusElementBase.SetStatus
    // If null gets returned, the state will not changed and nothing else will be done.
    //   Be careful and use this only to ignore unexpected calls (like with an unexpected task ID)
    //
    // taskfunction gets an argument webtaskid that can be used as pass argument to a request with a certain signature.
    // resultsevalfunction gets the typical fnc,sif,args,pass arguments to evaluate if the tasks was successful
    // notificationfunction gets the typical fnc,sif,rawdata arguments to evaluate if the tasks was successful
    //
    // When canfail is true, then the batch execution won't stop when the status of the task becomes "bad"
    // So if canfail is true, status "good" and "bad" leads to executing the next task.
    // Otherwise only a status of "good".
    //
    // Returns: the new created task object
    AddTask(htmllabel, taskfunction, resultevalfunction, notificationfunction=null, canfail=false)
    {
        let task = new Object();
        task["webuitaskid"]          = this.idseed++;
        task["statuselement"]        = new StatusItem(htmllabel, "open");
        task["taskfunction"]         = taskfunction;
        task["resultevalfunction"]   = resultevalfunction;
        task["notificationfunction"] = notificationfunction;
        task["canfail"]              = canfail;
        task["lastmessage"]          = null; // Last message from a task that is not null.

        this.tasks.push(task);
        this.AppendChild(task["statuselement"]);
        return task;
    }



    SetListenSignature(signature)
    {
        this.listensignature = signature;
    }



    Clear()
    {
        this.tasks         = new Array();
        this.finishedtasks = new Array();
        this.currenttask   = null;
        this.RemoveChilds();
    }



    // The callback gets called when all tasks have been processed
    // or when the processing has been stopped due to an error.
    // The callback gets two parameter: A list of all finished tasks, and a list of all left tasks.
    //   callback(opentasks, finishedtasks)
    SetOnFinishCallback(onfinishcallback)
    {
        this.onfinishcallback = onfinishcallback;
    }



    ExecuteTasks()
    {
        if(this.tasks.length <= 0)
        {
            if(typeof this.onfinishcallback === "function")
                this.onfinishcallback(this.tasks, this.finishedtasks);
            return;
        }

        this.currenttask = this.tasks[0];
        this.tasks       = this.tasks.splice(1);

        let state = "unknown";
        if(typeof this.currenttask["taskfunction"] === "function")
            state = this.currenttask["taskfunction"](this.currenttask["webuitaskid"]);

        this.UpdateState(state);
    }



    UpdateState(newstate, forcenexttask)
    {
        if(newstate === null)
            return;
        if(this.currenttask === null)
            return;

        this.currenttask["statuselement"].SetState(newstate);

        if(newstate == "bad")
        {
            // The task failed.
            window.console?.warn("Finished task returned status \"bad\". Batch execution will be stopped.");
            // Because the current task is left open (as it failed), this needs to be considered as parameter
            //   for the open tasks list as well.
            if(typeof this.onfinishcallback === "function")
                this.onfinishcallback([this.currenttask, ...this.tasks], this.finishedtasks);
        }

        if(newstate == "good"
        || (newstate == "bad" && this.currenttask["canfail"] == true)
        || forcenexttask === true
        )
        {
            // This task has now finished. Continue with the next task.
            this.finishedtasks.push(this.currenttask);
            this.currenttask = null;
            this.ExecuteTasks();
        }
        return;
    }



    onConnectionLost()
    {
        // Do nothing if already in disconnected-state
        if(!this.connected)
            return;

        this.connected = false;
        this.UpdateState("warn");
        window.console?.warn("Connection to MusicDB WebSocket Server lost. Batch execution stalled.");
    }



    onReconnect()
    {
        if(this.connected)
        {
            window.console?.error(`Unexpected reconnection. Connected-state was ${this.connected}.`);
            return;
        }

        this.connected = true;
        this.UpdateState("warn", true /*Force next task*/);
        // The next task needs to be forced because the notification of the task being finished
        // may be lost due to the connection issue.
        window.console?.info("Connection to MusicDB WebSocket Server established. Batch execution continued.");
    }



    onNotification(fnc, sig, rawdata)
    {
        if(this.currenttask == null)
            return;

        let state = null;
        if(typeof this.currenttask["notificationfunction"] === "function")
            state = this.currenttask["notificationfunction"](fnc, sig, rawdata);
        if(typeof rawdata?.message === "string")
            this.currenttask["lastmessage"] = rawdata.message;

        this.UpdateState(state);
    }



    onExecutionFinished(fnc, sig, args, pass)
    {
        if(this.currenttask == null)
            return;

        if(pass?.webuitaskid != this.currenttask["webuitaskid"])
        {
            window.console?.error("onExecutionFinished event unexpected task was triggered.");
            return;
        }

        let state = null;
        if(typeof this.currenttask["resultevalfunction"] === "function")
            state = this.currenttask["resultevalfunction"](fnc, sig, args, pass);

        this.UpdateState(state);
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        if(sig == this.listensignature)
        {
            this.onExecutionFinished(fnc, sig, args, pass);
        }
    }

    onMusicDBNotification(fnc, sig, rawdata)
    {
        this.onNotification(fnc, sig, rawdata);
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

