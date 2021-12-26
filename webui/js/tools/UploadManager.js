// MusicDB,  a music manager with web-bases UI that focus on music.
// Copyright (C) 2017-2021  Ralf Stemmer <ralf.stemmer@gmx.net>
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
/*
 *
 * This manager handled uploading data.
 *
 * When an upload gets started, an data ID is generated by this script.
 * Together with other meta data, an Upload-Request gets send to the MusicDB Server.
 * The server then requests chunks of the data.
 *
 * After a chunk of data is sent, a notification within a certain time gets expected by this upload manager.
 * This notification contains a state and request of the next chunk.
 *
 */

class UploadManager
{
    constructor()
    {
        this.uploads = new Object;
        this.videouploads      = new UploadTable();
    }



    GetVideoUploadsTable()
    {
        return this.videouploads;
    }



    // initialannotations: an object with initial annotations
    UploadFile(contenttype, filedescription, initialannotations=null)
    {
        let reader = new FileReader();

        reader.onload = (event)=>
            {
                let contents = event.target.result;
                this.StartUpload(contenttype, filedescription, new Uint8Array(contents), initialannotations);
            };
        reader.readAsArrayBuffer(filedescription);
    }



    // This method returns the generated task ID (task.id)
    async StartUpload(contenttype, filedescription, rawdata, initialannotations=null)
    {
        
        // ! SHA-1 is used as ID and object key in the server and client because it is short.
        // Furthermore it is used to check if the upload was successful.
        // It is not, and never should be, used for security relevant tasks
        let checksum  = BufferToHexString(await crypto.subtle.digest("SHA-1", rawdata));
        let task      = new Object();
        task.id       = checksum;
        task.data     = rawdata;
        task.filesize = rawdata.length;
        task.offset   = 0;
        task.contenttype = contenttype;
        task.mimetype = filedescription.type;
        task.checksum = checksum;
        task.filename = filedescription.name
        this.uploads[task.id] = task;
        
        MusicDB_Request("InitiateUpload",
            "UploadingContent",
            {
                taskid:   task.id,
                mimetype: task.mimetype,
                contenttype: task.contenttype,
                filesize: task.filesize,
                checksum: task.checksum,
                filename: task.filename
            },
            {contenttype: task.contenttype});

        if(typeof initialannotations === "object" && initialannotations !== null)
            MusicDB_Call("AnnotateUpload", {taskid: task.id, ...initialannotations});

        window.console && console.log(task);
        return task.id;
    }


    UploadNextChunk(state)
    {
        window.console && console.log("UploadNextChunk");
        let taskid    = state.taskid;
        let task      = this.uploads[taskid]
        let rawdata   = task.data.subarray(task["offset"], task["offset"] + state.chunksize)
        //let chunkdata = btoa(rawdata); // FIXME: Does not work. rawdata will be implicit converted to string
        let chunkdata = BufferToHexString(rawdata)
        task.offset  += rawdata.length;

        window.console && console.log(task);
        MusicDB_Call("UploadChunk", {taskid: taskid, chunkdata: chunkdata});
    }



    onMusicDBNotification(fnc, sig, data)
    {
        if(fnc == "MusicDB:Task")
        {
            window.console?.log(data);
            let state = data.state;
            if(state === "notexisting")
            {
                window.console?.warn(`MusicDB:Task notification for task in "notexisting" state`);
                if(sig == "InternalError")
                    window.console?.warn(`The same task came with the message: "${data.message}"`);
                return;
            }

            // Get information of the task that caused this notification
            let taskid      = data.taskid;
            let task        = data.task;
            let contenttype = task.contenttype;

            // Only process task, if this client is the owner of the task
            if(typeof this.uploads[taskid] === "undefined")
                return;

            if(sig == "ChunkRequest")
            {
                if(contenttype == "video")
                    this.videouploads.UpdateRow(task);
                this.UploadNextChunk(data)
            }
            else // "StateUpdate", "InternalError"
            {
                //this.videouploads.Update(data.uploadslist.videos);
            }

            if(sig == "StateUpdate")
            {
                window.console?.info(`Stateupdate for ${contenttype} to ${state}`);
                // Import artwork
                if(contenttype == "artwork")
                {
                    if(state == "readyforintegration")
                    {
                        let musicpath = task.annotations.musicpath;
                        MusicDB_Call("InitiateContentIntegration", {taskid: taskid, musicpath: musicpath});
                    }
                }

                // Remove tasks of this client from the list of active tasks when they are done
                if(state === "remove")
                {
                    delete this.uploads[taskid];
                }
            }
        }
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        return;
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

