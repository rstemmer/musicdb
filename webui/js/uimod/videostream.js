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
 *
 *
 */

var GLOBAL_PLAYING   = false;   // Is this client playing the stream
var GLOBAL_STREAMING = false;   // Is the server streaming videos

function NextVideo(videopath)
{
}

function PlayVideo(MDBVideo, entryid)
{
    let player     = document.getElementById("VideoStreamPlayer");
    let posterpath = EncodeVideoThumbnailPath(MDBVideo.framesdirectory, MDBVideo.thumbnailfile);
    let videopath  = "/musicdb/music/" + MDBVideo.path;

    //player.width  = MDBVideo.xresolution;
    //player.height = MDBVideo.yresolution;
    player.src = videopath;

    player.onloadeddata = (event) =>
        {
            player.currentTime = MDBVideo.vbegin;
        };
    player.ontimeupdate = (event) =>
        {
            if(player.currentTime >= MDBVideo.vend)
            {
                player.pause();
                player.currentTime = 0;
                onVideoEnded(entryid);
            }
        };
    player.onended = (event) =>
        {
            onVideoEnded(entryid);
        };
    player.onclick = (event) =>
        {
            GLOBAL_PLAYING = !GLOBAL_PLAYING;
            UpdatePlayerState();
        };

    player.load();

    if(GLOBAL_PLAYING == false)
    {
        player.poster = posterpath;
    }
    else
    {
        player.poster = null;
    }

    UpdatePlayerState();
}


// isstreaming (optional): true, false, null
function UpdatePlayerState(isstreaming)
{
    if(typeof isstreaming === "boolean")
    {
        GLOBAL_STREAMING = isstreaming;
    }

    let player = document.getElementById("VideoStreamPlayer");

    if(GLOBAL_PLAYING == true && GLOBAL_STREAMING == true)
    {
        player.play();
    }
    else
    {
        player.pause();
    }
}


function onVideoEnded(entryid)
{
    MusicDB_Call("VideoEnded", {entryid: entryid});
}

function onVideoStreamConnect()
{
}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

