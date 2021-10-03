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

class MainView extends Element
{
    constructor(id, headline=null)
    {
        super("div", ["MainView", "flex-column"], id);
        this.headline   = headline
        if(this.headline != null)
            this.AppendChild(this.headline);

        this.UnlockView();
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

    onViewMounted()
    {
    }
    onViewUnmounted()
    {
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
        this.RemoveChilds();
        this.RemoveCSSClass("flex-column");
        this.AddCSSClass("flex-row");

        this.artwork = artwork;
        this.artwork.AddCSSClass("MainArtwork");

        this.column1 = new Element("div", ["column1", "flex-column", "flex-grow"]);
        this.column2 = new Element("div", ["column2", "flex-column"]);

        this.column1.AppendChild(this.headline);
        this.column2.AppendChild(this.artwork);
        this.AppendChild(this.column1);
        this.AppendChild(this.column2);
    }



    ReplaceArtwork(newartwork)
    {
        this.column2.ReplaceChild(newartwork, this.artwork);
        this.artwork = newartwork;
        this.artwork.AddCSSClass("MainArtwork");
        return;
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

