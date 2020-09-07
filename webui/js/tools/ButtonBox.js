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

class ButtonBox
{
    constructor()
    {
        this.element = document.createElement("div");
        this.element.classList.add("ButtonBox");
        this.element.classList.add("flex-row");
        this.element.classList.add("hovpacity");
    }



    GetHTMLElement()
    {
        return this.element;
    }



    AddButton(svgbutton)
    {
        this.element.appendChild(svgbutton.GetHTMLElement());
    }
}


class ButtonBox_AddVideoToQueue extends ButtonBox
{
    constructor(videoid)
    {
        super();
        this.videoid = videoid;
        this.AddButton(new SVGButton("Append", ()=>{this.AddVideoToQueue("last");}));
        this.AddButton(new SVGButton("Insert", ()=>{this.AddVideoToQueue("next");}));
    }


    AddVideoToQueue(position)
    {
        event.preventDefault();
        event.stopPropagation();
        MusicDB_Call("AddVideoToQueue", {videoid: this.videoid, position: position});
    }
}



class ButtonBox_QueueEntryControls extends ButtonBox
{
    constructor(musictype, entryid, musicid)
    {
        super();

        if(musictype == "audio")
        {
            this.AddButton(new SVGButton("Relation", ()=>{this.GetSongRelationship(musicid);}));
            this.AddButton(new SVGButton("Remove",   ()=>{this.RemoveSongFromQueue(entryid);}));
        }
        else if(musictype == "video")
        {
            this.AddButton(new SVGButton("Remove",   ()=>{this.RemoveVideoFromQueue(entryid);}));
        }
    }


    GetSongRelationship(musicid)
    {
        MusicDB_Request("GetSongRelationship", "ShowSongRelationship", {songid: musicid});
    }
    RemoveSongFromQueue(entryid)
    {
        MusicDB_Call("RemoveSongFromQueue", {entryid: entryid});
    }
    RemoveVideoFromQueue(entryid)
    {
        MusicDB_Call("RemoveVideoFromQueue", {entryid: entryid});
    }

}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

