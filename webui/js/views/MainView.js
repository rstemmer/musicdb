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

class MainView
{
    constructor(id, headline=null)
    {
        this.headline   = headline
        this.element    = document.createElement("div");
        this.element.classList.add("MainView");
        this.element.classList.add("flex-column");
        this.element.id = id;
        if(this.headline != null)
            this.element.appendChild(this.headline.GetHTMLElement());

        this.UnlockView();
    }



    GetHTMLElement()
    {
        return this.element;
    }



    // The view lock is checked by the ViewManager and can be used
    // to avoid automatically switching between views.
    // If a view is visible and locked, it will never be replaced by a different view
    LockView()
    {
        this.viewlock = true;
    }
    UnlockView()
    {
        this.viewlock = false;
    }
    GetLockState()
    {
        return this.viewlock;
    }
}


/*
 * View Layout:
 *     this.column1            this.column2
 *   ┌───────────────────────┬───────────────┐
 *   │                       │               │
 *   │  this.headline        │  ┌─────────┐  │
 *   │                       │  │         │  │
 *   ├───────────────────────┤  │ /_\    /│  │
 *   │                       │  │/   \/\/ │  │
 *   │                     █ │  │ Artwork │  │
 *   │                     █ │  └─────────┘  │
 *   │                     ░ │ this.artwork  │
 *   │                     ░ ├───────────────┤
 *   │                     ░ │               │
 *   │                     ░ │               │
 *   └───────────────────────┴───────────────┘
 * 
 */

class MainView2 extends MainView
{
    constructor(id, headline, artwork)
    {
        super(id, headline);
        // reset settings from base class
        this.element.innerHTML = "";    
        this.element.classList.remove("flex-column");
        this.element.classList.add("flex-row");

        this.artwork = artwork;
        this.artwork.GetHTMLElement().classList.add("MainArtwork");

        this.column1 = document.createElement("div");
        this.column1.classList.add("column1");
        this.column1.classList.add("flex-column");
        this.column1.classList.add("flex-grow");
        this.column2 = document.createElement("div");
        this.column2.classList.add("column2");
        this.column2.classList.add("flex-column");

        this.column1.appendChild(this.headline.GetHTMLElement());
        this.column2.appendChild(this.artwork.GetHTMLElement());
        this.element.appendChild(this.column1);
        this.element.appendChild(this.column2);
    }



    ReplaceArtwork(newartwork)
    {
        this.column2.replaceChild(newartwork.GetHTMLElement(), this.artwork.GetHTMLElement());
        this.artwork = newartwork;
        this.artwork.GetHTMLElement().classList.add("MainArtwork");
        return;
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

