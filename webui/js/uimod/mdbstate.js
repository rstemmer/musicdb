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

/* OLD!
 * This class provides the mdbstate view consisting of the following components:
 *
 * Requirements:
 *   - JQuery
 *   - mdbstate.css
 * Show:
 *   - ShowMusicDBStateView(parentid)
 *   - SetMusicDBOnlineState(mdbstate, mpdstate)
 *   - SetMusicDBPlayingState(serverstate, clientstate)
 * Functions:
 * Callbacks:
 * Recommended Paths:
 * Trigger: (fnc -> sig)
 *
 * Timer:
 *   When the queue is loaded first clear the timer, then add the playtime of each queue entry
 *   On onTimeChanged-mpd-event set the TimePlayed. This call will also update the view
 */

//var GLOBAL_MDBMODE = "audio"; // audio/video

function ShowMusicDBStateView(parentID)
{
    let html = "";

    html += "<div id=MDBStateView class=\"hlcolor smallfont\">";

    // Data Stream (MusicDB)
    html += "<span id=MDBReconnectBtn data-online=\"unknown\""; 
    html += " title=\"Reconnect to MusicDB server\"";
    html += " onclick=\"ConnectToMusicDB();\">";
    html += "&#xf021;";
    html += "</span>";
    html += "<span id=DataStreamState class=\"onlinestate\" data-online=\"unknown\">";
    html += "MusicDB";
    html += "</span><br>";

    // Audio Stream (Icecast)
    html += "<span id=AudioStreamState class=\"onlinestate\" data-online=\"unknown\">";
    html += "Audio Stream";
    html += "</span><br>";

    // Video Stream (MusicDB)
    html += "<span id=VideoStreamState class=\"onlinestate\" data-online=\"unknown\">";
    html += "Video Stream";
    html += "</span><br>";
/*
    // Mode Select
    html += "<span id=MDBModeswitchBtn";
    html += " title=\"Switch between Audio/Video mode\"";
    html += " onClick=\"ToggleMusicDBMode();\"";
    html += ">";
    html += "↹";
    html += "</span>";
    html += "<span id=MDBMode";
    html += " class=\"onlinestate\"";
    html += " data-mode=\"unknown\"";
    html += " onClick=\"ToggleMusicDBMode();\"";
    html += ">";
    html += "Stream Mode";
    html += "</span><br>";
*/

    // Playtime
    html += "<span id=CurrentTime class=\"timestats\" data-playstate=\"unknown\">";
    html += "00:00:00";
    html += "</span>";
    html += " / ";
    html += "<span id=PlayTime class=\"timestats\" data-playstate=\"unknown\">";
    html += "00:00:00";
    html += "</span>";

    html += "</div>";
    
    // Create Elements
    document.getElementById(parentID).innerHTML = html;
    ShowMDBControls("Controls");
    UpdateMDBControls(null);
}



// Valid states: yes, no, error, unknown, *null* (to change nothing)
function SetMusicDBOnlineState(datastreamstate, audiostreamstate, videostreamstate)
{
    let audioelement = document.getElementById("AudioStreamState");
    let videoelement = document.getElementById("VideoStreamState");
    let dataelement  = document.getElementById("DataStreamState");
    let reconnect    = document.getElementById("MDBReconnectBtn"); // shall have same state as data stream state

    if(typeof audiostreamstate === "string")
    {
        audioelement.dataset.online = audiostreamstate;
    }
    
    if(typeof videostreamstate === "string")
    {
        videoelement.dataset.online = videostreamstate;
    }
    
    if(typeof datastreamstate === "string")
    {
        dataelement.dataset.online = datastreamstate;
        reconnect.dataset.online = datastreamstate;
    }
}



// Valid states: unknown, playing, paused, *null* (to change nothing)
function SetMusicDBPlayingState(serverstate, clientstate)
{
    let sselement  = document.getElementById("PlayTime");
    let cselement  = document.getElementById("CurrentTime");

    if(typeof serverstate === "string")
        sselement.dataset.playstate = serverstate;
    if(typeof clientstate === "string")
        cselement.dataset.playstate = serverstate;

    window.console && console.log("SetMusicDBPlayingState");

    UpdateMDBControls(serverstate);
}



