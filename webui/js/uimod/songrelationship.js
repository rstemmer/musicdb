
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

    let currentartist = -1;
    for(let i in MDBSonglist)
    {
        let MDBSong     = MDBSonglist[i].song;
        let MDBAlbum    = MDBSonglist[i].album;
        let MDBArtist   = MDBSonglist[i].artist;
        let MDBTags     = MDBSonglist[i].tags;
        let weight      = MDBSonglist[i].weight;
        let topbuttons  = Button_AddSongToQueue(MDBSong.id);
        let bottombuttons;
        bottombuttons   = Button_RelationshipControls(songid, MDBSong.id, MDBSong.name, weight);

        if(i > 0)
            html += "<div class=\"SREntrySeparator\"></div>";

        // Create Artist headline
        if(MDBArtist.id != currentartist)
        {
            html += "<div class=\"MDBSArtistListEntry hlcolor\" onclick=\"ScrollToArtist("+MDBArtist.id+");\" title=\"Scroll to this artist\">";
            html += MDBArtist.name;
            html += "</div>";
            currentartist = MDBArtist.id;
        }

        // Create genre-class list
        let genreclasses = "";
        for(let genre of MDBTags.genres)
            genreclasses += " genre_" + MakeSafeForCSS(genre.name);

        // Create Song entry
        var opacity;
        if(weight < 5)
            opacity = weight / 5;
        else
            opacity = 1.0;

        html += "<div class=\"SRSongListEntry fmcolor " + genreclasses + "\">";
        html += "<div class=\"SRRelevance fmcolor\" style=\"opacity:"+opacity+";\"></div>"
        html += CreateSongTile(MDBSong, MDBAlbum, MDBArtist, topbuttons, bottombuttons, MDBTags);
        html += "</div>";
    }

    html += "</div>";
    
    // Create Element
    $("#"+parentID).html(html);

    // Update song tags
    for(let entry of MDBSonglist)
    {
        let songid = entry.song.id;
        let tags   = entry.tags;
        Taginput_Show("SongTileGenre_"+songid,    "STMGI_"+songid, songid, tags, "Genre",    "Song");
        Taginput_Show("SongTileSubgenre_"+songid, "STSGI_"+songid, songid, tags, "Subgenre", "Song");
    }

    // New elements were created, update there colors with the current style
    UpdateStyle();

    // Request genre-highlight update
    MusicDB_Request("GetMDBState", "UpdateRelationshipGenreHighlight");
}


function UpdateRelationshipTileTags(inputid, MDBTags)
{
    if(inputid.startsWith("STMGI_"))
        Taginput_Update(inputid, MDBTags, "show");
}


function UpdateRelationshipGenreHighlight(MDBState)
{
    // Make all song entries transparent
    $(".SRSongListEntry").css("opacity", "0.2");

    // And now make those visible, that match the album filter
    for(let genrename of MDBState.albumfilter)
    {
        $(".genre_"+MakeSafeForCSS(genrename)).css("opacity", "1.0");
    }
}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

