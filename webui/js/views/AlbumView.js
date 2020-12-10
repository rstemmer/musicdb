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

/*
 * Album View Layout:
 *
 *   ┌───────────────────────┬───────────────┐
 *   │                       │               │
 *   │  Headline     (+) (>) │  ┌─────────┐  │
 *   │                       │  │         │  │
 *   ├───────────────────────┤  │ /_\    /│  │
 *   │                       │  │/   \/\/ │  │
 *   │  # Song name (+)(>) █ │  │ Artwork │  │
 *   │  # Song name (+)(>) █ │  └─────────┘  │
 *   │  # Song name (+)(>) ░ │               │
 *   │  # Song name (+)(>) ░ ├───────────────┤
 *   │  # Song name (+)(>) ░ │ Tags          │
 *   │  # Song name (+)(>) ░ │ Colors        │
 *   └───────────────────────┴───────────────┘
 * 
 */

class AlbumView
{
    constructor()
    {
        this.currentalbumid = -1;
        this.currentsongid  = -1;

        // Button Array
        let appendbutton = new SVGButton("Append", ()=>{this.AddRandomSongToQueue("last");});
        let insertbutton = new SVGButton("Insert", ()=>{this.AddRandomSongToQueue("next");});
        appendbutton.SetTooltip("Append random song from this album to the queue");
        insertbutton.SetTooltip("Insert random song from this album into the queue after current playing song");
        this.buttons     = new Array();
        this.buttons.push(appendbutton);
        this.buttons.push(insertbutton);

        // Create Headline
        this.headline = new MainViewHeadline(this.buttons);
        this.artwork  = new AlbumArtwork(null, "large"); // album=null -> default artwork

        // Create Settings
        this.settings_tags  = document.createElement("div");
        this.settings_tags.classList.add("flex-grow");
        this.settings_color = document.createElement("div");
        this.settings_color.classList.add("flex-grow");

        this.settings   = new TabSelect();
        this.tagstabid  = this.settings.AddTab(new SVGIcon("Tags"),    "Genre Tags",   this.settings_tags, true);
        this.colortabid = this.settings.AddTab(new SVGIcon("Artwork"), "Color Scheme", this.settings_color);

        // Show settings on right click
        this.headline.SetRightClickCallback((event)=>{this.settings.ToggleVisibility(); event.preventDefault();});
        this.settings.Hide();

        // Create Layout
        let  leftcolumn  = document.createElement("div");
        let  rightcolumn = document.createElement("div");
        this.headlinecell= document.createElement("div");
        this.songscell   = document.createElement("div");
        this.artworkcell = document.createElement("div");
        this.settingscell= document.createElement("div");

        leftcolumn.classList.add("leftcolumn");
        leftcolumn.classList.add("flex-column");
        leftcolumn.classList.add("flex-grow");
        leftcolumn.appendChild(this.headlinecell);
        leftcolumn.appendChild(this.settingscell);
        leftcolumn.appendChild(this.songscell);
        rightcolumn.classList.add("rightcolumn");
        rightcolumn.classList.add("flex-column");
        rightcolumn.appendChild(this.artworkcell);
        //rightcolumn.appendChild(this.settingscell);

        this.settingscell.classList.add("flex-grow");
        this.songscell.classList.add("flex-grow");
        this.songscell.id = "SongList"

        this.headlinecell.appendChild(this.headline.GetHTMLElement());
        this.artworkcell.appendChild(this.artwork.GetHTMLElement());
        this.settingscell.appendChild(this.settings.GetHTMLElement());

        // Create Album View Element
        this.element    = document.createElement("div");
        this.element.id = "AlbumView";
        this.element.classList.add("mainview_container");
        this.element.classList.add("flex-row");
        this.element.appendChild(leftcolumn);
        this.element.appendChild(rightcolumn);
    }



    GetHTMLElement()
    {
        return this.element;
    }



    AddRandomSongToQueue(position)
    {
        MusicDB_Call("AddRandomSongToQueue", {albumid: this.currentalbumid, position: position});
    }



