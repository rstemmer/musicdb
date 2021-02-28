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

class AlphabetBar
{
    constructor()
    {
        this.element = document.createElement("div");
        this.element.id = "AlphabetBar";
        this.element.classList.add("hlcolor");
        this.element.classList.add("smallfont");
        let alphabet = ["↑",
                        "A","B","C","D",
                        "E","F","G","H",
                        "I","J","K","L",
                        "M","N","O","P",
                        "Q","R","S","T",
                        "U","V","W","X",
                        "Y","Z",
                        "↓"];

        for(let marker of alphabet)
        {
            let button = this.CreateButton(marker);
            this.element.appendChild(button);
        }
    }



    GetHTMLElement()
    {
        return this.element;
    }



    CreateButton(marker)
    {
        let button = document.createElement("span");
        button.classList.add("button");
        button.innerText = marker;
        button.onclick   = ()=>{artistsview.ScrollToMarker(marker);};
        return button;
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

