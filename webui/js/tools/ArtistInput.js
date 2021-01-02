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


class ArtistsPopup extends PopupElement
{
    // onartistselect(artistid, artistname)
    constructor(onartistselect)
    {
        super(["ArtistsPopup", "flex-column"]);
        this.onartistselect = onartistselect;
    }



    ShowArtistsList(searchstring)
    {
        let artistslist = artistscache.FindArtist(searchstring);
        if(artistslist.length <= 0)
        {
            this.Hide();
            return;
        }

        this.element.innerHTML = "";
        for(let artist of artistslist)
        {
            this.AddEntry(artist);
        }

        this.Show();
        return;
    }



    AddEntry(MDBArtist)
    {
        let artistid   = MDBArtist.id;
        let artistname = MDBArtist.name;

        let entry       = document.createElement("div");
        let nameelement = document.createElement("span");
        let addicon     = new SVGIcon("Add");

        nameelement.innerText = artistname;
        nameelement.classList.add("flex-grow");

        entry.classList.add("flex-row");
        entry.classList.add("hoverframe");
        entry.title   = "Click to Select This Artist";
        entry.onclick = (event)=>
            {
                event.stopPropagation();
                this.onartistselect(artistid, artistname);
            };
        entry.appendChild(nameelement);
        entry.appendChild(addicon.GetHTMLElement());

        this.element.appendChild(entry);
    }
}


class ArtistInput extends Element
{
    // oninput(Artist ID (=null, when there is no known artist), Artist Name)
    constructor(oninput, artistname, tooltip="")
    {
        super("div", ["ArtistInput", "PopupParent"]);
        this.oninput = oninput;
        this.popup = new ArtistsPopup((id,name)=>{this.onArtistSelect(id, name);});
        this.input = new TextInput((value)=>{return this.onInput(value);}, artistname);

        this.element.title = tooltip;
        this.element.appendChild(this.input.GetHTMLElement());
        this.element.appendChild(this.popup.GetHTMLElement());
    }



    onArtistSelect(artistid, artistname)
    {
        this.input.SetValue(artistname);
        this.popup.Hide();
    }



    onInput(rawvalue)
    {
        let artistname = rawvalue;
        let artistid   = null;
        let valid      = true;

        // Check if name exists
        let artistslist = artistscache.FindArtist(artistname, "strcmp");
        if(artistslist.length == 1)
            artistid = artistslist[0].id;

        // Try to find and show artists with similar name
        this.popup.ShowArtistsList(rawvalue);

        // Check if input is valid at all
        if(typeof this.oninput === "function")
            valid = this.oninput(artistid, artistname);

        return valid;
    }



    // Reimplement the Input-Interface
    SetValidState(valid)
    {
        this.input.SetValidState(valid);
    }
    GetValidState(valid)
    {
        return this.input.GetValidState();
    }



    GetValue()
    {
        return this.input.GetValue();
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

