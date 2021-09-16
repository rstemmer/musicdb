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

// Control buttons can have the following stated: "play", "stop"
// The state represents the action that will be done when pressing the button


class MusicDBControls extends Element
{
    constructor()
    {
        super("div", ["MusicDBControlsBox", "frame", "hovpacity", "hlcolor"]);

        this.controls = new Object();
        this.controls["audio"] = this._CreateControls("audio");
        this.controls["video"] = this._CreateControls("video");
        this.ShowAudioControls();
    }



    ShowAudioControls()
    {
        this.RemoveChilds()
        this.AppendChild(this.controls["audio"].element);
    }

    ShowVideoControls()
    {
        this.RemoveChilds()
        this.AppendChild(this.controls["video"].element);
    }


    UpdateButton(button, text, tooltip, state)
    {
        button.SetInnerText(text);
        button.SetTooltip(tooltip);
        button.SetData("state", state);
    }


    SetAudioStatus(state) // "playing"/"stopped"
    {
        if(typeof this.predictiontimeoutid === "number")
        {
            window.clearTimeout(this.predictiontimeoutid);
            this.predictiontimeoutid = null;
            return; // Status is already set
        }

        let playbutton = this.controls["audio"].playbutton

        if(state == "playing")
        {
            this.UpdateButton(playbutton, "Pause Audio Stream", "Pause audio streaming on server side for all clients", "stop");
        }
        else if(state == "stopped")
        {
            this.UpdateButton(playbutton, "Play Audio Stream", "Continue audio streaming on server side for all clients", "play");
        }
    }
    SetVideoStatus(state) // "playing"/"stopped"
    {
        if(typeof this.predictiontimeoutid === "number")
        {
            window.clearTimeout(this.predictiontimeoutid);
            this.predictiontimeoutid = null;
            return; // Status is already set
        }

        let playbutton = this.controls["video"].playbutton

        if(state == "playing")
        {
            this.UpdateButton(playbutton, "Pause Video Stream", "Pause video streaming for all clients", "stop");
        }
        else if(state == "stopped")
        {
            this.UpdateButton(playbutton, "Play Video Stream", "Continue video streaming for all clients", "play");
        }
    }



    // mode = "audio", "video"
    onPlayPause(mode)
    {
        // To be more responsive, directly update the button state and do not wait on the servers response
        // The server response that finally sets the actual state.
        let btnstate = this.controls[mode].playbutton.GetData("state");
        let newstate;

        // Assume new state
        if(btnstate == "stop")
            newstate = "stopped";
        else if(btnstate == "play")
            newstate = "playing";

        // Set new state and tell the server
        if(mode == "audio")
        {
            this.SetAudioStatus(newstate);
            MusicDB_Call("SetAudioStreamState", {state:"playpause"});
        }
        else if(mode == "video")
        {
            this.SetVideoStatus(newstate);
            MusicDB_Call("SetVideoStreamState", {state:"playpause"});
        }

        // In case the server does not response, accept that the prediction failed.
        this.predictiontimeoutid = window.setTimeout(()=>{this.onPredictionFailed(mode, newstate)}, 1500/*ms*/);

        return;
    }



    onPredictionFailed(mode, predictedstate)
    {
        let playbutton = this.controls[mode].playbutton
        this.UpdateButton(playbutton, "Play/Pause Failed!", "Connection to MusicDB Server lost", "error");
        return;
    }



    _CreateControls(streamtype)
    {
        let controls   = new Object();
        let streamname;
        let musicname;
        if(streamtype === "audio")
        {
            streamname = "Audio";
            musicname  = "Song";
        }
        else if(streamtype === "video")
        {
            streamname = "Video";
            musicname  = "Video";
        }
        else
        {
            window.console?.error(`type must be "audio" or "video". Typed was "${type}"!`);
            return;
        }

        // Create Play/Pause Button
        let playbutton = new Element("div", ["playbutton"]);
        this.UpdateButton(playbutton, `Play/Pause ${streamname} Stream`, `Update ${streamname} Stream State`, "unknwon");
        playbutton.element.onclick = (event) => {this.onPlayPause(streamtype);};
        
        // Create Next Button
        let nextbutton = new Element("div", ["nextbutton"]);
        this.UpdateButton(nextbutton, `Next ${musicname}`, `Play Next ${musicname} from the Queue`, "unknwon");
        nextbutton.element.onclick = (event) => {MusicDB_Call(`PlayNext${musicname}`);};

        // Put all Buttons Together
        let element = new Element("div", ["musicdbcontrols"]);
        element.AppendChild(playbutton);
        element.AppendChild(nextbutton);

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

