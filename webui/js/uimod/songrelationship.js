
"use strict";
/*
 * This class provides the mdbstate view consisting of the following components:
 *
 * Requirements:
 *   - JQuery
 *   - mdbsearch.css
 *   - tools/hovpacity
 * Show:
 * Functions:
 * Callbacks:
 * Recommended Paths:
 * Trigger: (fnc -> sig)
 *   - Find -> ShowSearchResults
 *
 */

function ShowSongRelationship(parentID, songid, MDBSonglist)
{
    var html = "";
    html += "<div id=SRMainBox>";

    for(var i in MDBSonglist)
    {
        var MDBSong     = MDBSonglist[i].song;
        var MDBAlbum    = MDBSonglist[i].album;
        var MDBArtist   = MDBSonglist[i].artist;
        var weight      = MDBSonglist[i].weight;
        var topbuttons  = Button_AddSongToQueue(MDBSong.id);
        var bottombuttons;
        bottombuttons   = Button_RelationshipControls(songid, MDBSong.id, MDBSong.name, weight);

        if(i > 0)
            html += "<div class=\"SREntrySeparator\"></div>";

        var opacity;
        if(weight < 5)
            opacity = weight / 5;
        else
            opacity = 1.0;

        html += "<div class=\"SRSongListEntry fmcolor\">";
        html += "<div class=\"SRRelevance fmcolor\" style=\"opacity:"+opacity+";\"></div>"
        html += CreateSongTile(MDBSong, MDBAlbum, MDBArtist, topbuttons, bottombuttons);
        html += "</div>";
    }

    html += "</div>";
    
    // Create Element
    $("#"+parentID).html(html);
    // New elements were created, update there colors with the current style
    UpdateStyle();
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

