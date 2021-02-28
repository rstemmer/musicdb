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
 * This is a base class for SongQueueTile in SongTile.js
 * and VideoQueueTile in VideoTile.js
 */

class QueueTile extends Tile
{
    constructor()
    {
        super();
    }



    // musictype: "song" or "video"
    MakeElement(queueentryid, musictype, musicid, artwork, title, subtitle, buttonbox)
    {
        super.MakeElement(artwork, title, new Array(buttonbox), subtitle, null);
        super.ConfigDraggable(musictype, musicid, "move", `QueueEntry${queueentryid}_`);
        this.element.dataset.entryid = queueentryid;
    }
}



class SongQueueTile extends QueueTile
{
    constructor(queueentryid, MDBSong, MDBAlbum, MDBArtist, buttonbox)
    {
        super();
        let artwork  = new AlbumArtwork(MDBAlbum, "small");
        let title    = super.CreateSongTitle(MDBSong);
        let subtitle = super.CreateSongSubtitle(MDBAlbum, MDBArtist);

        super.MakeElement(queueentryid, "song", MDBSong.id, artwork, title, subtitle, buttonbox);
    }
}



class VideoQueueTile extends QueueTile
{
    constructor(queueentryid, MDBVideo, MDBArtist, buttonbox)
    {
        super();
        let artwork  = new VideoArtwork(MDBVideo, "small");
        let title    = super.CreateVideoTitle(MDBVideo);
        let subtitle = super.CreateVideoSubtitle(MDBArtist);

        super.MakeElement(queueentryid, "video", MDBVideo.id, artwork, title, subtitle, buttonbox);
    }
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

