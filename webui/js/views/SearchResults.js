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

class BaseSearchResults
{
    constructor()
    {
        this.element = document.createElement("div");
        this.element.classList.add("flex-column");
        this.element.classList.add("fgcolor");
        this.element.classList.add("SearchResults");
    }



    GetHTMLElement()
    {
        return this.element;
    }



    Update(MDBArtistResults, MDBAlbumResults, MDBSongResults)
    {
        this.element.innerHTML = "";
        let artistresults = this.CreateArtistResults(MDBArtistResults);
        let albumresults  = this.CreateAlbumResults(MDBAlbumResults);
        let songresults   = this.CreateSongResults(MDBSongResults);

        this.element.appendChild(artistresults);
        this.element.appendChild(albumresults);
        this.element.appendChild(songresults);
    }



    CreateArtistResults(MDBArtistResults)
    {
        let preview = document.createElement("div");
        preview.classList.add("flex-column");
        preview.classList.add("ArtistResults");

        for(let result of MDBArtistResults)
        {
            // Only show artists that have albums
            if(result.albums.length == 0)
                continue;

            let MDBArtist     = result.artist;
            let albumspreview = document.createElement("div");
            albumspreview.classList.add("flex-row");
            albumspreview.classList.add("AlbumResults");
            for(let MDBAlbum of result.albums)
            {
                let tile = new SmallAlbumTile(MDBAlbum, ()=>
                    {
                        MusicDB_Request("GetAlbum", "ShowAlbum", {albumid: MDBAlbum.id});
                    });
                albumspreview.appendChild(tile.GetHTMLElement());
            }

            let artistname = document.createElement("span");
            artistname.innerText = MDBArtist.name;
            artistname.onclick   = ()=>{artistsview.ScrollToArtist(MDBArtist.id);};

            preview.appendChild(artistname);
            preview.appendChild(albumspreview);
        }
        return preview;
    }



    CreateAlbumResults(MDBAlbumResults)
    {
        let albumspreview = document.createElement("div");
        albumspreview.classList.add("flex-row");
        albumspreview.classList.add("AlbumResults");

        for(let result of MDBAlbumResults)
        {
            let MDBAlbum  = result.album;
            let MDBArtist = result.artist;
            let tile      = new SmallAlbumTile(MDBAlbum, ()=>
                {
                    MusicDB_Request("GetAlbum", "ShowAlbum", {albumid: MDBAlbum.id});
                });
            albumspreview.appendChild(tile.GetHTMLElement());
        }
        return albumspreview;
    }



    CreateSongResults(MDBSongResults)
    {
        let songspreview = document.createElement("div");
        songspreview.classList.add("flex-column");
        songspreview.classList.add("SongResults");

        for(let result of MDBSongResults)
        {
            let MDBSong   = result.song;
            let MDBAlbum  = result.album;
            let MDBArtist = result.artist;
            let tile      = new SongTile(MDBSong, MDBAlbum, MDBArtist);
            songspreview.appendChild(tile.GetHTMLElement());
        }
        return songspreview;
    }
}



class SearchResultsPopup extends BaseSearchResults
{
    constructor(onhide=null)
    {
        super();
        this.element.classList.add("frame");
        this.element.classList.add("opaque");
        this.element.classList.add("SearchResultsPopup");

        if(onhide == null)
            this.onhide        = this.Hide;
        else
            this.onhide        = onhide;

        this.element.onclick   = ()=>{this.onhide();};
        this.element.innerText = "Loading …";

        this.closebutton = new SVGButton("Remove", ()=>{this.onhide();});
        this.closebutton.SetTooltip("Close search results preview");
        this.closebutton.GetHTMLElement().classList.add("closebutton");
        this.element.appendChild(this.closebutton.GetHTMLElement());
    }

    Update(MDBArtistResults, MDBAlbumResults, MDBSongResults)
    {
        super.Update(MDBArtistResults, MDBAlbumResults, MDBSongResults);
        this.element.appendChild(this.closebutton.GetHTMLElement());
    }


    ToggleVisibility()
    {
        if(this.element.style.display == "none")
            this.Show();
        else
            this.Hide();
    }
    Show()
    {
        this.element.style.display = "flex";
    }
    Hide()
    {
        this.element.style.display = "none";
    }
}



class SearchResultsView extends BaseSearchResults
{
    constructor()
    {
        super();
        this.element.id = "SearchResultsView";
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        if(fnc == "Find")
        {
            if(sig == "ShowResults")
            {
                this.Update(args.artists, args.albums, args.songs);
            }
        }
        return;
    }
}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

