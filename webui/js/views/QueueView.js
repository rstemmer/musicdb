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

class QueueView extends Element
{
    constructor()
    {
        super("div", ["QueueView"]);
        this.streamviewmount = new Element("div");
        this.numberofentries = 0;
    }



    MountStreamView(streamview)
    {
        let backbutton = new SVGButton("ToMainView", ()=>
            {
                streamview.ShowInMainView();
            });
        backbutton.SetTooltip("Show Stream in Main View");

        this.streamviewmount.AppendChild(streamview);
        this.streamviewmount.AppendChild(backbutton);
        return;
    }
    UnmountStreamView()
    {
        this.streamviewmount.RemoveChilds();
    }



    // position: "next", "last", or queue entry ID
    AddFakeEntry(musictype, position)
    {
        let faketile     = new FakeQueueTile(musictype);
        let fakedropzone = new QueueDropZone(null);

        if(position === "last")
        {
            super.AppendChild(faketile);
            super.AppendChild(fakedropzone);
        }
        else if(position === "next")
        {
            let firsttile     = this.element.firstChild;
            let firstdropzone = new Element(firsttile.nextSibling);
            firstdropzone.InsertAfter(fakedropzone);
            firstdropzone.InsertAfter(faketile);
        }
        else
        {
            let dropzoneid      = "dropzone"+position;
            let dropzoneelement = document.getElementById(dropzoneid);
            let dropzone        = new Element(dropzoneelement);
            dropzone.InsertAfter(fakedropzone);
            dropzone.InsertAfter(faketile);
        }
    }

    // When the user skips the current playing music, remove it immediately
    //  and do not wait until the updated Queue comes from the back-end
    FakeEntrySkipping()
    {
        let firstelement  = this.element.firstChild;
        let firsttile     = new Element(firstelement);
        let firstdropzone = new Element(firstelement.nextSibling);
        firsttile.Hide();
        firstdropzone.Hide();

        // Fake random added song to fill up the queue
        if(this.numberofentries === 2)
            this.AddFakeEntry("song", "last"); // TODO: May not be "song"
    }



    // musictype: "audio" or "video"
    Update(musictype, MDBQueue)
    {
        let queuetimemanager = WebUI.GetView("QueueTime");
        // Nothing in the queue? -> Nothing to do
        // A fresh installed MusicDB may have no queue!
        if(MDBQueue.length === 0)
        {
            let nomusicwarning = new MessageBarWarning("There is no Music in the Queue");
            nomusicwarning.Show();
            super.RemoveChilds();
            super.AppendChild(nomusicwarning);
            return;
        }

        // Reset timer
        if(MDBQueue[0].song !== undefined)
        {
            queuetimemanager.ClearTime("audio");
        }
        else if(MDBQueue[0].video !== undefined)
        {
            queuetimemanager.ClearTime("video");
        }

        // Reset QueueView
        super.RemoveChilds();
        if(MDBQueue[0].video !== undefined)
        {
            // In video mode, place the mount point for the StreamView
            super.AppendChild(this.streamviewmount);
        }

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
                tile        = new SongQueueTile(entryid, MDBMusic, MDBAlbum, MDBArtist, buttonbox);
            }
            else if(musictype == "video")
            {
                tile        = new VideoQueueTile(entryid, MDBMusic, MDBArtist, buttonbox);
            }
            else
                continue;   // No song and no video? Should never happen, but who knows…

            if(queueposition > 0)
                tile.BecomeDraggable();

            // When the user presses the remove button, the tile should be hidden as soon as possible.
            // If the music cannot be removed from the queue it will appear on queue refresh,
            // otherwise it is already gone and the user experiences fast response
            buttonbox.SetOnRemoveCallback(()=>{tile.Hide(); dropzone.Hide();});

