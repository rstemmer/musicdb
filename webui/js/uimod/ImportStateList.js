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

/*
 * TODO:
 *  - rename to UploadStateList? (or two lists?)
 * */

class ImportStateListItem extends StatusElementBase
{
    constructor(text, state=null)
    {
        super("li", ["ImportStateListItem", "flex-row"], text, state);
    }
}


class ImportStateList extends Element
{
    constructor()
    {
        super("ul", ["ImportStateList", "flex-column"]);

        this.states = new Object();
        this.AddState("uploading",     "Uploading selected file");
        this.AddState("preprocess",    "Preprocessing uploaded file");
        this.AddState("integrate",     "Integrating upload into the music directory");
        this.AddState("importmusic",   "Importing upload into the music database");
        this.AddState("importartwork", "Generating artwork for the user interface");
    }



    AddState(statename, statelabel)
    {
        let item = new ImportStateListItem(statelabel, "unknown");
        this.states[statename] = item;
        this.element.appendChild(item.GetHTMLElement());
        return;
    }



    SetState(statename, state)
    {
        this.states[statename].SetState(state);
    }
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

