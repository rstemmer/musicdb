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

/*
 * This class provides the artistloader.
 * It is possible to select a set of genres and/or to reload the artists-list
 */

function ShowMPDControls(parentID)
{
    window.console && console.log("ShowMPDControls is deprecated. Use ShowMDBControls instead!");
    return ShowMDBControls(parentID, "audio");
}

// mode can be "audio" or "video"
function ShowMDBControls(parentID, mode)
{
    let html = "";

    html += "<div id=MDBControls>"; // main box
    // Frame
    html += "<div id=MDBCMainFrame class=\"fmcolor\">";
    
    // Pause/Play
    html += "<div";
    html += " id=MDBCPauseButton";
    html += " class=\"MDBC_button hlcolor\"";
    if(mode == "audio")
    {
        html += " title=\"Play/Pause song\"";
        html += " onClick=\"MusicDB_Call(\'SetAudioStreamState\', {state:\'playpause\'});\"";
    }
    else if(mode == "video")
    {
        html += " title=\"Play/Pause video\"";
        html += " onClick=\"MusicDB_Call(\'SetVideoStreamState\', {state:\'playpause\'});\"";
    }
    html += ">";
    html += "Pause/Play";
    html += "</div>";

    // Next
    html += "<div";
    html += " id=MDBCNextButton";
    html += " class=\"MDBC_button hlcolor\"";
    if(mode == "audio")
    {
        html += " title=\"Play next song from queue\"";
        html += " onClick=\"MusicDB_Call(\'PlayNextSong\');\"";
    }
    else if(mode == "video")
    {
        html += " title=\"Play next video from queue\"";
        html += " onClick=\"MusicDB_Call(\'PlayNextVideo\');\"";
    }
    html += ">";
    if(mode == "audio")
    {
        html += "Next Song";
    }
    else if(mode == "video")
    {
        html += "Next Video";
    }
    html += "</div>";

    html += "</div>"; // frame
    html += "</div>"; // main box

    // Create Element
    let parentelement = document.getElementById(parentID);
    parentelement.innerHTML = html;
    UpdateStyle();  // Colorize text correctly
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

