// MusicDB,  a music manager with web-bases UI that focus on music.
// Copyright (C) 2017-2020  Ralf Stemmer <ralf.stemmer@gmx.net>
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

class QueueView
{
    constructor()
    {
        this.element = document.createElement("div");
        this.element.classList.add("QueueView");
    }



    GetHTMLElement()
    {
        return this.element;
    }



    // musictype: "audio" or "video"
    Update(musictype, MDBQueue)
    {
        // Reset timer
        if(MDBQueue[0].song !== undefined)
        {
            queuetimemanager.ClearTime("audio");
        }
        else if(MDBQueue[0].video !== undefined)
        {
            queuetimemanager.ClearTime("video");
        }

        this.element.innerHTML = "";
        let queueposition      = 0;
        for(let entry of MDBQueue)
        {
            let entryid     = entry.entryid;
            let MDBAlbum    = entry.album;
            let MDBArtist   = entry.artist;
            let MDBMusic    = null;
            if(musictype == "audio")
                MDBMusic    = entry.song;
            else if(musictype == "video")
                MDBMusic    = entry.video;
            else
                continue;   // No song and no video? Should never happen, but who knows…

            // Update timer
            queuetimemanager.AddTime(musictype, MDBMusic.playtime);
            
            // Create Entry
            let buttonbox   = new ButtonBox_QueueEntryControls(musictype, MDBMusic.id, entryid);
            let dropzone    = new QueueDropZone(entryid);
            let tile        = null;
            if(musictype == "audio")
            {
                tile        = new SongQueueTile(MDBMusic, MDBAlbum, MDBArtist, entryid, queueposition, buttonbox);
            }
            else if(musictype == "video")
            {
                tile        = new VideoQueueTile(MDBMusic, MDBArtist, entryid, queueposition, buttonbox);
            }
            else
                continue;   // No song and no video? Should never happen, but who knows…

            this.element.appendChild(tile.GetHTMLElement());
            this.element.appendChild(dropzone.GetHTMLElement());
            queueposition += 1;
        }
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        if(fnc == "GetSongQueue" && sig == "ShowSongQueue")
        {
            let mainviewbox = document.getElementById("RightContentBox"); // \_ HACK
            mainviewbox.innerHTML = "";
            mainviewbox.appendChild(queueview.GetHTMLElement());           // /  This should do a Main View Manager
            this.Update("audio", args);
        }
        else if(fnc == "GetVideoQueue" && sig == "ShowVideoQueue")
        {
            let mainviewbox = document.getElementById("RightContentBox"); // \_ HACK
            mainviewbox.innerHTML = "";
            mainviewbox.appendChild(queueview.GetHTMLElement());           // /  This should do a Main View Manager
            this.Update("video", args);
        }
    }
}





class QueueDropZone extends DropTarget
{
    constructor(entryid)
    {
        super();
        this.element    = document.createElement("div");
        this.element.classList.add("QueueTile");
        this.element.classList.add("QueueDropZone");
        
        this.entryid    = entryid;

        this.BecomeDropTarget();
    }



    GetHTMLElement()
    {
        return this.element;
    }



    onTransfer(draggableid)
    {
        let draggable = document.getElementById(draggableid);
        let entryid   = draggable.dataset.entryid;
        let musictype = draggable.dataset.musictype;
        let musicid   = draggable.dataset.musicid;
        let droptask  = draggable.dataset.droptask;

        switch(droptask)
        {
            case "move":
                if(entryid == this.entryid)
                    break;

                if(musictype == "song")
                    MusicDB_Call("MoveSongInQueue", {entryid:entryid, afterid:this.entryid});
                else if(musictype == "video")
                    MusicDB_Call("MoveVideoInQueue", {entryid:entryid, afterid:this.entryid});
                break;

            case "insert":
                if(musictype == "song")
                {
                    window.console && console.log("MusicDB_Call(\"AddSongToQueue\", {videoid: "+musicid+", position:"+this.entryid+");");
                }
                else if(musictype == "video")
                {
                    window.console && console.log("MusicDB_Call(\"AddVideoToQueue\", {videoid: "+musicid+", position:"+this.entryid+");");
                }
                window.console && console.warn("The back-end does not support this featred yet");
                break;

        }
    }
}


/*
 * This class provides the artistloader.
 * It is possible to select a set of genres and/or to reload the artists-list
 *
 * Requirements:
 *   - JQuery
 *   - mdb_queue.css
 *   - mdbstate.js (for timing)
 * Show:
 *   - ShowQueue(parentID)
 * Functions:
 * Callbacks:
 * Recommended Paths:
 * Trigger: (fnc -> sig)
 *
 */

