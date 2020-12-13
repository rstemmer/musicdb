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



class ButtonBox_AddSongToQueue extends ButtonBox
{
    constructor(songid)
    {
        super();
        this.songid = songid;
        this.AddButton(new SVGButton("Append", ()=>{this.AddSongToQueue("last");}));
        this.AddButton(new SVGButton("Insert", ()=>{this.AddSongToQueue("next");}));
    }


    AddSongToQueue(position)
    {
        event.preventDefault();
        //event.stopPropagation();
        // The onClick event must be propagated to the Search Result Preview
        // so that the preview recognizes an action an can close itself.
        MusicDB_Call("AddSongToQueue", {songid: this.songid, position: position});
    }
}



class ButtonBox_QueueEntryControls extends ButtonBox
{
    constructor(musictype, musicid, entryid)
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



class ButtonBox_QueueControls extends ButtonBox
{
    constructor()
    {
        super();

        this.addlast = new SVGButton("Add",    ()=>{this.AddRandomMusic("last");});
        this.addnext = new SVGButton("Insert", ()=>{this.AddRandomMusic("next");});
        this.AddButton(this.addlast);
        this.AddButton(this.addnext);
    }



    AddRandomMusic(position)
    {
        let musictype = mdbmodemanager.GetCurrentMode();
        let command   = null;
        if(musictype == "audio")
        {
            command = "AddRandomSongToQueue";
        }
        else if(musictype == "video")
        {
            command = "AddRandomVideoToQueue";
        }

        MusicDB_Call(command, {position: position});
        return;
    }



    UpdateTooltips()
    {
        let musictype = mdbmodemanager.GetCurrentMode();
        if(musictype == "audio")
        {
            this.addlast.SetTooltip("Add random song to the queue end");
            this.addnext.SetTooltip("Add random song to the queue begin");
        }
        else if(musictype == "video")
        {
            this.addlast.SetTooltip("Add random video to the queue end");
            this.addnext.SetTooltip("Add random video to the queue begin");
        }
        return;
    }
}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

