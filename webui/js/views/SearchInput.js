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

class SearchInput
{
    constructor()
    {
        this.element = document.createElement("div");
        this.element.classList.add("flex-row");
        this.element.classList.add("hlcolor");
        this.element.classList.add("hovpacity");
        this.element.classList.add("SearchInput");
        this._AddInputBoxElements();

        this.timeoutinterval = 500;
        this.preview = new SearchResultsPopup();
        this.preview.Hide();
        this.element.appendChild(this.preview.GetHTMLElement());
    }



    _AddInputBoxElements()
    {
        this.icon        = new SVGIcon("MusicDB");
        
        this.clearbutton = new SVGButton("Remove", ()=>{this.ClearInput();});
        this.clearbutton.GetHTMLElement().classList.add("hovpacity");

        this.input       = document.createElement("input");
        this.input.oninput     = ()=>{this.onInput(event);};
        this.input.onkeyup     = ()=>{this.onKeyUp(event);};
        this.input.onclick     = ()=>{this.onClick(event);};
        this.input.type        = "search";
        this.input.placeholder = "Search…";

        this.element.appendChild(this.icon.GetHTMLElement());
        this.element.appendChild(this.input);
        this.element.appendChild(this.clearbutton.GetHTMLElement());
        return;
    }



    GetHTMLElement()
    {
        return this.element;
    }



    Find(searchstring)
    {
        window.console && console.log(`Find: ${searchstring}`);
        let limit = 5;
        MusicDB_Request("Find", "ShowPreview", {searchstring:searchstring, limit:limit});

        // after timeout, this method gets called. So with this function call the handler became invalid.
        this.timeouthandler = null; 
        return;
    }



    ClearInput()
    {
        return;
    }



    // Events from the text input element
    onInput(event)
    {
        if(this.input.value.length <= 0)
        {
            window.console && console.log("Hide Preview");
            this.preview.Hide();
            return;
        }

        if(this.timeouthandler)
            clearTimeout(this.timeouthandler)

        this.timeouthandler = setTimeout(this.Find, this.timeoutinterval, this.input.value);
        return;
    }


    onKeyUp(event)
    {
        let keycode = event.which || event.keyCode;
        if(keycode == 13 /*ENTER*/ && this.input.value.length > 0)
        {
            window.console && console.log("Show full result");
            this.preview.Hide();
        }
        else if(keycode == 27 /*ESC*/)
        {
            window.console && console.log("Hide Preview");
            this.preview.Hide();
        }
        return;
    }


    onClick(event)
    {
        if(this.input.value.length > 0)
        {
            window.console && console.log("Show Preview");
            this.preview.Show();
        }
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        if(fnc == "Find")
        {
            if(sig == "ShowPreview")
            {
                this.preview.Update(args.artists, args.albums, args.songs);
                window.console && console.log("Show Preview");
                this.preview.Show();
            }
        }
        return;
    }
}



class SearchResults
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
        window.console && console.log(MDBArtistResults);
        window.console && console.log(MDBAlbumResults);
        window.console && console.log(MDBSongResults);
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
        preview.classList.add("flex-row");
        preview.classList.add("AlbumResults");

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



class SearchResultsPopup extends SearchResults
{
    constructor()
    {
        super();
        this.element.classList.add("frame");
        this.element.classList.add("SearchResultsPopup");

        this.element.innerText = "Dummy Text";
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

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

