
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

function ShowSearchInput(parentID)
{
    var html = "";

    html += "<div id=MDBSearchBox>";
    html += "<div class=\"MDBSInnerBox hovpacity\">";

    // result popup
    html += "<div id=MDBSResultPopup class=\"bgcolor frame fmcolor\"></div>";

    // search element
    html += "<div class=\"MDBSFrame hlcolor\">";

    html += "<div class=\"MDBSIconBoxLeft\">";
    html += "<i class=\"fa fa-search\"></i>";
    html += "</div>";
    
    html += "<div class=\"MDBSInputBox\">";
    html += "<input";
    html += " class=\"MDBSInput hlcolor\"";
    html += " type=\"search\"";
    html += " onInput=\"_MDBS_onInput(event, this);\"";
    html += " onKeyup=\"_MDBS_onKeyup(event, this);\"";
    html += " onClick=\"_MDBS_onClick(event, this);\"";
    html += " placeholder=\"Search…\">";
    html += "</div>";

    html += "<div";
    html += " class=\"MDBSIconBoxRight\"";
    html += " title=\"Clear input and close preview\"";
    html += " onClick=\"_MDBS_onDelete(event, this);\">";
    html += "<i class=\"fa fa-times-circle\"></i>";
    html += "</div>";

    html += "</div>";

    html += "</div>";
    html += "</div>";
    
    // Create Element
    $("#"+parentID).html(html);
}


var _MDBS_FindTimeoutInterval   = 500;  /*ms (old: 200)*/
var _MDBS_FindTimeoutHandler    = null;
var _MDBS_ResultViewState       = "no";  /*{"no", "preview", "full"}*/

function MDBS_Find(searchstring)
{
    var limit;  // limit of search results
    if(_MDBS_ResultViewState == "preview")
        limit = 5;
    else if(_MDBS_ResultViewState == "full")
        limit = 20;
    else
        return;

    MusicDB_Request("Find", "ShowSearchResults", {searchstring:searchstring, limit:limit});
}


function _MDBS_onInput(event, element)
{
    var value   = element.value;
    var length  = element.value.length;
    if(length > 0)
    {
        // We have a searchstring, so at least preview the results
        if(_MDBS_ResultViewState == "no")
            _MDBS_ResultViewState = "preview";

        // In FindTimeoutInterval millisecound the MDBS_Find function shall trigger
        // a search searching for value
        if(_MDBS_FindTimeoutHandler)
            clearTimeout(_MDBS_FindTimeoutHandler);
        _MDBS_FindTimeoutHandler = setTimeout(MDBS_Find, _MDBS_FindTimeoutInterval, value);
    }
    else
    {
        // No search string, no results
        _MDBS_ResultViewState = "no";
        _MDBS_HideResultPopup();
    }
}

function _MDBS_onKeyup(event, element)
{
    var keycode = event.which || event.keyCode;
    var value   = element.value;
    var length  = element.value.length;
    
    if(keycode == 13 && length > 0)   // ENTER
    {
        // Show full results
        _MDBS_HideResultPopup();
        _MDBS_ResultViewState = "full";

        // And show them now
        if(_MDBS_FindTimeoutHandler)
            clearTimeout(_MDBS_FindTimeoutHandler);
        MDBS_Find(value);
    }
    else if(keycode == 27)  // ESC
    {
        _MDBS_HideResultPopup();
    }
}

function _MDBS_onClick(event, element)
{
    var value   = element.value;
    var length  = element.value.length;
    if(length > 0)
    {
        // We have a searchstring, so at least preview the results
        if(_MDBS_ResultViewState == "no")
            _MDBS_ResultViewState = "preview";

        // Show the last results
        if(_MDBS_ResultViewState == "preview")
            $("#MDBSResultPopup").css("display", "block");
    }
}

function _MDBS_onDelete(event, element)
{
    $("input.MDBSInput").val("");
    _MDBS_HideResultPopup();
}


function _MDBS_HideResultPopup()
{
    $("#MDBSResultPopup").css("display", "none");

    // don't be full anymore. Next time it shall only be a preview
    if(_MDBS_ResultViewState == "full")
        _MDBS_ResultViewState = "preview";
}

function ShowSearchResults(artists, albums, songs)
{
    var html = "";

    // Artists
    html += "<div class=\"MDBSResultList MDBSArtistList\">";
    for(var i in artists)
    {
        var entry       = artists[i];
        var MDBArtist   = entry.artist;
        var artistname  = MDBArtist.name.replace(" - ", " – ");
        var artistid    = MDBArtist.id;
        var onclick     = "ScrollToArtist(" + artistid + "); _MDBS_HideResultPopup();";
        html += "<div class=\"MDBSArtistListEntry\" onClick=\"" + onclick + "\" title=\"Scroll to this artist\">";
        html += artistname;
        html += "</div>";
    }
    html += "</div>";

    // Albums
    html += "<div class=\"MDBSResultList MDBSAlbumList\">";
    for(var i in albums)
    {
        var entry       = albums[i];
        var MDBAlbum    = entry.album;
        html += "<div class=\"MDBSAlbumListEntry\" onClick=\"_MDBS_HideResultPopup();\" title=\"Show this album\">";
        if(_MDBS_ResultViewState == "preview")
            html += CreateSmallAlbumTile(MDBAlbum);
        else
            html += CreateAlbumTile(MDBAlbum);
        html += "</div>";
    }
    html += "</div>";
    
    // Songs
    html += "<div class=\"MDBSResultList MDBSSongList\">";
    for(var i in songs)
    {
        if(i > 0)
            html += "<div class=\"MDBSEntrySeparator\"></div>";

        var entry       = songs[i];
        var MDBArtist   = entry.artist;
        var MDBAlbum    = entry.album;
        var MDBSong     = entry.song;
        var buttons     = Button_AddSongToQueue(MDBSong.id);

        html += "<div class=\"MDBSSongListEntry fmcolor\" onClick=\"_MDBS_HideResultPopup();\">";
        html += CreateSongTile(MDBSong, MDBAlbum, MDBArtist, buttons);
        html += "</div>";
    }
    html += "</div>";

    if(_MDBS_ResultViewState == "preview")
    {
        $("#MDBSResultPopup").html(html);
        $("#MDBSResultPopup").css("display", "block");
    }
    else if(_MDBS_ResultViewState == "full")
    {
        html = "<div id=MDBSResultView class=\"fmcolor\">" + html + "</div>";
        $("#MiddleContentBox").html(html);
    }

    // New elements were created, update there colors with the current style
    UpdateStyle();
}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

