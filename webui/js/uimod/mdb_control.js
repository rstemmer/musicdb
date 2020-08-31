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

// Control buttons can have the following stated: "play", "stop"
// The state represents the action that will be done when pressing the button


class MusicDBControls
{
    constructor()
    {
        this.element        = document.createElement("div");
        this.element.classList.add("musicdbcontrolsslot");
        this.element.classList.add("hlcolor");

        this.controls = new Object();
        this.controls["audio"] = this._CreateControls("audio");
        this.controls["video"] = this._CreateControls("video");
        this.ShowAudioControls();
    }



    GetHTMLElement()
    {
        return this.element;
    }



    ShowAudioControls()
    {
        this.element.innerHTML = "";
        this.element.appendChild(this.controls["audio"].element);
    }

    ShowVideoControls()
    {
        this.element.innerHTML = "";
        this.element.appendChild(this.controls["video"].element);
    }


    SetAudioStatus(state) // "playing"/"stopped"
    {
        if(state == "playing")
        {
            this.controls["audio"].playbutton.textContent   = "Pause Audio Stream";
            this.controls["audio"].playbutton.title         = "Pause audio streaming on server side for all clients";
            this.controls["audio"].playbutton.dataset.state = "stop";
        }
        else if(state == "stopped")
        {
            this.controls["audio"].playbutton.textContent   = "Play Audio Stream";
            this.controls["audio"].playbutton.title         = "Continue audio streaming on server side for all clients";
            this.controls["audio"].playbutton.dataset.state = "play";
        }
    }
    SetVideoStatus(state) // "playing"/"stopped"
    {
        if(state == "playing")
        {
            this.controls["video"].playbutton.textContent   = "Pause Video Stream";
            this.controls["video"].playbutton.title         = "Pause video streaming for all clients";
            this.controls["video"].playbutton.dataset.state = "stop";
        }
        else if(state == "stopped")
        {
            this.controls["video"].playbutton.textContent   = "Play Video Stream";
            this.controls["video"].playbutton.title         = "Continue video streaming for all clients";
            this.controls["video"].playbutton.dataset.state = "play";
        }
    }



    _CreateControls(type)
    {
        let controls   = new Object();

        // Create Play/Pause Button
        let playbutton = document.createElement("div");
        playbutton.dataset.state = "unknown";
        playbutton.classList.add("playbutton");
        if(type == "audio")
        {
            playbutton.textContent = "Play/Pause Audio Stream";
            playbutton.title       = "Update Audio Stream State";
            playbutton.onclick     = (event) => { MusicDB_Call("SetAudioStreamState", {state:"playpause"}); };
        }
        else if(type == "video")
        {
            playbutton.textContent = "Play/Pause Video Stream";
            playbutton.title       = "Update Video Stream State";
            playbutton.onclick     = (event) => { MusicDB_Call("SetVideoStreamState", {state:"playpause"}); };
        }
        
        // Create Next Button
        let nextbutton = document.createElement("div");
        nextbutton.classList.add("nextbutton");
        if(type == "audio")
        {
            nextbutton.textContent = "Next Song";
            nextbutton.title       = "Play Next Song from Queue";
            nextbutton.onclick     = (event) => { MusicDB_Call("PlayNextSong"); };
        }
        else if(type == "video")
        {
            nextbutton.textContent = "Next Video";
            nextbutton.title       = "Play Next Video from Queue";
            nextbutton.onclick     = (event) => { MusicDB_Call("PlayNextVideo"); };
        }

        // Put all Buttons Together
        let element = document.createElement("div");
        element.classList.add("musicdbcontrols");
        element.appendChild(playbutton);
        element.appendChild(nextbutton);

        controls["playbutton"] = playbutton;
        controls["nextbutton"] = nextbutton;
        controls["element"]    = element;
        return controls;
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        if(fnc == "GetMDBState" && sig == "UpdateMDBState")
        {
            if(args.MusicDB.uimode == "audio")
                this.ShowAudioControls();
            else
                this.ShowVideoControls();
        }

        else if(fnc == "GetAudioStreamState")
        {
            if(args.isplaying)
                this.SetAudioStatus("playing");
            else
                this.SetAudioStatus("stopped");
        }

        else if(fnc == "GetVideoStreamState")
        {
            if(args.isstreaming)
                this.SetVideoStatus("playing");
            else
                this.SetVideoStatus("stopped");
        }

        return;
    }
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
