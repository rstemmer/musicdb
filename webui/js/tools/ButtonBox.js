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

class ButtonBox extends Element
{
    constructor()
    {
        super("div", ["ButtonBox", "flex-row", "hovpacity"]);
    }



    AddButton(svgbutton, tooltip=null)
    {
        if(tooltip !== null)
            svgbutton.SetTooltip(tooltip);
        this.AppendChild(svgbutton.GetHTMLElement());
    }
}


class ButtonBox_AddMusicToQueue extends ButtonBox
{
    // musictype: "song", "video"
    constructor(musictype, musicid)
    {
        super();
        this.musicid   = musicid;
        this.musictype = musictype;

        this.appendbutton = new SVGButton("Append", ()=>{this._AddMusicToQueue("last");});
        this.insertbutton = new SVGButton("Insert", ()=>{this._AddMusicToQueue("next");});
        this.AddButton(this.appendbutton, `Append this ${this.musictype} on the queue`);
        this.AddButton(this.insertbutton, `Insert this ${this.musictype} into the queue after current playing ${this.musictype}`);
    }


    _AddMusicToQueue(position)
    {
        queueview.AddFakeEntry(this.musictype, position);
        this.AddMusicToQueue(position);
    }

    AddMusicToQueue(position)
    {
        event.preventDefault();
        //event.stopPropagation();
        // The onClick event must be propagated to the Search Result Preview
        // so that the preview recognizes an action an can close itself.
        if(this.musictype == "song")
            MusicDB_Call("AddSongToQueue", {songid: this.musicid, position: position});
        else
            MusicDB_Call("AddVideoToQueue", {videoid: this.videoid, position: position});
    }
}


class ButtonBox_AddVideoToQueue extends ButtonBox_AddMusicToQueue
{
    constructor(videoid)
    {
        super("video", videoid);
    }
}



class ButtonBox_AddSongToQueue extends ButtonBox_AddMusicToQueue
{
    constructor(songid)
    {
        super("song", songid);
    }
}



class ButtonBox_QueueControls extends ButtonBox_AddMusicToQueue
{
    constructor()
    {
        super();
        this.UpdateTooltips();
    }



    AddMusicToQueue(position)
    {
        let musicdbmode = WebUI.GetManager("MusicMode").GetCurrentMode();
        let command     = null;
        if(musicdbmode == "audio")
        {
            command = "AddRandomSongToQueue";
        }
        else if(musicdbmode == "video")
        {
            command = "AddRandomVideoToQueue";
        }

        MusicDB_Call(command, {position: position});
        return;
    }



    UpdateTooltips()
    {
        let musicdbmode = WebUI.GetManager("MusicMode").GetCurrentMode();
        if(musicdbmode == "audio")
        {
            this.appendbutton.SetTooltip("Add random song to the queue end");
            this.insertbutton.SetTooltip("Add random song to the queue begin");
        }
        else if(musicdbmode == "video")
        {
            this.appendbutton.SetTooltip("Add random video to the queue end");
            this.insertbutton.SetTooltip("Add random video to the queue begin");
        }
        return;
    }
}



class ButtonBox_RelationControl extends ButtonBox
{
    constructor(songid, relatedsongid)
    {
        super();
        this.songid        = songid;
        this.relatedsongid = relatedsongid;

        this.AddButton(new SVGSpacer());
        this.AddButton(new SVGButton("CutRelation", ()=>{this.CutSongRelationship();}), "Delete relation with this song");
    }



    CutSongRelationship()
    {
        MusicDB_Request("CutSongRelationship", "ShowSongRelationship",
            {songid:this.songid, relatedsongid:this.relatedsongid});
        return;
    }
}



class ButtonBox_QueueEntryControls extends ButtonBox
{
    constructor(musictype, musicid, entryid, onremove=undefined)
    {
        super();
        this.SetOnRemoveCallback(onremove);

        if(musictype == "audio")
        {
            this.AddButton(new SVGButton("Relation", ()=>{this.GetSongRelationship(musicid);}), "Show related songs");
            this.AddButton(new SVGButton("Remove",   ()=>{this.RemoveSongFromQueue(entryid);}), "Remove this song from the queue");
        }
        else if(musictype == "video")
        {
            this.AddButton(new SVGButton("Remove",   ()=>{this.RemoveVideoFromQueue(entryid);}), "Remove this video from the queue");
        }
    }


    SetOnRemoveCallback(onremove)
    {
        this.onremove = onremove;
    }


    GetSongRelationship(musicid)
    {
        MusicDB_Request("GetSongRelationship", "ShowSongRelationship", {songid: musicid});
    }
    RemoveSongFromQueue(entryid)
    {
        if(typeof this.onremove === "function")
            this.onremove();
        MusicDB_Call("RemoveSongFromQueue", {entryid: entryid});
    }
    RemoveVideoFromQueue(entryid)
    {
        if(typeof this.onremove === "function")
            this.onremove();
        MusicDB_Call("RemoveVideoFromQueue", {entryid: entryid});
    }

}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

