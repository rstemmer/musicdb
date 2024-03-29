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

class SearchInput extends Element
{
    constructor(curtain=null)
    {
        super("div", ["SearchInput", "flex-row", "hlcolor", "hovpacity"]);
        this._AddInputBoxElements();

        this.curtain = curtain;
        if(this.curtain)
            this.curtain.AddClickEvent(()=>{this.HidePreview();});

        this.timeoutinterval = 500;
        this.preview = new SearchResultsPopup(()=>{this.HidePreview();});
        this.preview.Hide();
        this.AppendChild(this.preview);
    }



    _AddInputBoxElements()
    {
        this.icon        = new SVGIcon("Search");
        
        this.clearbutton = new SVGButton("Remove", ()=>{this.ClearInput();});
        this.clearbutton.GetHTMLElement().classList.add("hovpacity");
        this.clearbutton.SetTooltip("Clear search input and close preview");

        this.input       = document.createElement("input");
        this.input.oninput     = ()=>{this.onInput(event);};
        this.input.onkeyup     = ()=>{this.onKeyUp(event);};
        this.input.onclick     = ()=>{this.onClick(event);};
        this.input.type        = "search";
        this.input.placeholder = "Search…";

        this.AppendChild(this.icon);
        this.AppendChild(this.input);
        this.AppendChild(this.clearbutton);

        this.showpreview = false;
        this.showresults = false;
        this.target      = "none";
        return;
    }



    // Gets executed from from timer -> no this-object
    Find(searchstring, target)
    {
        if(target == "preview")
        {
            MusicDB.Request("Find", "ShowPreview", {searchstring:searchstring, limit:5});
        }
        else if(target == "results")
        {
            MusicDB.Request("Find", "ShowResults", {searchstring:searchstring, limit:20});
        }
        return;
    }



    ClearInput()
    {
        this.input.value = "";
        this.preview.Hide();
        return;
    }



    ShowPreview()
    {
        if(this.curtain)
            this.curtain.Show();

        this.showpreview = true;
        this.target      = "preview";
        this.preview.Show();
    }
    HidePreview()
    {
        if(this.curtain)
            this.curtain.Hide();

        this.showpreview = false;
        this.target      = "none";
        this.preview.Hide();
    }
    ShowResults()
    {
        this.HidePreview();
        this.showresults = true;
        this.target      = "results";
    }
    HideResults()
    {
        this.showresults = false;
        this.target      = "none";
    }



    // Events from the text input element
    onInput(event)
    {
        if(this.input.value.length <= 0)
        {
            this.HidePreview();
            return;
        }

        // Check if the results shall be presented in the preview or an open results view
        let searchresultsview = document.getElementById("SearchResultsView");
        if(searchresultsview == null)
        {
            this.HideResults();
            this.ShowPreview();
        }

        // Reset timer and request a new search
        if(this.timeouthandler)
            clearTimeout(this.timeouthandler)

        this.timeouthandler = setTimeout(this.Find, this.timeoutinterval, this.input.value, this.target);
        return;
    }


    onKeyUp(event)
    {
        let keycode = event.which || event.keyCode;
        if(keycode == 13 /*ENTER*/ && this.input.value.length > 0)
        {
            this.ShowResults();
            this.timeouthandler = setTimeout(this.Find, this.timeoutinterval, this.input.value, this.target);
        }
        else if(keycode == 27 /*ESC*/)
        {
            this.HidePreview();
        }
        return;
    }


    onClick(event)
    {
        if(this.input.value.length > 0)
        {
            this.ShowPreview();
            this.HideResults();
        }
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        if(fnc == "Find")
        {
            if(sig == "ShowPreview")
            {
                this.preview.Update(args.artists, args.albums, args.songs);
                this.ShowPreview();
            }
        }
        return;
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

