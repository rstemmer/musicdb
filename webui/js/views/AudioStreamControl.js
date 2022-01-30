// MusicDB,  a music manager with web-bases UI that focus on music.
// Copyright (C) 2017 - 2021  Ralf Stemmer <ralf.stemmer@gmx.net>
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


class AudioStreamControl extends Element
{
    constructor()
    {
        super("div", ["AudioStreamControl", "flex-column"]);

        this.button = new MenuEntry();
        this.button.Update(new SVGIcon("MusicDB"), "button", ()=>{this.onClick_PlayPause();}, "Tooltip");

        this.streamstatus = new StatusText();

        this.player = new AudioStreamPlayer();
        this.player.SetErrorCallback((event, message)=>{this.onStreamError(event, message);});
        this.player.SetPlaysCallback((event)=>{this.onStreamPlays(event);});
        this.player.SetStreamStatusCallback((event, state)=>{this.onStreamStatusUpdate(event, state);});
        this.player.Hide();

        this.streamerror = new MessageBarError();

        this.StopStream();

        this.AppendChild(this.player);
        this.AppendChild(this.button);
        this.AppendChild(this.streamstatus);
        this.AppendChild(this.streamerror);
    }



    onStreamError(event, message)
    {
        this.streamerror.UpdateMessage(`Error: ${message}`);
        this.streamerror.Show();
    }

    onStreamPlays(event)
    {
        this.streamerror.Hide();
    }

    onStreamStatusUpdate(event, state)
    {
        this.streamstatus.Show();
        switch(state)
        {
            case "error":
                this.streamstatus.SetStatus("bad", "Connection Failed");
                break;

            case "waiting":
                this.streamstatus.SetStatus("active", "Waiting for Data");
                break;

            case "stalled":
                this.streamstatus.SetStatus("active", "Stream Stalled");
                break;

            case "suspend":
                if(this.player.IsPlaying())
                    this.streamstatus.SetStatus("bad", "Stream Loading Suspend");
                else
                    this.streamstatus.Hide();
                break;

            case "ended":
                this.streamstatus.SetStatus("warn", "Failed");
                break;

            case "canplay":
                this.streamstatus.SetStatus("good", "Playing");
                this.streamstatus.Hide();
                break;

            default:
                window.console?.warn(`Unhandled status update ${state}`);
        }
    }



    PlayStream()
    {
        this.player.Play();
        this.button.Update(new SVGIcon("Pause"), "Disconnect", ()=>{this.onClick_PlayPause();},
            "Disconnect from the MusicDB Audio Stream.");
    }

    StopStream()
    {
        this.player.Stop();
        this.streamstatus.SetStatus("info", "Disconnected");
        this.button.Update(new SVGIcon("Play"), "Connect", ()=>{this.onClick_PlayPause();}, "Connect and play the MusicDB Audio Stream.");
    }



    onClick_PlayPause()
    {
        //event.preventDefault();
        event.stopPropagation();

        if(this.player.IsPlaying())
            this.StopStream();
        else
            this.PlayStream();
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        this.player.onMusicDBMessage(fnc, sig, args, pass);
    }
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

