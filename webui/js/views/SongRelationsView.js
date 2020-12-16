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

class SongRelationsView extends MainView
{
    constructor()
    {
        super("SongRelationsView", new MainViewHeadline(null));

        this.songsbox    = document.createElement("div");
        this.songsbox.classList.add("songsbox");
        this.songsbox.classList.add("flex-column");
        this.element.appendChild(this.songsbox);
    }



    Update(MDBSong, MDBAlbum, MDBArtist, songentries)
    {
        this.songsbox.innerHTML = "";
        this.headline.UpdateRawInformation(MDBSong.name, MDBArtist.name, MDBAlbum.name, MDBSong.name);
        this.headline.SetSubtitleClickAction(
            ()=>{artistsview.ScrollToArtist(MDBArtist.id);},
            ()=>{MusicDB_Request("GetAlbum", "ShowAlbum", {albumid: MDBAlbum.id});}
        );

        let activegenres    = tagmanager.GetActiveGenres();
        let currentartistid = -1;
        this.songtiles = new Object();
        for(let entry of songentries)
        {
            let song     = entry.song;
            let songid   = song.id;
            let album    = entry.album;
            let artist   = entry.artist;
            let tags     = entry.tags;
            let genres   = tags.genres;
            let weight   = entry.weight;

            // Create new Artist Headline
            if(artist.id != currentartistid)
            {
                this.AddArtistHeadline(artist);
                currentartistid = artist.id;
            }

            // Check if songs genre matches active genres
            let inactivegenre = false;
            for(let genre of genres)
            {
                let found = activegenres.find(activegenre => activegenre.id == genre.id);
                if(found)
                {
                    inactivegenre = true;
                    break;
                }
            }

            // Create Song tile
            let buttons  = new ButtonBox_RelationControl(MDBSong.id, song.id);
            let songtile = new TaggedSongTile(song, album, artist, tags, buttons);
            songtile.GetHTMLElement().title          = `Number of consecutive plays: ${weight}`;
            songtile.GetHTMLElement().dataset.active = inactivegenre;
            this.songsbox.appendChild(songtile.GetHTMLElement());

            this.songtiles[songid] = new Object();
            this.songtiles[songid].tile = songtile;
        }
        return;
    }



    UpdateSongTags(MDBSong, MDBTags)
    {
        let songid = MDBSong.id;
        let entry  = this.songtiles[songid];

        // Check if the updates song is part of the relations-list
        if(entry === undefined)
            return;

        // Update Tags
        let tile    = entry.tile;
        tile.UpdateTags(MDBTags);
        return;
    }



    AddArtistHeadline(MDBArtist)
    {
        let artistheadline = document.createElement("span");

        artistheadline.innerText = MDBArtist.name;
        artistheadline.onclick   = ()=>{artistsview.ScrollToArtist(MDBArtist.id);};

        this.songsbox.appendChild(artistheadline);
        return;
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        if(fnc == "GetSongRelationship")
        {
            if(sig == "ShowSongRelationship")
            {
                this.Update(args.song, args.album, args.artist, args.songs);
            }
        }
        else if(fnc == "GetSong")
        {
            if(sig == "UpdateTags")
            {
                this.UpdateSongTags(args.song, args.tags);
            }
        }
        return;
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

