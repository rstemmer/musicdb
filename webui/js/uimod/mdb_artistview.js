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

class ArtistsView
{
    constructor()
    {
        this.element = document.createElement("div");
        this.element.classList.add("flex-row");
        this.element.classList.add("artistsview");
        this.mode    = null; // Gets defined in the onMusicDBMessage method
    }



    GetHTMLElement()
    {
        return this.element;
    }



    Update(MDBArtistList)
    {
        let  anchor    = " ";   // track first letter of the artistname to set jumpmarks

        this.element.innerHTML = "";
        let firstanchor = document.createElement("div");
        firstanchor.id  = "TOP_mark";
        this.element.appendChild(firstanchor);

        for(let entry of MDBArtistList)
        {
            // Create artists entry
            window.console && console.log(entry);
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
                let anchorelement = document.createElement("div");
                anchorelement.id = anchor + "_mark";
                this.element.appendChild(anchorelement);
            }

            // Add artists music
            let artistelement = this._CreateArtistElement(artist, music)
            this.element.appendChild(artistelement);
        }

        let lastanchor = document.createElement("div");
        lastanchor.id  = "BOTTOM_mark";
        this.element.appendChild(lastanchor);

        window.console && console.log(this.artists);
        return;
    }


    _CreateArtistElement(artist, music)
    {
        let artistelement = document.createElement("div");
        artistelement.classList.add("artistentry")

        // Add artist headline
        let headline = this._CreateArtistHeadline(artist.name)
        artistelement.appendChild(headline);

        window.console && console.log(music);
        for(let entry of music)
        {
            let tile;
            if(this.mode == "audio")
            {
                // TODO
            }
            else
            {
                tile = new SmallVideoTile(entry.video);
            }

            artistelement.appendChild(tile.GetHTMLElement());
        }

        return artistelement;
    }



    _CreateArtistHeadline(artistname)
    {
        // Add artist headline
        let headline = document.createElement("span");
        headline.classList.add("fgcolor");
        headline.innerText = artistname;
        return headline;
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
    }
}

/*
 * This class provides the HUD consisting of the following components:
 *
 * Requirements:
 *   - JQuery
 *   - mdb_artistview.css
 *   - Set to each artist an id "Artist_[artistid]"
 * Show:
 *   - ShowArtists(parentID, MDBArgs);
 * Functions:
 * Callbacks:
 * Recommended Paths:
 * Trigger: (fnc -> sig)
 *   - GetAlbum -> ShowAlbum
 */

function ShowArtists(parentID, MDBArtistList)
{
    var html = "";

    html += "<div id=ArtistViewBox>"; // main box
    html += "<span id=TOP_mark class=\"ATV_mark\"></span>";
    
    // For each Arist
    var firstchar  = " ";   // track first letter of the artistname to set jumpmarks
    for(var i in MDBArtistList)
    {
        let MDBArtist      = MDBArtistList[i].artist;
        let MDBContentList = undefined;
        let MDBContentType = undefined;
        if(MDBArtistList[i].albums !== undefined)
        {
            MDBContentList = MDBArtistList[i].albums;
            MDBContentType = "audio";
        }
        else if(MDBArtistList[i].videos !== undefined)
        {
            MDBContentList = MDBArtistList[i].videos;
            MDBContentType = "video";
        }

        // if there is no content, skip this artist (This should not happen with modern backend)
        if(MDBContentList.length == 0)
            continue;

        // Set jump mark if this is the first artist of a letter in the alphabet
        var artistname = MDBArtist.name;
        if(artistname.charAt(0) != firstchar)
        {
            firstchar = artistname.charAt(0).toUpperCase();
            html += "<div id="+firstchar+"_mark class=\"ATV_mark\"></div>";
        }

        if(MDBContentType == "audio")
            html += _ATV_CreateArtistEntryWithAlbums(MDBArtist, MDBContentList);
        else if(MDBContentType == "video")
            html += _ATV_CreateArtistEntryWithVideos(MDBArtist, MDBContentList);
    }
    
    html += "<span id=BTM_mark class=\"ATV_mark\"></span>";
    html += "</div>"; // main box

    // Create Element
    $("#"+parentID).html(html);
    $(".nano").nanoScroller();          // update scrollbars
}


function _ATV_CreateArtistEntryWithAlbums(MDBArtist, MDBAlbumList)
{
    var html = "";
    var label= "Artist_" + MDBArtist.id;    // Label for ScrollToArtist

    html += "<div id=" + label + " class=\"ATV_artistentry\">";

    html += "<span class=\"ATV_artistname fgcolor\">";
    html += MDBArtist.name;
    html += "</span>";
   
    // Create the overview of the artists albums
    html += "<div class=\"ATV_albumlist\">";
    for(var i in MDBAlbumList)
    {
        var MDBAlbum   = MDBAlbumList[i].album;
        html += CreateAlbumTile(MDBAlbum);
    }
    html += "</div>"; // close albumlist div

    html += "</div>"; // close artistentry div

    return html;
}


function _ATV_CreateArtistEntryWithVideos(MDBArtist, MDBVideoList)
{
    var html = "";
    var label= "Artist_" + MDBArtist.id;    // Label for ScrollToArtist

    html += "<div id=" + label + " class=\"ATV_artistentry\">";

    html += "<span class=\"ATV_artistname fgcolor\">";
    html += MDBArtist.name;
    html += "</span>";
   
    // Create the overview of the artists albums
    html += "<div class=\"ATV_albumlist\">"; // FIXME: A different class may be better
    for(var i in MDBVideoList)
    {
        let MDBVideo  = MDBVideoList[i].video;
        let buttonbox = Button_AddVideoToQueue(MDBVideo.id);
        html += CreateSmallVideoTile(MDBVideo, buttonbox);
    }
    html += "</div>"; // close albumlist div

    html += "</div>"; // close artistentry div

    return html;
}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

