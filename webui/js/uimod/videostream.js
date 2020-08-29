// MusicDB,  a music manager with web-bases UI that focus on music.
// Copyright (C) 2020  Ralf Stemmer <ralf.stemmer@gmx.net>
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
 * The video stream client gets informed by the server when a new video shall be streamed.
 * This new video gets streamed as soon as the current streamed video finished.
 *
 * In case there is no new video, a new one gets requested.
 */

class VideoStreamPlayer
{
    constructor()
    {
        this.videoplayer  = null;
        this.currententry = 0;
        this.currentvideo = null;
        this.isstreaming  = false;
        this.isplaying    = false;
    }



    SetVideoPlayerElement(videoplayer)
    {
        this.videoplayer = videoplayer;

        this.videoplayer.onloadeddata = (event)=>
            {
                if(this.currentvideo == null)
                    return;
                window.console && console.log("videoplayer.onloadeddata");

                this.videoplayer.currentTime = this.currentvideo.vbegin;
                this.videoplayer.dataset.visible = true;
            };
        
        this.videoplayer.ontimeupdate = (event)=>
            {
                if(this.currentvideo == null)
                    return;

                // Begin fade out animation short before vend is reached
                if(this.videoplayer.currentTime >= this.currentvideo.vend - 2.0)
                {
                    this.videoplayer.dataset.visible = false;
                }

                // Stop video when vend is reached
                if(this.videoplayer.currentTime >= this.currentvideo.vend)
                {
                    this.videoplayer.pause();
                    this.videoplayer.currentTime = 0;
                    this.onVideoEnded(this.currententryid);
                }
            };

        this.videoplayer.onended = (event)=>
            {
                if(this.currentvideo == null)
                    return;
                window.console && console.log("videoplayer.onended");

                this.onVideoEnded(this.currententryid);
            };

        this.videoplayer.onclick = (event)=>
            {
                window.console && console.log("videoplayer.onclick");
                this.isplaying = !this.isplaying;
                this.UpdatePlayerState();
            };

        return;
    }



    // isstreaming (optional): true, false, null
    UpdatePlayerState(isstreaming)
    {
        window.console && console.log("videoplayer.UpdatePlayerState(" + isstreaming + ")");
        if(typeof isstreaming === "boolean")
        {
            this.isstreaming = isstreaming;
        }

        if(this.isplaying == true && this.isstreaming == true)
        {
            this.videoplayer.play();
            window.console && console.log("videoplayer.UpdatePlayerState -> play()");
        }
        else
        {
            this.videoplayer.pause();
            window.console && console.log("videoplayer.UpdatePlayerState -> pause()");
        }

        return;
    }



    PlayVideoFromQueue(MDBVideo, entryid)
    {
        window.console && console.log("videoplayer.PlayVideoFromQueue(" + MDBVideo.name + ")");
        let videopath       = "/musicdb/music/" + MDBVideo.path;
        let posterpath      = EncodeVideoThumbnailPath(MDBVideo.framesdirectory, MDBVideo.thumbnailfile);
        this.currentvideo   = MDBVideo;
        this.currententryid = entryid;

        this.videoplayer.src = videopath;
        this.videoplayer.load();

        if(this.isplaying == false)
        {
            this.videoplayer.poster = posterpath;
        }
        else
        {
            this.videoplayer.poster = null;
        }

        this.UpdatePlayerState();
        return;
    }



    onVideoEnded()
    {
        MusicDB_Call("VideoEnded", {entryid: this.currententryid});
        return;
    }



    onMusicDBNotification(fnc, sig, rawdata)
    {
        if(fnc == "MusicDB:VideoStream")
        {
            if(sig == "onStreamNextVideo")
            {
                this.PlayVideoFromQueue(rawdata.video, rawdata.queue.entryid);
            }
        }
        return;
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        if(fnc == "GetVideoStreamState")
        {
            this.UpdatePlayerState(args.isstreaming);

            if(this.currententryid != args.currententry)
            {
                this.PlayVideoFromQueue(args.video, args.currententry);
            }
        }
        return;
    }
}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

