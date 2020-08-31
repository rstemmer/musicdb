/*
 * This class provides the artistloader.
 * It is possible to select a set of genres and/or to reload the artists-list
 *
 * Artistloader_Show creates the UI element,
 * Artistloader_Update creates the genre buttons depending on the tags that the Tagmanager holds in his cache
 *
 * Requirements:
 *   - JQuery
 *   - mdb_artistloader.css
 *   - tools/hovpacoty.css
 * Show:
 *   - ShowArtistloader(parentID);
 *   - UpdateArtistloader(MDBState);
 * Functions:
 * Callbacks:
 * Recommended Paths:
 *   GetMDBState -> UpdateMDBState -> UpdateArtistloader
 * Trigger: (fnc -> sig)
 *   - GetArtistWithAlbums -> ShowArtists
 *
 */

// Gets triggered when the genres were changed.
// on timeout the artist lists will be requested
var RELOAD_INTERVAL      = 1000; //ms
var reloadtimeouthandler = null;

/*
 * This function creates the Artistloader View.
 * The genre buttons were not created. This is done by the Artistloader_Update function.
 * So the View can be created and rendered before the genre tags were loaded.
 *
 * This function can be calls on window.onload event.
 */
function Artistloader_Show(parentID)
{
    var html = "";

    html += "<div id=ALMainBox>"; // main box
    
    // Frame
    html += "<div id=ALMainFrame class=\"fmcolor frame hovpacity\">";

    // Tag-Selector-List
    html += "<div id=ALTaglist>";
    html += "</div>";

    // Controls
    html += "<div id=ALControls>";
    // Reload
    html += "<div";
    html += " title=\"Reload artist list\"";
    html += " id=ArtistControlButton_Reload";
    html += " class=\"AL_controlbutton hlcolor smallfont\"";
    html += " onClick=\"_AL_onToggleControlButton(\'Reload\');\"";
    html += ">";
    html += "Reload";
    html += "</div>";
    html += "</div>";
    
    html += "</div>"; // main frame
    html += "</div>"; // main box

    // Create Element
    $("#"+parentID).html(html);
}


/*
 * This function updates the genre-selection-button list.
 * It loads the current state of genres from the Tagmanager.
 * 
 * When rendering the buttons, only the posx-attribute gets considered.
 * The posy-attribute gets ignored.
 *
 * The genre gets represented by its name, not by the icon.
 *
 * The created button triggers the MusicDB state update as well as the update of the Artists View.
 *
 * This function should be called whenever there are changes regarding the tags.
 */
function Artistloader_UpdateControl()
{
    var genres;
    var html = "";

    // Get all available genre tags
    genres = Tagmanager_GetGenres();
    if(genres == null)
        return;

    // Create a button for each genre
    for(let genre of genres)
        html += _AL_CreateTagButton(genre.name);

    $("#"+"ALTaglist").html(html);
    UpdateStyle(); // Update style of the new created tag-elements (primary their frame color)
}

function Artistloader_UpdateState(MDBState)
{
    // Get selected genres
    var filter;
    filter = MDBState.albumfilter;

    // Get available genres
    var genres;
    genres = Tagmanager_GetGenres();
    if(genres == null)
        return;

    // Update the state of each tag
    for(let genre of genres)
        _AL_SetTagState(genre.name, (filter.indexOf(genre.name) >= 0));
}

function _AL_SetTagState(name, state)
{
    $("#TagButton_"+name).attr("data-checked", state);
}

function _AL_CreateTagButton(tagname)
{
    var html = "";

    html += "<div";
    html += " title=\"Toggle genre\"";
    html += " id=TagButton_" + tagname;
    html += " class=\"AL_tagbutton frame fmcolor hlcolor smallfont\"";
    html += " data-checked=false";
    html += " onClick=\"_AL_onToggleTagButton(\'"+tagname+"\');\"";
    html += ">";
    html += tagname;
    html += "</div>";

    return html;
}

function _AL_onToggleTagButton(tagname)
{
    var buttonid = "#TagButton_" + tagname;
    var state    = $(buttonid).attr("data-checked");
    if(state === "false")
        newstate = true;
    else
        newstate = false;

    // Set new state for responsivenes.
    // This attribute will be updated later by the servers global state.
    // I predict that the global and local value will be the same because I set it!
    $(buttonid).attr("data-checked", newstate);

    // The Call will trigger a broadcast of GetMDBState
    // By making a Request and giving a function signature the boradcast
    // gets handled exactly like a GetMDBState request
    MusicDB_Request("SetMDBState", "UpdateMDBState",
        {category:"albumfilter", name:tagname, value:newstate});

    // Start timer for a Artistlist-Refresh
    if(reloadtimeouthandler !== null)
    {
        clearTimeout(reloadtimeouthandler);
        reloadtimeouthandler = null;
    }
    reloadtimeouthandler = setTimeout("_AL_BroadcastRequestArtistlist()", RELOAD_INTERVAL);
}

function _AL_onToggleControlButton(name)
{
    if(name == "Reload")
    {
        if(reloadtimeouthandler !== null)
        {
            clearTimeout(reloadtimeouthandler);
            reloadtimeouthandler = null;
        }
        _AL_BroadcastRequestArtistlist();
    }
}



function _AL_BroadcastRequestArtistlist(type)
{
    if(mdbmodemanager.GetCurrentMode() == "audio")
    {
        MusicDB_Broadcast("GetFilteredArtistsWithAlbums", "ShowArtists");
        MusicDB_Broadcast("GetSongQueue",                 "ShowSongQueue");
    }
    else if(mdbmodemanager.GetCurrentMode() == "video")
    {
        MusicDB_Broadcast("GetFilteredArtistsWithVideos", "ShowArtists");
        MusicDB_Broadcast("GetVideoQueue",                "ShowVideoQueue");
    }
}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

