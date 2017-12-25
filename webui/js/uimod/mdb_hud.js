/*
 * This class provides the HUD consisting of the following components:
 *
 * Requirements:
 *   - JQuery
 *   - mdb_hud.css
 *   - scrollto.js
 * Show:
 *   - ShowMusicDBHUD(parentID);
 *   - UpdateMusicDBHUD(MDBSong, MDBAlbum, MDBArtist)
 * Functions:
 *   - MDBHUD_SetAlbumCover(MDBAlbum);
 *   - MDBHUD_SetSongInformation(MDBSong, MDBAlbum, MDBArtist)
 * Callbacks:
 * Recommended Paths:
 *   sig: onSongChanged, onStatusChanged -> GetMPDState -> UpdateMusicDBHUD
 * Trigger: (fnc -> sig)
 *   - GetAlbum -> ShowAlbum
 *   - UpdateSongStatistic \_ GetSong->UpdateCurrentSong
 *   - tool:ScrollToArtist(artistid)
 */

"use strict";

function ShowMusicDBHUD(parentID)
{
    var html = "";

    html += "<div id=MusicDBHUD>"; // main box
    
    // Albumcover
    html += "<div id=MDBHUD_AlbumBox>";
    html += "   <img id=MDBHUD_AlbumCover ";
    html += "   src=\"pics/TouchIcon.png\" >";   // DEFAULT
    html += "</div>";

    // Song-Information
    html += "<div id=MDBHUD_InformationBox>";
    html += _MDBHUD_CreateSongInformationEntry("Songname");
    html += _MDBHUD_CreateSongInformationEntry("Albumname");
    html += _MDBHUD_CreateSongInformationEntry("Artistname");
    html += "</div>";
    
    // Song-Properties
    html += "<div id=\"GenreHUDBox\">";
    html += "   <div id=\"GenreHUD\" class=\"hlcolor\"></div>";
    html += "   <div id=\"SubgenreHUD\" class=\"hlcolor\"></div>";
    html += "</div>";
    html += "<div id=\"MoodHUD\" class=\"hlcolor\"></div>";
    html += "<div id=\"PropertyHUD\" class=\"hlcolor\"></div>";
    
    html += "</div>"; // main box

    // Create Element
    $("#"+parentID).html(html);
}

function _MDBHUD_CreateSongInformationEntry(elementid)
{
    var icon = "";
    if(elementid == "Songname")
        icon = "♫";
    else if(elementid == "Albumname")
        icon = "&#xf1c0;";    /* fa-database */
    else if(elementid == "Artistname")
        icon = "&#xf0c0;";    /* fa-group */
    else
        icon = "!"; // invalid elementid


    var html = "";

    // on Click-Event
    html += "<span id=MDBHUD_"+elementid+"Button class=mdbhud_sientry>";

    // Icon
    html += "<i id=MDBHUD_"+elementid+"Icon class=\"mdbhud_siicon hlcolor\">";
    html += icon;
    html += "</i>";
    // Text
    html += "<span id=MDBHUD_"+elementid+"Content></span>";

    html += "</span>";
    return html;
}



function MDBHUD_SetAlbumCover(MDBAlbum)
{
    var imgpath = EncodeArtworkPath(MDBAlbum.artworkpath);
    var albumid = MDBAlbum.id;

    var html = "";
    html += "<img id=MDBHUD_AlbumCover ";
    html += "src=\"" + imgpath + "\" ";
    html += "onClick=\"MusicDB_Request(\'GetAlbum\', \'ShowAlbum\', {albumid:"+albumid+"});\"";
    html += ">";

    $("#MDBHUD_AlbumBox").html(html);
}

function MDBHUD_SetSongInformation(MDBSong, MDBAlbum, MDBArtist)
{
    $("#MDBHUD_SongnameButton").off().on("click",
        function()
        {
            // TODO: Call Trainer
        }
    );
    $("#MDBHUD_AlbumnameButton").off().on("click",
        function()
        {
            MusicDB_Request("GetAlbum", "ShowAlbum", {albumid:MDBAlbum.id});
        }
    );
    $("#MDBHUD_ArtistnameButton").off().on("click",
        function()
        {
            ScrollToArtist(MDBArtist.id);
        }
    );

    $("#MDBHUD_SongnameContent").html(MDBSong.name);
    $("#MDBHUD_AlbumnameContent").html(MDBAlbum.name);
    $("#MDBHUD_ArtistnameContent").html(MDBArtist.name);
}

function UpdateMusicDBHUD(MDBSong, MDBAlbum, MDBArtist)
{
    MDBHUD_SetAlbumCover(MDBAlbum);
    MDBHUD_SetSongInformation(MDBSong, MDBAlbum, MDBArtist);
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

