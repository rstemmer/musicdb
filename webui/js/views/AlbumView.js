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

class AlbumView extends MainView2
{
    constructor()
    {
        // Button Array
        let appendbutton = new SVGButton("Append", ()=>{this.AddRandomSongToQueue("last");});
        let insertbutton = new SVGButton("Insert", ()=>{this.AddRandomSongToQueue("next");});
        appendbutton.SetTooltip("Append random song from this album to the queue");
        insertbutton.SetTooltip("Insert random song from this album into the queue after current playing song");

        let headline = new MainViewHeadline(new Array(appendbutton, insertbutton));
        let artwork  = new AlbumArtwork(null, "large"); // album=null -> default artwork
        super("AlbumView", headline, artwork);

        this.currentalbumid = -1;
        this.currentsongid  = -1;

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

        // Create Tag-View
        this.genreview    = new TagListView();
        this.subgenreview = new TagListView();

        // Create Layout
        this.songscell    = document.createElement("div");
        this.songscell.classList.add("flex-grow");
        this.songscell.id = "SongList";

        this.tagscell     = document.createElement("div");
        this.tagscell.id  = "TagsCell";
        this.tagscell.appendChild(this.genreview.GetHTMLElement());
        this.tagscell.appendChild(this.subgenreview.GetHTMLElement());

        this.settingscell = document.createElement("div");
        this.settingscell.appendChild(this.settings.GetHTMLElement());

        // Create Album View Element
        this.column1.appendChild(this.settingscell);
        this.column1.appendChild(this.songscell);
        this.column2.appendChild(this.tagscell);
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
        // For new albums, some persistent information need to be updated
        if(MDBAlbum.id != this.currentalbumid)
        {
            this.currentalbumid = MDBAlbum.id;

            // Update Headline
            this.headline.UpdateInformation(MDBAlbum, MDBArtist)
            this.headline.SetSubtitleClickAction(
                ()=>{artistsview.ScrollToArtist(MDBArtist.id);},
                null
            );

            // Update Album Artwork and make it draggable
            let newartwork  = new AlbumArtwork(MDBAlbum, "large");
            this.ReplaceArtwork(newartwork);
            this.artwork.ConfigDraggable("album", MDBAlbum.id, "insert");
            this.artwork.BecomeDraggable();

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
            this.settings.Hide();

            // Update/Initialize Album View
            this.UpdateSongList(MDBCDs);
            this.UpdateTagInformation(MDBTags);
            this.ToggleSongPlayingState(true);
        }

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
                headline.classList.add("smallfont");
                headline.classList.add("hlcolor");
                headline.classList.add("CDNumber");
                headline.innerText = "CD " + (parseInt(cdnum) + 1);
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
                this.songtiles[songid].tags     = MDBTags;

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
        this.songtiles[songid].tags = MDBTags;

        this.ToggleSongPlayingState(false);
        this.currentsongid = MDBSong.id;   // update current song id
        this.ToggleSongPlayingState(true);
        return
    }



    UpdateTagInformation(MDBTags)
    {
        // Update existing tags
        this.genreedit.Update(   "album", this.currentalbumid, MDBTags);
        this.subgenreedit.Update("album", this.currentalbumid, MDBTags);

        this.genreview.Update(   "album", this.currentalbumid, MDBTags.genres);
        this.subgenreview.Update("album", this.currentalbumid, MDBTags.subgenres);

        // Update Mouse-Over Action
        for(let tag of this.genreview.GetTagList())
        {
            tag.SetMouseEnterAction((tagid)=>{this.HighlightSongsByTagID(tagid);});
            tag.SetMouseLeaveAction((tagid)=>{this.HighlightSongsByTagID(null); });
        }
        for(let tag of this.subgenreview.GetTagList())
        {
            tag.SetMouseEnterAction((tagid)=>{this.HighlightSongsByTagID(tagid);});
            tag.SetMouseLeaveAction((tagid)=>{this.HighlightSongsByTagID(null); });
        }

        return;
    }



    HighlightSongsByTagID(tagid)
    {
        for(let songid in this.songtiles)
        {
            let songtile = this.songtiles[songid];

            if(tagid == null)
            {
                // Un-highlight tile and continue
                songtile.tile.Highlight(false);
                continue;
            }

            // Get all songs tag IDs
            let genreids    = songtile.tags.genres.map(genre => genre.id);
            let subgenreids = songtile.tags.subgenres.map(subgenre => subgenre.id);
            let tagids      = genreids.concat(subgenreids);

            if(tagids.indexOf(tagid) >= 0)
            {
                // Highlight tile
                songtile.tile.Highlight(true);
            }
        }
        return;
    }



    ToggleSongPlayingState(newstate = null)
    {
        // Depending on the call order, some fundamental objects may not yet exist
        // This is OK because Song-State updates and Album-Updates are decoupled
        if(typeof this.songtiles != "object")
            return
        if(typeof this.songtiles[this.currentsongid] != "object")
            return

        if(newstate == null)
            newstate = ! this.songtiles[this.currentsongid].tile.GetPlayingState();

        this.songtiles[this.currentsongid].tile.SetPlayingState(newstate);
        return;
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
                this.ToggleSongPlayingState(false);
                this.currentsongid = args.song.id;   // update current song id
                this.ToggleSongPlayingState(true);

                // FIXME: The ViewManager should decide if the album needs to be loaded
                // The request and presentation may be two decisions
                // If for example a different view is more important than the AlbumView
                if(args.album.id != this.currentalbumid)
                    MusicDB_Request("GetAlbum", "ShowAlbum", {albumid: args.album.id});
            }
        }
        else if(fnc == "GetAlbum" && sig == "ShowAlbum")
        {
            this.UpdateInformation(args.album, args.artist, args.tags, args.cds);
            this.currentalbumid = args.album.id;
        }
        else if(fnc == "GetAlbum" && sig == "UpdateTags")
        {
            if(args.album.id == this.currentalbumid)
            {
                this.UpdateTagInformation(args.tags);
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

