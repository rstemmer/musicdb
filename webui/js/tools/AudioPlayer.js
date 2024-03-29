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

class AudioPlayer extends Element
{
    constructor(source, classes=[])
    {
        super("audio", classes);
        this.element.controls = "controls";
        this.element.preload  = "none";
        this.isplaying        = false;

        this.element.onerror   = (event)=>{this.onError(event);};
        this.element.onwaiting = (event)=>{this.onWaiting(event);};
        this.element.onstalled = (event)=>{this.onStalled(event);};
        this.element.onsuspend = (event)=>{this.onSuspend(event);};
        this.element.onended   = (event)=>{this.onEnded(event);};
        this.element.oncanplay = (event)=>{this.onCanPlay(event);};

        this.SetSource(source);
        this.SetErrorCallback(null);
        this.SetStreamStatusCallback(null);
    }



    onWaiting(event)
    {
        window.console?.log(`onWaiting`);
        if(typeof this.statuscallback === "function")
            this.statuscallback(event, "waiting");
    }

    onStalled(event)
    {
        window.console?.log(`onStalled`);
        if(typeof this.statuscallback === "function")
            this.statuscallback(event, "stalled");
    }

    onSuspend(event)
    {
        window.console?.log(`onSuspend`);
        if(typeof this.statuscallback === "function")
            this.statuscallback(event, "suspend");
    }

    onEnded(event)
    {
        window.console?.log(`onEnded`);
        if(typeof this.statuscallback === "function")
            this.statuscallback(event, "ended");
    }

    onCanPlay(event)
    {
        window.console?.log(`onCanPlay`);
        if(typeof this.statuscallback === "function")
            this.statuscallback(event, "canplay");
    }

    onError(event)
    {
        // Get error code
        // Type: MediaError: https://developer.mozilla.org/en-US/docs/Web/API/MediaError
        let error = event.target.error;
        let code  = error.code;

        let message;
        switch(code)
        {
            case 1:
                message = "Connecting aborted by the user.";
                break;
            case 2:
                message = "Network connection error. Are you online? Is the URL correct (incl. protocol, port number)?";
                break;
            case 3:
                message = "Decoding failed. Is the URL actually addressing an audio stream? Is the port number correct? Did your audio driver having issues?";
                break;
            case 4:
                message = "Media source not suitable. If it is a TLS secured stream (https://), does your browser trust the certificate?";
                break;
        }

        window.console?.error(`Error: ${message}`);
        if(typeof this.errorcallback === "function")
            this.errorcallback(event, message);
        if(typeof this.statuscallback === "function")
            this.statuscallback(event, "error");
    }



    SetSource(source)
    {
        this.element.src = source;
    }

    ResetSource()
    {
        this.SetSource(this.element.src);
    }



    IsPlaying()
    {
        return this.isplaying;
    }



    SetErrorCallback(callback)
    {
        this.errorcallback = callback;
    }

    SetPlaysCallback(callback)
    {
        this.element.onplay = callback;
    }

    SetPausedCallback(callback)
    {
        this.element.onpause = callback;
    }

    SetStreamStatusCallback(callback)
    {
        this.statuscallback = callback;
    }



    Play()
    {
        this.isplaying = true;
        this.element.play();
    }

    Stop()
    {
        this.isplaying = false;
        this.element.pause();
        this.ResetSource();
    }
}



class SongPlayer extends AudioPlayer
{
    constructor(songpath)
    {
        let url = EncodePath("/musicdb/music/" + songpath);
        super(url);
    }
}




// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

