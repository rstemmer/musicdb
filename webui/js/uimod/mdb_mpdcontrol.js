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

// mode can be "audio" or "video"
function ShowMDBControls(parentID)
{
    let mode = mdbmodemanager.GetCurrentMode();
    let html = "";

    html += "<div id=MDBControls>"; // main box
    // Frame
    html += "<div id=MDBCMainFrame class=\"fmcolor\">";
    
    // Pause/Play
    html += "<div";
    html += " id=MDBCPauseButton";
    html += " class=\"MDBC_button hlcolor\"";
    html += ">";
    html += "…";
    html += "</div>";

    // Next
    html += "<div";
    html += " id=MDBCNextButton";
    html += " class=\"MDBC_button hlcolor\"";
    html += ">";
    html += "…";
    html += "</div>";

    html += "</div>"; // frame
    html += "</div>"; // main box

    // Create Element
    let parentelement = document.getElementById(parentID);
    parentelement.innerHTML = html;
    UpdateMDBControls(null, mode);
    UpdateStyle();  // Colorize text correctly
}


// Valid states: unknown, playing, paused, *null* (to change nothing)
// Valid modes: audio, video, *null*
function UpdateMDBControls(serverstate)
{
    let playbutton = document.getElementById("MDBCPauseButton");
    let nextbutton = document.getElementById("MDBCNextButton");
    let mode       = mdbmodemanager.GetCurrentMode();

    if(playbutton)
    {
        if(typeof serverstate === "string")
        {
            let buttonlabel = "";

            if(serverstate === "playing")
                buttonlabel = "Pause Stream";
            else if(serverstate === "paused")
                buttonlabel = "Continue Stream";
            else
                buttonlabel = "(Server State Unknown)";

            playbutton.textContent = buttonlabel;
        }

        if(typeof mode === "string")
        {
            if(mode == "audio")
            {
                playbutton.title   = "Update Audio Stream State";
                playbutton.onclick = (event) => { MusicDB_Call("SetAudioStreamState", {state:"playpause"}); };
            }
            else if(mode == "video")
            {
                playbutton.title   = "Update Video Stream State";
                playbutton.onclick = (event) => { MusicDB_Call("SetVideoStreamState", {state:"playpause"}); };
            }
        }
    }


    if(nextbutton)
    {
        if(typeof mode === "string")
        {
            if(mode == "audio")
            {
                nextbutton.title       = "Play Next Song from Queue";
                nextbutton.onclick     = (event) => { MusicDB_Call("PlayNextSong"); };
                nextbutton.textContent = "Next Song";
            }
            else if(mode == "video")
            {
                nextbutton.title       = "Play Next Video from Queue";
                nextbutton.onclick     = (event) => { MusicDB_Call("PlayNextVideo"); };
                nextbutton.textContent = "Next Video";
            }
        }
    }
}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