            super.AppendChild(tile);
            super.AppendChild(dropzone);
            queueposition += 1;
        }

        this.numberofentries = MDBQueue.length;
    }



    // WHAT THE FUCK IS GOING ON HERE?
    // This code it totally messed up and needs to be refactored.
    // Like the left page is managed by the LeftViewManager
    // this code could be managed by a RightViewManager.
    onMusicDBMessage(fnc, sig, args, pass)
    {
        if(fnc == "GetSongQueue" && sig == "ShowSongQueue")
        {
            let mainviewbox = document.getElementById("RightContentBox"); // \_ HACK
            mainviewbox.innerHTML = "";
            mainviewbox.appendChild(WebUI.GetView("Queue").GetHTMLElement());           // /  This should do a Main View Manager
            this.Update("audio", args);
        }
        else if(fnc == "GetVideoQueue" && sig == "ShowVideoQueue")
        {
            let mainviewbox = document.getElementById("RightContentBox"); // \_ HACK
            mainviewbox.innerHTML = "";
            mainviewbox.appendChild(WebUI.GetView("Queue").GetHTMLElement());           // /  This should do a Main View Manager
            this.Update("video", args);
        }
        else if(fnc == "GetAlbum")
        {
            if(sig == "AlbumRenamed" || sig == "SongRenamed")
            {
                let mode = WebUI.GetManager("MusicMode").GetCurrentMode();
                if(mode == "audio")
                    MusicDB.Request("GetSongQueue", "ShowSongQueue");
            }
        }
    }
}





class QueueDropZone extends DropTarget
{
    constructor(entryid)
    {
        super("div", ["QueueDropZone", "QueueTile"], "dropzone"+entryid, ["song", "video", "album", "CD"]);
        
        this.entryid    = entryid;
        this.BecomeDropTarget();
    }



    onTransfer(draggableid)
    {
        let draggable = document.getElementById(draggableid);
        let entryid   = draggable.dataset.entryid;
        let musictype = draggable.dataset.musictype;
        let musicid   = draggable.dataset.musicid;
        let droptask  = draggable.dataset.droptask;
        //window.console && console.log(`Droped ${musictype} with id ${musicid}, ${droptask} at ${this.entryid}`);

        switch(droptask)
        {
            case "move":
                if(entryid == this.entryid)
                    break;

                if(musictype == "song")
                    MusicDB.Call("MoveSongInQueue", {entryid:entryid, afterid:this.entryid});
                else if(musictype == "video")
                    MusicDB.Call("MoveVideoInQueue", {entryid:entryid, afterid:this.entryid});

                // For a responsive user experience, the Move-Action needs to be faked
                // until the response from the back-end comes.
                // Therefore the tile that shall be moved and its corresponding drop zone will be loaded
                // into tilea and zonea.
                // Then it gets moved.
                //
                // Before:
                //  tile b
                //  zone b <--------,
                //   ...            |
                //  tile a -- Move -'
                //  zone a
                //
                // After:
                //  tile b
                //  zone b
                //  tile a
                //  zone a

                let tile = draggable;
                let zone = draggable.nextSibling;
                this.InsertAfter(zone);
                this.InsertAfter(tile);
                break;

            case "insert":
                if(musictype == "song")
                {
                    let songid = parseInt(musicid);
                    MusicDB.Call("AddSongToQueue", {songid: songid, position: this.entryid});
                    WebUI.GetView("Queue").AddFakeEntry(musictype, this.entryid)
                }
                else if(musictype == "video")
                {
                    let videoid = parseInt(musicid);
                    MusicDB.Call("AddVideoToQueue", {videoid: videoid, position: this.entryid});
                }
                else if(musictype == "album")
                {
                    let albumid = parseInt(musicid);
                    MusicDB.Call("AddAlbumToQueue", {albumid: albumid, position: this.entryid});
                }
                else if(musictype == "CD")
                {
                    let [albumid, cdnum] = musicid.split('.');
                    albumid = parseInt(albumid);
                    cdnum   = parseInt(cdnum);
                    MusicDB.Call("AddAlbumToQueue", {albumid: albumid, position: this.entryid, cd: cdnum});
                }
                break;

        }
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

