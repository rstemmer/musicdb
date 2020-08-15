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
    player.poster = posterpath;
    player.src    = videopath;
    player.load();
    //player.play();

    player.onended = (event) =>
        {
            onVideoEnded(entryid)
        };
}


function UpdateVideoEventHandler(videoid, entryid)
{
    let video = document.getElementById(videoid);
    // Use the onended property to avoid adding multiple event handler
}

function onVideoEnded(entryid)
{
    MusicDB_Call("VideoEnded", {entryid: entryid});
}

function onVideoStreamConnect()
{
}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