var GLOBAL_TotalPlaytime = 0;   // total playtime of all songs in the queue
var GLOBAL_TimePlayed    = 0;   // time the first song in the queue was played

function AddPlaytime(playtime)
{
    GLOBAL_TotalPlaytime += playtime;
}

function ClearPlaytime()
{
    GLOBAL_TotalPlaytime = 0;
}

function SetTimePlayed(played)
{
    GLOBAL_TimePlayed = played;
    // Ugly but works fine for now.
    // SetTimePlayed gets called by the websocket handler. 
    // The server sends every second the current state of the currently playing song.
    // So this function gets called every second independent if the song is playing or not.
    UpdateTimeview();
}

function UpdateTimeview()
{
    // Get current time
    let date = new Date();

    let h = date.getHours();
    let m = date.getMinutes();
    let s = date.getSeconds();

    // Calculate estimated end time (hours, minutes and seconds)
    let es, em, eh;
    es = s + GLOBAL_TotalPlaytime - GLOBAL_TimePlayed;
    em = m + Math.floor(es / 60);
    es = Math.floor(es % 60);
    eh = h + Math.floor(em / 60);
    em = Math.floor(em % 60);
    eh = Math.floor(eh % 24);

    // convert to string
    let currenttime = HMSToString( h,  m,  s);
    let endtime     = HMSToString(eh, em, es);

    // Display time
    let ctimeelement = document.getElementById("CurrentTime");
    let ptimeelement = document.getElementById("PlayTime");
    ctimeelement.innerHTML = currenttime;
    ptimeelement.innerHTML = endtime;
}

/*
function ToggleMusicDBMode()
{
    // Switch mode
    if(GLOBAL_MDBMODE == "audio")
    {
        MusicDB_Call("SetAudioStreamState", {state:"pause"});
        GLOBAL_MDBMODE = "video";
    }
    else
    {
        MusicDB_Call("SetVideoStreamState", {state:"pause"});
        GLOBAL_MDBMODE = "audio";
    }

    // Reset genre-selection timer
    if(reloadtimeouthandler !== null)
    {
        clearTimeout(reloadtimeouthandler);
        reloadtimeouthandler = null;
    }

    // Get artist list for new mode
    _MDBState_RequrestContentUpdate();
    // The UpdateMDBState signal make other clients to request the data by them self.
    // So there is no need for a Broadcast-Request
    
    // Inform everyone about the mode change
    // The Call will trigger a broadcast of GetMDBState
    // By making a Request and giving a function signature the broadcast
    // gets handled exactly like a GetMDBState request
    MusicDB_Request("SetMDBState", "UpdateMDBState",
        {category:"MusicDB", name:"uimode", value:GLOBAL_MDBMODE});
}
*/

/*
function UpdateMusicDBMode(MDBState)
{
    // Check and update UI Mode
    if(GLOBAL_MDBMODE != MDBState.MusicDB.uimode)
    {
        GLOBAL_MDBMODE = MDBState.MusicDB.uimode;
        _MDBState_RequrestContentUpdate();    // Reload Artist list for new Mode
    }    

    // Update UI
    UpdateMDBControls(null, GLOBAL_MDBMODE);
    
    let modeelement = document.getElementById("MDBMode");
    modeelement.dataset.mode = GLOBAL_MDBMODE;

    // Show/Hide video panel
    let videopanel  = document.getElementById("VideoPanel");
    let panels      = document.getElementById("Panels");
    if(GLOBAL_MDBMODE == "audio")
    {
        panels.dataset.panels      = "1";
        videopanel.dataset.visible = "false";
    }
    else
    {
        panels.dataset.panels      = "2";
        videopanel.dataset.visible = "true";
    }

}
*/
/*
function _MDBState_RequrestContentUpdate()
{
    if(GLOBAL_MDBMODE == "audio")
    {
        MusicDB_Request("GetFilteredArtistsWithAlbums", "ShowArtists");
        MusicDB_Request("GetSongQueue",                 "ShowSongQueue");
    }
    else if(GLOBAL_MDBMODE == "video")
    {
        MusicDB_Request("GetFilteredArtistsWithVideos", "ShowArtists");
        MusicDB_Request("GetVideoQueue",                "ShowVideoQueue");
    }
}
*/

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

