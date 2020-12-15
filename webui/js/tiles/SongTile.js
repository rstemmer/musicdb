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

class SongTile extends Tile
{
    constructor(MDBSong, MDBAlbum, MDBArtist)
    {
        super();
        let buttonbox = new ButtonBox_AddSongToQueue(MDBSong.id);
        let artwork   = new AlbumArtwork(MDBAlbum, "small");
        let title     = super.CreateSongTitle(MDBSong);
        let subtitle  = super.CreateSongSubtitle(MDBAlbum, MDBArtist);
        super.MakeElement(artwork, title, new Array(buttonbox), subtitle, null);
        this.element.classList.add("SongTile");
        super.ConfigDraggable("song", MDBSong.id, "insert", "SongTile_");
        super.BecomeDraggable();
    }
}



class TaggedSongTile extends Tile
{
    constructor(MDBSong, MDBAlbum, MDBArtist, MDBTags, bottombuttons=null)
    {
        super();
        let buttonbox     = new ButtonBox_AddSongToQueue(MDBSong.id);
        let artwork       = new AlbumArtwork(MDBAlbum, "small");
        this.genreview    = new TagListView();
        this.subgenreview = new TagListView();
        this.songid       = MDBSong.id;

        let title         = super.CreateSongTitle(MDBSong);
        let subtitle      = super.CreateSongSubtitle(MDBAlbum, MDBArtist);

        let bottomcontrols;
        if(bottombuttons != null)
            bottomcontrols = new Array(this.subgenreview, bottombuttons);
        else
            bottomcontrols = new Array(this.subgenreview);

        super.MakeElement(artwork, title, new Array(this.genreview, buttonbox), subtitle, bottomcontrols);
        this.element.classList.add("SongTile");
        this.UpdateTags(MDBTags);

        super.ConfigDraggable("song", MDBSong.id, "insert", "SongTile_");
        super.BecomeDraggable();
    }



    UpdateTags(MDBTags)
    {
        this.genreview.Update(   "audio", this.songid, MDBTags.genres);
        this.subgenreview.Update("audio", this.songid, MDBTags.subgenres);
    }
}



/* Layout:
 *
 *  # Song Name    Flags (l) (+) (>) |
 *
 */
class SongEntryTile extends Draggable
{
    // TODO: Lyrics-integration
    constructor(MDBSong, MDBTags)
    {
        super();
        this.songid  = MDBSong.id;
        this.element = document.createElement("div");

        this.songnum      = this.CreateSongNumber(MDBSong);
        this.playingicon  = new SVGIcon("StatusPlaying");
        this.playingicon.GetHTMLElement().dataset.playing = false;
        this.playingicon.GetHTMLElement().classList.add("playingicon");
        this.songname     = this.CreateSongName(MDBSong);
        this.flagbar      = new FlagBar(MDBSong, MDBTags.moods);
        this.appendbutton = new SVGButton("Append", ()=>{this.AddSongToQueue("last");});
        this.insertbutton = new SVGButton("Insert", ()=>{this.AddSongToQueue("next");});
        this.appendbutton.SetTooltip("Append song to the queue");
        this.insertbutton.SetTooltip("Insert song into the queue after current playing song");

        this.element.appendChild(this.songnum);
        this.element.appendChild(this.playingicon.GetHTMLElement());
        this.element.appendChild(this.songname);
        this.element.appendChild(this.flagbar.GetHTMLElement());
        this.element.appendChild(this.appendbutton.GetHTMLElement());
        this.element.appendChild(this.insertbutton.GetHTMLElement());
        this.element.classList.add("SongEntryTile");
        this.element.classList.add("flex-row");
        this.element.dataset.highlight = false;

        if(MDBSong.disabled)
        {
            this.element.classList.add("hovpacity");
        }
        else if(MDBSong.favorite == -1)
        {
            this.element.classList.add("hovpacity");
        }

        this.ConfigDraggable("song", this.songid, "insert");
        this.BecomeDraggable();
    }



    GetHTMLElement()
    {
        return this.element;
    }



    AddSongToQueue(position)
    {
        MusicDB_Call("AddSongToQueue", {songid: this.songid, position: position});
    }



    CreateSongNumber(MDBSong)
    {
        let songnum = document.createElement("div");
        songnum.classList.add("songnumber");
        songnum.classList.add("hlcolor");

        if(MDBSong.number != 0)
            songnum.innerText = MDBSong.number
        else
            songnum.innerText = "⚪&#x0000FE0E;";
        return songnum;
    }



    CreateSongName(MDBSong)
    {
        let songname   = MDBSong.name;
        let disabled   = MDBSong.disabled;
        let lastplayed = new Date(MDBSong.lastplayed * 1000);
        let element    = document.createElement("div");
        element.classList.add("songname");

        // Set HLColor if disabled
        if(disabled)
            element.classList.add("hlcolor");

        // Create tool tip
        // Source: https://gist.github.com/kmaida/6045266
        let yyyy   = lastplayed.getFullYear();
        let mm     = ('0' + (lastplayed.getMonth() + 1)).slice(-2);   // Months are zero based. Add leading 0.
        let dd     = ('0' +  lastplayed.getDate()).slice(-2);         // Add leading 0.
        let lpdate = dd + "." + mm + "." + yyyy;

        let tooltip;
        if(lastplayed > 0)
            tooltip = songname + "\u000A" + lpdate;
        else
            tooltip = songname;

        element.title = tooltip;

        // Set Name
        element.innerText = songname;

        return element;
    }



    SetRightClickCallback(callback)
    {
        this.element.oncontextmenu = callback;
    }



    SetPlayingState(state)
    {
        this.playingicon.GetHTMLElement().dataset.playing = state;
    }
    GetPlayingState()
    {
        return this.playingicon.GetHTMLElement().dataset.playing;
    }



    Highlight(state)
    {
        this.element.dataset.highlight = state;
    }
}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

