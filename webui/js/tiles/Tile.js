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


class Tile extends Draggable
{
    constructor(classes=[])
    {
        super("div", ["Tile", "flex-row", ...classes]);
    }



    onDragStart(event)
    {
        super.onDragStart(event);

        // When dragged from a search preview, hide everything to clear the drop zones
        curtain.Hide();
        searchinput.HidePreview();
    }



    MakeElement(artwork, title, topfeatureelements, subtitle, bottomfeatureelements)
    {
        if(artwork != null)
            this.artwork = artwork;
        else
            this.artwork = new AlbumArtwork(null, "small");

        // Create info box
        this.infobox    = document.createElement("div");
        this.infobox.classList.add("flex-column");
        this.infobox.classList.add("infobox");

        this.toprow     = document.createElement("div");
        this.toprow.classList.add("flex-row");
        if(title != null)
            this.toprow.appendChild(title);
        if(topfeatureelements != null)
            for(let featureelement of topfeatureelements)
                this.toprow.appendChild(featureelement.GetHTMLElement());

        this.bottomrow  = document.createElement("div");
        this.bottomrow.classList.add("flex-row");
        if(subtitle != null)
            this.bottomrow.appendChild(subtitle);
        if(bottomfeatureelements != null)
            for(let featureelement of bottomfeatureelements)
                this.bottomrow.appendChild(featureelement.GetHTMLElement());

        // Create layout
        this.infobox.appendChild(this.toprow);
        this.infobox.appendChild(this.bottomrow);

        super.AppendChild(this.artwork);
        super.AppendChild(this.infobox);
    }



    CreateSongTitle(MDBSong)
    {
        let songname      = MDBSong.name.replace(" - ", " – ");
            songname      = songname.replace(    " ∕ ", " / ");
        let title         = document.createElement("span");
        title.classList.add("Title");
        title.textContent = songname;
        title.classList.add("fgcolor");
        title.classList.add("flex-grow");
        return title;
    }



    CreateVideoTitle(MDBVideo)
    {
        let videoname     = MDBVideo.name.replace(" - ", " – ");
            videoname     = videoname.replace(    " ∕ ", " / ");
        let title         = document.createElement("span");
        title.classList.add("Title");
        title.textContent = videoname;
        title.onclick     = ()=>{MusicDB_Request("GetVideo", "ShowVideo", {videoid: this.videoid});};
        title.classList.add("fgcolor");
        title.classList.add("flex-grow");
        return title;
    }



    CreateSongSubtitle(MDBAlbum, MDBArtist)
    {
        let artistname = MDBArtist.name;
        let albumname  = MDBAlbum.name.replace(" - ", " – ");
            albumname  = albumname.replace(    " ∕ ", " / ");
        let songinfos  = document.createElement("div");
        songinfos.classList.add("Subtitle");
        songinfos.classList.add("hlcolor");
        songinfos.classList.add("smallfont");
        songinfos.classList.add("flex-grow");

        let artist = document.createElement("span");
        let spacer = document.createElement("span");
        let album  = document.createElement("span");

        spacer.classList.add("fgcolor");
        
        artist.innerText = artistname;
        spacer.innerText = " – ";
        album.innerText  = albumname;

        artist.onclick   = ()=>{artistsview.ScrollToArtist(MDBArtist.id);};
        album.onclick    = ()=>{MusicDB_Request("GetAlbum", "ShowAlbum", {albumid: MDBAlbum.id});};

        songinfos.appendChild(artist);
        songinfos.appendChild(spacer);
        songinfos.appendChild(album);
        return songinfos;
    }



    CreateVideoSubtitle(MDBArtist)
    {
        let artistname = MDBArtist.name;
        let songinfos  = document.createElement("div");
        songinfos.classList.add("Subtitle");
        songinfos.classList.add("hlcolor");
        songinfos.classList.add("smallfont");
        songinfos.classList.add("flex-grow");

        let artist = document.createElement("span");
        artist.innerText = artistname;
        artist.onclick   = ()=>{artistsview.ScrollToArtist(MDBArtist.id);};

        songinfos.appendChild(artist);
        return songinfos;
    }

}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

