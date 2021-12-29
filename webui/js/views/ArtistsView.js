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


class Marker extends Element
{
    constructor(id)
    {
        super("div", ["marker"], id);
    }
}


class ArtistsView extends LeftView
{
    constructor()
    {
        super("ArtistView", ["artistview", "flex-row"]);
        this.element.classList.remove("flex-column");
        this.mode    = null; // Gets defined in the onMusicDBMessage method
        this.tiles   = null; // Will be set during rendering the tiles
    }



    Update(MDBArtistList)
    {
        let  anchor     = " ";   // track first letter of the artistname to set jumpmarks

        this.tiles      = new Object();
        this.RemoveChilds();
        this.AppendChild(new Marker("↑_mark"));

        for(let entry of MDBArtistList)
        {
            // Create artists entry
            let artist   = entry.artist;

            // Get music content from artist
            let music;
            if(this.mode == "audio")
                music = entry.albums;
            else
                music = entry.videos;

            if(music.length == 0)
                continue;

            // Set anchor
            let firstchar = artist.name.charAt(0).toUpperCase();
            if(firstchar != anchor)
            {
                anchor = firstchar;
                this.AppendChild(new Marker(anchor + "_mark"));
            }

            // Add artists music
            let artistelement = this._CreateArtistElement(artist, music)
            this.AppendChild(artistelement);
        }

        this.AppendChild(new Marker("↓_mark"));
        return;
    }


    _CreateArtistElement(artist, music)
    {
        let artistelement = new Element("div", ["artistentry"]);

        // Add artist headline
        let headline = this._CreateArtistHeadline(artist)
        artistelement.AppendChild(headline);

        for(let entry of music)
        {
            let tile;
            let musicid;
            if(this.mode == "audio")
            {
                musicid = entry.album.id;
                tile = new AlbumTile(entry.album, ()=>
                    {
                        MusicDB_Request("GetAlbum", "ShowAlbum", {albumid: musicid});
                    });
            }
            else
            {
                musicid = entry.video.id;
                tile = new VideoTile(entry.video, ()=>
                    {
                        MusicDB_Request("GetVideo", "ShowVideo", {videoid: musicid});
                    },
                    new FlagBar(entry.video, entry.tags.moods, "left" /*icons are left aligned*/)
                    );
            }

            if(configuration.ArtistsView.showrelease == false)
                tile.HideReleaseDate();

            this.tiles[musicid] = tile;
            artistelement.AppendChild(tile);
        }

        return artistelement;
    }



    _CreateArtistHeadline(MDBArtist)
    {
        // Add artist headline
        let headline = new Element("span", ["fgcolor"], "Artist_" + MDBArtist.id);
        headline.SetInnerText(MDBArtist.name);
        headline.SetTooltip(MDBArtist.name);
        return headline;
    }



    ScrollToArtist(artistid)
    {
        let element = document.getElementById("Artist_" + artistid);
        if(element != null)
            element.scrollIntoView({behavior: "smooth", block: "start"});
        return;
    }

    ScrollToMarker(marker)
    {
        let element = document.getElementById(marker + "_mark");
        if(element != null)
            element.scrollIntoView({behavior: "smooth", block: "start"});
        return;
    }



    UpdateTile(MDBMusic, MDBTags)
    {
        let musicid = MDBMusic.id;
        let tile    = this.tiles[musicid];
        let flagbar = new FlagBar(MDBMusic, MDBTags.moods);
        tile.ReplaceFlagBar(flagbar);

        if(MDBMusic.disabled)
            tile.SetDisabled();
        else
            tile.SetEnabled();
        return;
    }



    /*
     * This method does two things:
     *  If the genre is valid but the tile does not exist -> Request new aritsts list
     *  If the genre is not valid but the tile does exist -> Request new artists list
     */
    ValidateTile(MDBMusic, MDBGenres)
    {
        let musicid      = MDBMusic.id;
        let tile         = this.tiles[musicid];
        let activegenres = tagmanager.GetActiveGenres();

        for(let genre of MDBGenres)
        {
            let found = activegenres.find(activegenre => activegenre.id == genre.id);
            if(found) // Genre is OK, but does the tile exist?
            {
                if(tile === undefined)
                    this.RequestUpdate();
                return; // OK, Tile is still valid
            }
        }

        // Genres are no longer active. Does the tile still exist?
        if(tile !== undefined)
            this.RequestUpdate();
        
        return;
    }

    RequestUpdate()
    {
        let mode = WebUI.GetManager("MusicMode").GetCurrentMode();
        if(mode == "audio")
            MusicDB_Broadcast("GetFilteredArtistsWithAlbums", "ShowArtists");
        else if(mode == "video")
            MusicDB_Broadcast("GetFilteredArtistsWithVideos", "ShowArtists");
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        if(fnc == "GetFilteredArtistsWithAlbums" && sig == "ShowArtists")
        {
            this.mode = "audio";
            this.Update(args);
        }
        else if(fnc == "GetFilteredArtistsWithVideos" && sig == "ShowArtists")
        {
            this.mode = "video";
            this.Update(args);
        }
        else if(fnc == "GetVideo")
        {
            if(this.mode != "video")
                return;

            if(sig == "UpdateVideo") // There may be some changes regarding the flags
                this.UpdateTile(args.video, args.tags);

            if(sig == "UpdateTags") // Is the main genre set still intersecting the selected genres?
                this.ValidateTile(args.video, args.tags.genres);
        }
        else if(fnc == "HideAlbum" && sig == "UpdateArtists")
        {
            let mode = WebUI.GetManager("MusicMode").GetCurrentMode();
            if(mode == "audio")
                MusicDB_Request("GetFilteredArtistsWithAlbums", "ShowArtists");
            else
                MusicDB_Request("GetFilteredArtistsWithVideos", "ShowArtists");
        }
        else if(fnc == "GetAlbum" && sig == "AlbumRenamed")
        {
            let mode = WebUI.GetManager("MusicMode").GetCurrentMode();
            if(mode == "audio")
                MusicDB_Request("GetFilteredArtistsWithAlbums", "ShowArtists");
        }
        return;
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