    UpdateInformation(MDBAlbum, MDBArtist, MDBTags, MDBCDs)
    {
        // For new videos, some persistent information need to be updated
        if(MDBAlbum.id != this.currentalbumid)
        {
            this.currentalbumid = MDBAlbum.id;

            // Update Headline
            this.headline.UpdateInformation(MDBAlbum, MDBArtist)

            // Update Album
            this.artwork  = new AlbumArtwork(MDBAlbum, "large");
            this.artwork.ConfigDraggable("album", MDBAlbum.id, "insert");
            this.artwork.BecomeDraggable();

            this.artworkcell.innerHTML = "";
            this.artworkcell.appendChild(this.artwork.GetHTMLElement());

            // Update Settings
            this.colorselect = new ColorSchemeSelection("audio", this.currentalbumid);
            this.settings_color.innerHTML = "";
            this.settings_color.appendChild(this.colorselect.GetHTMLElement());

            this.genreedit          = new TagListEdit("genre");
            this.subgenreedit       = new TagListEdit("subgenre");
            this.settings_tags.innerHTML = "";
            this.settings_tags.appendChild(this.genreedit.GetHTMLElement());
            this.settings_tags.appendChild(this.subgenreedit.GetHTMLElement());

            this.settings.SelectTab(this.tagstabid);

            // Update Song-List
            this.UpdateSongList(MDBCDs);
        }

        this.genreedit.Update(   "album", this.currentalbumid, MDBTags);
        this.subgenreedit.Update("album", this.currentalbumid, MDBTags);
        this.colorselect.SetColors(MDBAlbum.bgcolor, MDBAlbum.fgcolor, MDBAlbum.hlcolor);

        return;
    }



    UpdateSongList(MDBCDs)
    {
        this.songscell.innerHTML = "";
        this.songtiles = new Object();

        for(let cdnum in MDBCDs)
        {
            let MDBSongList = MDBCDs[cdnum];

            // If more than 1 CD, create a small headline
            if(MDBCDs.length > 1)
            {
                let headline = document.createElement("div");
                headline.classList.add("small");
                headline.classList.add("hlcolor");
                headline.innerText = "CD " + parseInt(cdnum) + 1;
                this.songscell.appendChild(headline);
            }

            // Create actual song list
            for(let songnum in MDBSongList)
            {
                let MDBSong      = MDBSongList[songnum].song;
                let MDBTags      = MDBSongList[songnum].tags;
                let songid       = MDBSong.id;
                let songsettings = new SongSettings(MDBSong, MDBTags);
                let songtile     = new SongEntryTile(MDBSong, MDBTags);

                this.songscell.appendChild(songtile.GetHTMLElement());
                this.songscell.appendChild(songsettings.GetHTMLElement());

                this.songtiles[songid] = new Object();
                this.songtiles[songid].tile     = songtile;
                this.songtiles[songid].settings = songsettings;

                songtile.SetRightClickCallback((event)=>{songsettings.ToggleVisibility(); event.preventDefault();});
                songsettings.Hide();
            }
        }

        return;
    }



    UpdateSongInformation(MDBSong, MDBTags)
    {
        let songid = MDBSong.id;
        let newsongtile  = new SongEntryTile(MDBSong, MDBTags);
        let oldsongtile  = this.songtiles[songid].tile;
        let songsettings = this.songtiles[songid].settings;

        // Update song tile
        newsongtile.SetRightClickCallback((event)=>{songsettings.ToggleVisibility(); event.preventDefault();});
        this.songscell.replaceChild(newsongtile.GetHTMLElement(), oldsongtile.GetHTMLElement());

        // Update internal data
        this.songtiles[songid].tile = newsongtile;
        this.songtiles[songid].settings.Update(MDBSong, MDBTags);
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        if(fnc == "GetAudioStreamState" && sig == "UpdateStreamState")
        {
            // Check is there 
            if(!args.hasqueue)
            {
                window.console && console.log("There is no queue and no current song!")
                return;
            }

            // if the song changes, show the new album (or reload for update)
            if(args.song.id != this.currentsongid)
            {
                this.currentsongid = args.song.id;   // update current song id
                MusicDB_Request("GetAlbum", "ShowAlbum", {albumid: args.album.id});
            }
        }
        else if(fnc == "GetAlbum" && sig == "ShowAlbum")
        {
            this.UpdateInformation(args.album, args.artist, args.tags, args.cds);
            this.currentalbumid = args.album.id;
        }
        else if(fnc == "GetAlbum" && sig == "UpdateTagInput")
        {
            if(args.album.id == this.currentalbumid)
            {
                //Albumview_UpdateAlbum(args.album, args.tags);
                // TODO: Use a different update method to avoid rebuilding the song-list
                this.UpdateInformation(args.album, args.artist, args.tags, args.cds);
            }
        }
        else if(fnc == "GetSong")
        {
            if(args.album.id == this.currentalbumid)
            {
                this.UpdateSongInformation(args.song, args.tags);
            }
        }
        return;
    }

}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

