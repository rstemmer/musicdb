// MusicDB,  a music manager with web-bases UI that focus on music.
// Copyright (C) 2017 - 2022  Ralf Stemmer <ralf.stemmer@gmx.net>
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
 *   │  # Song name (+)(>) ░ │               │
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

        // Create Settings
        this.settings_tags  = new Element("div", ["flex-column"], "AlbumGenreSettings");
        this.settings_color = new Element("div", ["flex-column"]);
        this.settings_more  = new Element("div", ["flex-column"]);
        this.settings   = new TabSelect();
        this.tagstabid  = this.settings.AddTab(new SVGIcon("Tags"),    "Genre Tags",   this.settings_tags, true);
        this.colortabid = this.settings.AddTab(new SVGIcon("Artwork"), "Color Scheme", this.settings_color);
        this.moretabid  = this.settings.AddTab(new SVGIcon("Settings"),"More Settings",this.settings_more);

        // Show settings on right click
        this.headline.SetRightClickCallback((event)=>{this.settings.ToggleVisibility(); event.preventDefault();});
        this.settings.Hide();

        this.hidealbum  = new SettingsCheckbox(
            "Hide Album",
            "When the album is hidden, it will not be shown in the Artists list.</br>Furthermore it is not considered by the random song selection algorithm.</br>You can make the album visible again with the MusicDB Management tools (See Main Menu).");


        // Create Tag-View
        this.genreview    = new TagListView();
        this.subgenreview = new TagListView();

        // Create Layout
        this.songscell    = new Element("div", ["flex-grow"], "SongList");

        this.tagscell     = new Element("div", ["hovpacity"], "TagsCell");
        this.tagscell.AppendChild(this.genreview);
        this.tagscell.AppendChild(this.subgenreview);

        this.settingscell = new Element("div")
        this.settingscell.AppendChild(this.settings);

        // Create Album View Element
        this.column1.AppendChild(this.settingscell);
        this.column1.AppendChild(this.songscell);
        this.column2.AppendChild(this.tagscell);

        this.currentalbumtags = null;
        this.artworkuploader  = null;
    }



    AddRandomSongToQueue(position)
    {
        let currentalbumid = WebUI.GetManager("MusicMode").GetCurrentAlbumID();
        MusicDB.Call("AddRandomSongToQueue", {albumid: currentalbumid, position: position});
    }



    UpdateInformation(MDBAlbum, MDBArtist, MDBTags, MDBCDs)
    {
        let currentalbumid    = WebUI.GetManager("MusicMode").GetCurrentAlbumID();
        this.currentalbumtags = MDBTags;

        // Update Headline
        this.headline.UpdateInformation(MDBAlbum, MDBArtist)
        this.headline.SetSubtitleClickAction(
            ()=>{WebUI.GetView("Artists").ScrollToArtist(MDBArtist.id);},
            null
        );

        // Update Album Artwork and make it draggable
        let newartwork  = new AlbumArtwork(MDBAlbum, "large");
        this.ReplaceArtwork(newartwork);
        this.artwork.ConfigDraggable("album", MDBAlbum.id, "insert");
        this.artwork.BecomeDraggable();

        // Update Settings
        this.colorselect     = new ColorSchemeSelection("audio", currentalbumid);
        this.artworkuploader = new ArtworkUploader("album", MDBAlbum.path, MDBAlbum.id);
        this.settings_color.RemoveChilds();
        this.settings_color.AppendChild(this.artworkuploader.GetHTMLElement());
        this.settings_color.AppendChild(this.colorselect.GetHTMLElement());

        this.hidealbum.SetState(MDBAlbum.hidden);
        this.hidealbum.SetHandler((state)=>
            {
                MusicDB.Broadcast("HideAlbum", "UpdateArtists", {albumid: MDBAlbum.id, hide: state});
            }
        );
        this.albumsettings = new TextButton("Settings", "Show Advanced Album Settings", ()=>
            {
                MusicDB.Request("GetAlbum", "ShowAlbumSettingsLayer", {albumid: MDBAlbum.id});
            },
            "Open album settings layer to review and change all details of this album stored in the database.");
        this.songssettings = new TextButton("Settings", "Show Songs Settings", ()=>
            {
                MusicDB.Request("GetAlbum", "ShowSongsSettingsLayer", {albumid: MDBAlbum.id});
            },
            "Open songs settings layer to review and change all details of the songs of this album.");

        this.settings_more.RemoveChilds();
        this.settings_more.AppendChild(this.hidealbum);
        this.settings_more.AppendChild(this.albumsettings);
        this.settings_more.AppendChild(this.songssettings);

        this.genreedit          = new TagListEdit("genre");
        this.subgenreedit       = new TagListEdit("subgenre");
        this.applytoall         = new TextButton("Approve", `Apply to ${this.CountUntaggedSongs()} Songs that have no Genre Tag`, ()=>{this.ApplyGenreSettingsToAllUntaggedSongs();},
            "Tag all Songs of this Album with the albums Genre and Sub-Genre Tag, if the Songs are not tagged at all. Only approved album tags will be added. The new set song tags can be approved or discard by the user when the song gets played.");
        this.settings_tags.RemoveChilds();
        this.settings_tags.AppendChild(this.genreedit);
        this.settings_tags.AppendChild(this.subgenreedit);
        this.settings_tags.AppendChild(this.applytoall);

        this.settings.SelectTab(this.tagstabid);
        this.settings.Hide();

        // Update/Initialize Album View
        this.UpdateSongList(MDBCDs);
        this.UpdateTagInformation(MDBTags);
        this.ToggleSongPlayingState();

        this.colorselect.SetColors(MDBAlbum.bgcolor, MDBAlbum.fgcolor, MDBAlbum.hlcolor);

        return;
    }



    ApplyGenreSettingsToAllUntaggedSongs()
    {
        // Get Genres and Sub-Genres
        let albumgenres    = this.currentalbumtags.genres;
        let albumsubgenres = this.currentalbumtags.subgenres;
        let albumtags      = [...albumgenres, ...albumsubgenres];
        
        // For all song entries
        for(let songid in this.songtiles)
        {
            let songgenres    = this.songtiles[songid].tags.genres;
            let songsubgenres = this.songtiles[songid].tags.subgenres;
            if(songgenres.length === 0 && songsubgenres.length === 0)
            {
                for(let tag of albumtags)
                {
                    let approval = tag.approval;
                    let tagid    = tag.tagid;

                    if(approval <= 0)
                        continue;   // Not user approved. Only tag songs if the user is sure.

                    MusicDB.Request("SetSongTag", "UpdateTags", 
                        {songid:songid, tagid:tagid, approval:0, confidence:1.0});
                }
            }
        }
        return;
    }



    CountUntaggedSongs()
    {
        let counter = 0;
        // For all song entries
        for(let songid in this.songtiles)
        {
            let songgenres    = this.songtiles[songid].tags.genres;
            let songsubgenres = this.songtiles[songid].tags.subgenres;
            if(songgenres.length === 0 && songsubgenres.length === 0)
            {
                counter++;
            }
        }
        return counter;
    }



    UpdateSongList(MDBCDs)
    {
        this.songscell.RemoveChilds();
        this.songtiles = new Object();

        for(let cdnum in MDBCDs)
        {
            let MDBSongList = MDBCDs[cdnum];

            // If more than 1 CD, create a small headline
            // Use this headline also for allowing adding the CD into the queue.
            // The music ID for CDs is AlbumID.CDNum
            if(MDBCDs.length > 1)
            {
                let cdname       = parseInt(cdnum) + 1;
                let albumid      = MDBSongList[0].song["albumid"];
                let headline     = new Draggable("div", ["smallfont", "hlcolor", "CDNumber"]);
                let headlinetext = "CD " + cdname;
                headline.SetInnerText(headlinetext);
                headline.ConfigDraggable("CD", `${albumid}.${cdnum}`, "insert");
                headline.BecomeDraggable();
                this.songscell.AppendChild(headline);
            }

            // Create actual song list
            for(let songnum in MDBSongList)
            {
                let MDBSong      = MDBSongList[songnum].song;
                let MDBTags      = MDBSongList[songnum].tags;
                let songid       = MDBSong.id;
                let songsettings = new SongSettings(MDBSong, MDBTags);
                let songtile     = new SongEntryTile(MDBSong, MDBTags);

                this.songscell.AppendChild(songtile);
                this.songscell.AppendChild(songsettings);

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
        this.songscell.ReplaceChild(newsongtile, oldsongtile);

        // Update internal data
        this.songtiles[songid].tile = newsongtile;
        this.songtiles[songid].settings.Update(MDBSong, MDBTags);
        this.songtiles[songid].tags = MDBTags;

        this.ToggleSongPlayingState();
        return
    }



    UpdateTagInformation(MDBTags)
    {
        let currentalbumid    = WebUI.GetManager("MusicMode").GetCurrentAlbumID();
        this.currentalbumtags = MDBTags;

        // Update existing tags
        this.genreedit.Update(   "album", currentalbumid, MDBTags);
        this.subgenreedit.Update("album", currentalbumid, MDBTags);

        this.genreview.Update(   "album", currentalbumid, MDBTags.genres);
        this.subgenreview.Update("album", currentalbumid, MDBTags.subgenres);

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



    ToggleSongPlayingState()
    {
        // Depending on the call order, some fundamental objects may not yet exist
        // This is OK because Song-State updates and Album-Updates are decoupled
        if(typeof this.songtiles !== "object")
            return

        // Get current song ID and check if it is available in the shown album
        let currentsongid = WebUI.GetManager("MusicMode").GetCurrentSongID();
        if(typeof this.songtiles[currentsongid] !== "object")
            return;

        // Set all to false
        for(let songid in this.songtiles)
        {
            let songtile = this.songtiles[songid];
            if(typeof songtile !== "object")
                continue
            songtile.tile.SetPlayingState(false);
        }

        // Set actual tile to true
        this.songtiles[currentsongid].tile.SetPlayingState(true);

        // The ScrollIntoView requires the element being rendered.
        // Especially after a GetAlbum->ShowAlbum message exchange,
        // the album view may not yet be visible at all.
        // So this requires a short delay before scrolling to the currently playing song.
        window.setTimeout(()=>
            {
                this.songtiles[currentsongid].tile.ScrollIntoView();
            }, 500/*ms*/);
        return;
    }



    onMusicDBNotification(fnc, sig, rawdata)
    {
        this.artworkuploader?.onMusicDBNotification(fnc, sig, rawdata);
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        let currentalbumid = WebUI.GetManager("MusicMode").GetCurrentAlbumID();

        if(fnc == "GetAlbum" && sig == "ShowAlbum")
        {
            this.UpdateInformation(args.album, args.artist, args.tags, args.cds);
        }
        else if(fnc == "GetAlbum" && (sig == "AlbumRenamed" || sig == "SongRenamed"))
        {
            if(args.album.id !== currentalbumid)
                return;
            this.UpdateInformation(args.album, args.artist, args.tags, args.cds);
        }
        else if(fnc == "GetAlbum" && sig == "UpdateTags")
        {
            if(args.album.id == currentalbumid)
                this.UpdateTagInformation(args.tags);
        }
        else if(fnc == "GetTags" || fnc == "RemoveSongTag")
        {
            // In case there are changes with the tags, refresh the album view
            if(sig == "UpdateTags")
                MusicDB.Request("GetAlbum", "UpdateTags", {albumid: currentalbumid});
        }
        else if(fnc == "GetSong")
        {
            if(args.album.id == currentalbumid)
            {
                this.UpdateSongInformation(args.song, args.tags);

                // When a song got new tags, there may be new suggestions for the album as well
                if(sig == "UpdateTags")
                    MusicDB.Request("GetAlbum", "UpdateTags", {albumid: args.album.id});
            }
        }


        this.artworkuploader?.onMusicDBMessage(fnc, sig, args, pass);
        return;
    }

}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

