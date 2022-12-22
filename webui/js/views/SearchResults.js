// MusicDB,  a music manager with web-bases UI that focus on music.
// Copyright (C) 2017 - 2023  Ralf Stemmer <ralf.stemmer@gmx.net>
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

class SearchResultsElement extends Element
{
    constructor()
    {
        super("div", ["flex-column", "fgcolor", "SearchResults"]);
    }



    Update(MDBArtistResults, MDBAlbumResults, MDBSongResults)
    {
        this.RemoveChilds();
        let artistresults = this.CreateArtistResults(MDBArtistResults);
        let albumresults  = this.CreateAlbumResults(MDBAlbumResults);
        let songresults   = this.CreateSongResults(MDBSongResults);

        this.AppendChild(artistresults);
        this.AppendChild(albumresults);
        this.AppendChild(songresults);
    }



    // TODO: Use Element class
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
                        MusicDB.Request("GetAlbum", "ShowAlbum", {albumid: MDBAlbum.id});
                    });
                albumspreview.appendChild(tile.GetHTMLElement());
            }

            let artistname = document.createElement("span");
            artistname.innerText = MDBArtist.name;
            artistname.onclick   = ()=>{WebUI.GetView("Artists").ScrollToArtist(MDBArtist.id);};

            preview.appendChild(artistname);
            preview.appendChild(albumspreview);
        }
        return preview;
    }



    // TODO: Use Element class
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
                    MusicDB.Request("GetAlbum", "ShowAlbum", {albumid: MDBAlbum.id});
                });
            albumspreview.appendChild(tile.GetHTMLElement());
        }
        return albumspreview;
    }



    // TODO: Use Element class
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



class SearchResultsPopup extends PopupElement
{
    constructor(onhide=null)
    {
        super(["SearchResultsPopup"]);

        this.resultselement = new SearchResultsElement();

        if(onhide == null)
            this.onhide        = this.Hide;
        else
            this.onhide        = onhide;

        this.SetClickEventCallback(()=>{this.onhide();});
        this.SetInnerText("Loading …");

        this.closebutton = new SVGButton("Remove", ()=>{this.onhide();});
        this.closebutton.SetTooltip("Close search results preview");
        this.closebutton.AddCSSClass("closebutton");
        this.AppendChild(this.closebutton);
    }

    Update(MDBArtistResults, MDBAlbumResults, MDBSongResults)
    {
        this.RemoveChilds();
        this.resultselement.Update(MDBArtistResults, MDBAlbumResults, MDBSongResults);
        this.AppendChild(this.resultselement);
        this.AppendChild(this.closebutton);
    }
}



class SearchResultsView extends MainView
{
    constructor()
    {
        super("SearchResultsView", new SimpleMainViewHeadline("Search Results"));
        this.resultselement = new SearchResultsElement();
        this.AppendChild(this.resultselement);
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        if(fnc == "Find")
        {
            if(sig == "ShowResults")
            {
                this.resultselement.Update(args.artists, args.albums, args.songs);
            }
        }
        return;
    }
}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