function ShowQueue(parentID, MDBQueue)
{
    let html = "";

    // Reset timer
    if(MDBQueue[0].song !== undefined)
    {
        queuetimemanager.ClearTime("audio");
    }
    else if(MDBQueue[0].video !== undefined)
    {
        queuetimemanager.ClearTime("video");
    }

    html += "<div class=QueueView>"; // main box
    for(let pos in MDBQueue)
    {
        let entryid     = MDBQueue[pos].entryid;
        let MDBAlbum    = MDBQueue[pos].album;
        let MDBArtist   = MDBQueue[pos].artist;

        let MDBMusic    = null;
        let queuetype   = null;
        if(MDBQueue[pos].song !== undefined)
        {
            MDBMusic  = MDBQueue[pos].song;
            queuetype = "audio"
        }
        else if(MDBQueue[pos].video !== undefined)
        {
            MDBMusic  = MDBQueue[pos].video;
            queuetype = "video"
        }
        else
            continue;   // No song and no video? Should never happen, but who knows…

        // Update timer
        queuetimemanager.AddTime(queuetype, MDBMusic.playtime);
        
        // Create Entry

        let buttonbox = Button_QueueEntryControls(MDBMusic.id, entryid, pos, queuetype);

        html += "<div";
        html += " id=Q_drag_" + pos;
        html += " class=\"Q_entry\"";
        html += " draggable=\"true\"";
        html += " data-pos=\""     + pos         + "\"";
        html += " data-musicid=\"" + MDBMusic.id + "\"";
        html += " data-entryid=\"" + entryid     + "\"";
        html += " data-musictype=\"" + queuetype + "\"";
        html += ">";
        if(queuetype == "audio")
            html += CreateSongTile(MDBMusic, MDBAlbum, MDBArtist, buttonbox)
        else if(queuetype == "video")
            html += CreateVideoTile(MDBMusic, MDBAlbum, MDBArtist, buttonbox)
        html += "</div>";

        html += "<div";
        html += " id=Q_drop_" + pos;
        html += " class=\"Q_separator\"";
        html += " data-entryid=\"" + entryid + "\"";
        html += "></div>";
    }
    
    html += "</div>"; // main box

    // Create Element
    $("#"+parentID).html(html);
    UpdateStyle();


    // make all dropentrys useful by adding event handler to them
    let dropelement = ".Q_separator";
    let dragelement = ".Q_entry";

    $(dropelement).on("dragover", function(e){
        e.preventDefault();
        //e.originalEvent.dataTransfer.dropEffect = 'move';
    });
    $(dropelement).on("dragenter", function(e){
        e.preventDefault();
        $(this).addClass("Q_hldropzone");
    });
    $(dropelement).on("dragleave", function(e){
        e.preventDefault();
        $(this).removeClass("Q_hldropzone");
    });
    $(dropelement).on("drop", function(e){
        e.preventDefault();
        $(this).removeClass("Q_hldropzone");

        let attrid    = "#" + e.target.id;
        let dstpos    = $(attrid).attr("data-entryid");
        let srcpos    = e.originalEvent.dataTransfer.getData("srcpos");
        let musicid   = e.originalEvent.dataTransfer.getData("musicid");
        let musictype = e.originalEvent.dataTransfer.getData("musictype");

        if(musictype == "video")
            MusicDB_Call("MoveVideoInQueue", {entryid:srcpos, afterid:dstpos});
        else if(musictype == "audio")
            MusicDB_Call("MoveSongInQueue", {entryid:srcpos, afterid:dstpos});
        else
            window.console && console.log("Unknown music type"+musictype);
    });

    // the entries itself need some DnD-handler too
    $(dragelement).on("dragstart", function(e){
        e.target.style.opacity = "0.5";

        // get data needed for queue-move and set it as dataTransfer
        let attrid = "#" + e.originalEvent.originalTarget.id;

        let entryid   = $(attrid).attr("data-entryid");
        let musicid   = $(attrid).attr("data-musicid");
        let musictype = $(attrid).attr("data-musictype");

        // Set data that will be transferred (mandatory to make DnD work)
        e.originalEvent.dataTransfer.setData("srcpos",    entryid);
        e.originalEvent.dataTransfer.setData("musicid",   musicid);
        e.originalEvent.dataTransfer.setData("musictype", musictype);
    });
    $(dragelement).on("dragend", function(e){
        e.target.style.opacity = "1.0";
    });
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

