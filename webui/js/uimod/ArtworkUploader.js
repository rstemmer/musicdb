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


class ArtworkUploader extends Element
{
    // musictype: "album", "video"
    constructor(musictype, musicpath, musicid)
    {
        super("div", ["ArtworkUploader", "flex-column", "flex-grow"]);
        this.musicid = musicid;

        let annotations = new Object();
        annotations["musictype"] = musictype;
        annotations["musicpath"] = musicpath;
        annotations["musicid"  ] = musicid;

        this.listenontaskid = null;

        this.fileselect = new ArtworkFileSelect("Select Artwork File", "Select an artwork file (.jpg) form your local computer.", annotations);
        let  statustext = new StatusText(); // Empty UploadStatusText as place holder

        this.AppendChild(this.fileselect);
        this.AppendChild(statustext);
    }



    UpdateUploadStatus(uploadstatus)
    {
        // it is not important that the uploaded temporary file got removed
        if(uploadstatus == "remove")
            return;

        let  statustext = new UploadStatusText(uploadstatus);
        this.RemoveChilds();
        this.AppendChild(this.fileselect);
        this.AppendChild(statustext);

        if(uploadstatus == "importcomplete")
        {
            let messagebar = new MessageBarInfo(`Artwork successfully replaced. You may have to reload the WebUI to update the Browser\'s cache.`);
            messagebar.Show();
            this.AppendChild(messagebar);
        }
        else if (uploadstatus == "importfailed")
        {
            let messagebar = new MessageBarError(`Importing Artwork failed!`);
            messagebar.Show();
            this.AppendChild(messagebar);
        }
    }



    // upload: raw data from the notification
    ShowErrorStatus(upload)
    {
        let state   = upload.state;
        let message = upload.message;

        let messagebar = new MessageBarError(`Replacing Artwork failed with error: ${message}.`);
        messagebar.Show();

        this.UpdateUploadStatus(state);
        this.AppendChild(messagebar);
    }



    onMusicDBNotification(fnc, sig, rawdata)
    {
        if(fnc == "MusicDB:Upload")
        {
            let task  = rawdata.uploadtask;
            let state = rawdata.state;

            if(this.listenontaskid !== task.id)
                return;

            if(sig == "StateUpdate")
                this.UpdateUploadStatus(state);
            else if(sig == "InternalError")
                this.ShowErrorStatus(rawdata);
        }
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        if(fnc == "InitiateUpload" && sig == "UploadingContent")
        {
            let task = pass.task;
            if(task.contenttype != "artwork")
                return;

            this.listenontaskid = task.id;  // TODO: Should be args, needs to be refactored in the back-end
        }
        else if(fnc == "InitiateArtworkImport" && sig == "ImportingArtwork")
        {
            let taskid      = args;
            let annotations = pass.annotations;
            let musicid     = annotations.musicid;

            if(musicid !== this.musicid)
                return;

            this.listenontaskid = taskid;
        }
        return;
    }
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

