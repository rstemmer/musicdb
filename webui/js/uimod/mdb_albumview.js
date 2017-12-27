
"use strict";

/*
 * This class shows an album and its songs
 *
 * Requirements:
 *   - JQuery
 *   - mdb_albumview.css
 *   - scrollto.js
 *   - lyrics
 * Show:
 *   - ShowAlbum(parentID, MDBArgs);
 * Functions:
 * Callbacks:
 * Recommended Paths:
 * Trigger: (fnc -> sig)
 */

// the current song id is used to highlight the currently playing song
function ShowAlbum(parentID, MDBArtist, MDBAlbum, MDBCDs, MDBAlbumTags, currentsongid)
{
    var html = "";

    html += "<div id=AlbumViewBox>"; // main box

    html += "<div id=ABVMetaBox>";
    // Cover
    html += _ABV_CreateCover(MDBAlbum);
    // Tags
    html += "<div id=\"AlbumGenreBox\" class=\"hlcolor smallfont\">";
    html += "   <div id=\"AlbumGenre\" class=\"hlcolor\"></div>";
    html += "   <div id=\"AlbumSubgenre\" class=\"hlcolor\"></div>";
    html += "</div>";
    html += "</div>";

    // Add-Button
    html += "<div id=ABVToolbar class=\"hlcolor hovpacity\" title=\"Add whole album to queue\">";
    html += Button_AddAlbumToQueue(MDBAlbum.id);
    html += "</div>";

    // Album title and artist infos
    html += _ABV_CreateHeadline(MDBArtist, MDBAlbum);

    // Hidden settings
    html += _ABV_CreateSettings(MDBAlbum, MDBAlbumTags);

    html += "<div id=ABVSongs>";
    for(var i in MDBCDs)
    {
        var MDBSongList = MDBCDs[i];

        html += "<div class=\"ABV_cd\">";

        // If there are more than one CD, output the numbor of the current one
        if(MDBCDs.length > 1)
        {
            html += "<span class=\"ABV_cdnum hlcolor smallfont\">CD " + (parseInt(i)+1) + "</span>";
        }


        html += "<div class=\"ABV_songlist\">";
        for(let songindex in MDBSongList)
        {
            var MDBSong     = MDBSongList[songindex].song;
            var MDBSongTags = MDBSongList[songindex].tags;
            html += _ABV_CreateSongEntry(MDBSong, MDBSongTags);
        }
        html += "</div>";

        html += "</div>";
    }
    html += "</div>";

    html += "</div>"; // main box

    // Create Element
    $("#"+parentID).html(html);
    $("#ABVPS_"+currentsongid).attr("data-playing", "yes");

    // Update all settings to the current state
    for(let CD of MDBCDs)
    {
        for(let track of CD)
        {
            var MDBSong     = track.song;
            var MDBSongTags = track.tags;
            _ABV_UpdateSongSettings(MDBSong, MDBSongTags);
        }
    }

    // Update album settings to the current state
    Taginput_Update("ABV_albumgenre_"    + MDBAlbum.id, MDBAlbumTags);
    Taginput_Update("ABV_albumsubgenre_" + MDBAlbum.id, MDBAlbumTags);
    Taginput_Show("AlbumGenre",    "AlbumGenreView",    MDBAlbum.id, MDBAlbumTags, "Genre", "Album");
    Taginput_Show("AlbumSubgenre", "AlbumSubgenreView", MDBAlbum.id, MDBAlbumTags, "Subgenre", "Album");

    // Final updates
    $(".nano").nanoScroller();          // update scrollbars
    UpdateStyle(MDBAlbum.bgcolor, MDBAlbum.fgcolor, MDBAlbum.hlcolor);
}


function _ABV_CreateCover(MDBAlbum)
{
    var html = "";
    html += "<div id=ABVArtworkBox>";
    var imgpath = EncodeArtworkPath(MDBAlbum.artworkpath);
    html += "<img id=ABVArtworkImage src=\"" + imgpath + "\">";
    html += "</div>";
    return html;
}

function _ABV_CreateSettings(MDBAlbum, MDBAlbumtags)
{
    var albumid = MDBAlbum.id;
    var html = "";
    var bgcolor = MDBAlbum.bgcolor || "#000000";
    var hlcolor = MDBAlbum.hlcolor || "#000000";    
    var fgcolor = MDBAlbum.fgcolor || "#000000";
    html += "<div id=ABVSettingsBox>";

    html += "<div id=ABVSettings>";

    html += Taginput_Create("ABV_albumgenre_"    + albumid, albumid, "Genre",    "Album");
    html += Taginput_Create("ABV_albumsubgenre_" + albumid, albumid, "Subgenre", "Album");

    html += "<div class=\"ABVColorSettingsBox hlcolor fmcolor\">";

    html += "<div class=\"ABVColorSettingsRow\">";
    html += "<span class=\"ABVSettingName\">Background:</span>";
    html += CreateColorInput("CI_BGColor", bgcolor, 
        "_ABV_onColorSave("+MDBAlbum.id+", \'CI_BGColor\');",
        _ABV_onColorChange
        );
    html += "</div>";
    
    html += "<div class=\"ABVColorSettingsRow\">";
    html += "<span class=\"ABVSettingName\">Foreground:</span>";
    html += CreateColorInput("CI_FGColor", fgcolor, 
        "_ABV_onColorSave("+MDBAlbum.id+", \'CI_FGColor\');",
        _ABV_onColorChange
        );
    html += "</div>";
    
    html += "<div class=\"ABVColorSettingsRow\">";
    html += "<span class=\"ABVSettingName\">Highlight:</span>";
    html += CreateColorInput("CI_HLColor", hlcolor, 
        "_ABV_onColorSave("+MDBAlbum.id+", \'CI_HLColor\');",
        _ABV_onColorChange
        );
    html += "</div>";
    
    html += "</div>";

    html += "</div>";

    html += "</div>";

    return html;
}

function _ABV_onColorChange(elementid, color)
{
    if(elementid == "CI_BGColor")
    {
        $(".bgcolor").css("background-color", color);
    }
    else if(elementid == "CI_FGColor")
    {
        $(".fgcolor").css("color", color);
    }
    else if(elementid == "CI_HLColor")
    {
        $(".hlcolor").css("color", color);
        $(".fmcolor").css("border-color", color);
    }
}

function _ABV_onColorSave(albumid, elementid)
{
    var color = $("#"+elementid).val();

    // Do not send bullshit even if the server could handle it
    if(color == "#NANNANNAN")
        return;
    if(color == null || color == "null")
        return;

    // this is the NULL-Color. It would be so fucking bad designe-style that I will never use it
    if(color == "#000000")
        return;

    var colorname = "";
    if(elementid == "CI_BGColor")
        colorname = "bgcolor";
    else if(elementid == "CI_FGColor")
        colorname = "fgcolor";
    else if(elementid == "CI_HLColor")
        colorname = "hlcolor";
    else
        return;

    MusicDB_Call("SetAlbumColor", {albumid:albumid, colorname:colorname, color:color});
}

function _ABV_CreateHeadline(MDBArtist, MDBAlbum)
{
    var html = "";
    html += "<div id=ABVHeadlineBox title=\"Origin: " + MDBAlbum.origin + "\"";
    html += " oncontextmenu=\"ToggleVisibility(\'ABVSettings\'); return false;\""; // Show settings
    html += ">";

    html += "<div id=ABVMainHeadline>";
    // Albumname
    html += "<span ";
    html += " id=ABVAlbumName";
    html += " class=\"fgcolor\">";
    html += MDBAlbum.name.replace(" - ", " – ");
    html += "</span>";

    html += "</div>";
    html += "<div id=ABVSubHeadline class=\"smallfont\">";
    // Artistname
    html += "<span ";
    html += " onClick=\"ScrollToArtist(" + MDBArtist.id + ");\"";
    html += " id=ABVArtistName";
    html += " class=\"hlcolor\">";
    html += MDBArtist.name.replace(" - ", " – ");
    html += "</span>";

    html += "<span id=ABVSHLSeparator class=\"fgcolor\"> – </span>";
    
    // Albumrelease
    html += "<span ";
    html += " id=ABVAlbumRelease";
    html += " class=\"hlcolor\">";
    html += MDBAlbum.release;
    html += "</span>";

    html += "</div>";
    html += "</div>";
    return html;
}

function _ABV_CreateSongEntry(MDBSong, MDBSongTags)
{
    var html = "";
    //window.console && console.log(MDBSong);

    var settingsid = "ABV_songsettings_" + MDBSong.id;
    html += "<div";
    html += " class=\"ABV_songentry fmcolor\"";
    html += " oncontextmenu=\"ToggleVisibility(\'" + settingsid + "\'); return false;\""
    html += ">";

    html += _ABV_CreateSongEntryNumber(MDBSong.number);
    html += _ABV_CreateSongEntryName(MDBSong.name, MDBSong.id, MDBSong.disabled);
    html += _ABV_CreateSongEntryTags(MDBSongTags);
    html += _ABV_CreateSongEntryButtonbox(MDBSong);
    html += _ABV_CreateSongEntryLikeGraph(MDBSong);

    html += "</div>";

    html += "<div id=\"" + settingsid + "\" class=\"ABV_songsettings fmcolor frame\">";
    html += "<div class=\"ABV_songsettings_row\">";
    html += _ABV_CreateSongSettings(MDBSong, MDBSongTags);
    html += "</div>";
    html += "<div class=\"ABV_songsettings_row\">";
    html += "   <div class=\"ABVS_playerbox\">";
    html += "   <audio controls preload=none class=\"ABVS_player hovpacity\">";
    html += "   <source src=\"/musicdb/music/"+MDBSong.path+"\">";
    html += "   </audio>";
    html += "   </div>";
    html += "</div>";
    html += "</div>";

    return html;
}

function _ABV_CreateSongSettings(MDBSong, MDBSongTags)
{
    var songid = MDBSong.id;
    var html = "";
    var moodboxid = "ABVS_moodbox_" + songid;
    var propboxid = "ABVS_propbox_" + songid;
    var tagsboxid = "ABVS_tagsbox_" + songid;

    html += "<div id=\""+moodboxid+"\" class=\"ABVS_moodbox hlcolor\">"
    html += "</div>";
    html += "<div id=\""+propboxid+"\" class=\"ABVS_propbox hlcolor\">";
    html += "</div>";
    html += "<div id=\""+tagsboxid+"\" class=\"ABVS_tagsbox\">";
    html += Taginput_Create("ABVS_genre_"    + songid, songid, "Genre",    "Song");
    html += Taginput_Create("ABVS_subgenre_" + songid, songid, "Subgenre", "Song");
    html += "</div>";

    return html;
}
// For internal use only! - For extern, use Albumview_UpdateSong
function _ABV_UpdateSongSettings(MDBSong, MDBSongTags)
{
    var songid = MDBSong.id;
    var moodboxid = "ABVS_moodbox_" + songid;
    var propboxid = "ABVS_propbox_" + songid;
    var tagsboxid = "ABVS_tagsbox_" + songid;
    Songtags_ShowMoodControl(moodboxid, moodboxid);
    Songtags_UpdateMoodControl(moodboxid, MDBSongTags);
    
    Songproperties_ShowControl(propboxid, propboxid);
    Songproperties_UpdateControl(propboxid, MDBSong, true); // true: initialize and reset like/dislike buttons

    Taginput_Update("ABVS_genre_"    + songid, MDBSongTags);
    Taginput_Update("ABVS_subgenre_" + songid, MDBSongTags);
}


function Albumview_UpdateAlbum(MDBAlbum, MDBAlbumTags)
{
    Taginput_Show("AlbumGenre",    "AlbumGenreView",    MDBAlbum.id, MDBAlbumTags, "Genre", "Album");
    Taginput_Show("AlbumSubgenre", "AlbumSubgenreView", MDBAlbum.id, MDBAlbumTags, "Subgenre", "Album");
    Taginput_Update("ABV_albumgenre_"    + MDBAlbum.id, MDBAlbumTags);
    Taginput_Update("ABV_albumsubgenre_" + MDBAlbum.id, MDBAlbumTags);
}

/*
 *
 */
function Albumview_UpdateSong(MDBAlbum, MDBSong, MDBSongTags)
{
    var songid      = MDBSong.id;
    var moodboxid   = "ABVS_moodbox_"  + songid;
    var propboxid   = "ABVS_propbox_"  + songid;
    var tagboxid    = "ABV_tagbox_"    + songid;
    var buttonboxid = "ABV_buttonbox_" + songid;

    // Check if the song does exist in the Albumview
    if($("#"+buttonboxid).length === 0)
        return;

    // Update Song Entry
    var tagbox, buttonbox;
    tagbox    = _ABV_CreateSongEntryTags(MDBSongTags);
    $("#"+tagboxid).replaceWith(tagbox);
    buttonbox = _ABV_CreateSongEntryButtonbox(MDBSong);
    $("#"+buttonboxid).replaceWith(buttonbox);

    // Update Settings
    Songtags_UpdateMoodControl(moodboxid, MDBSongTags);
    Songproperties_UpdateControl(propboxid, MDBSong, false);
    Taginput_Update("ABVS_genre_"    + songid, MDBSongTags);
    Taginput_Update("ABVS_subgenre_" + songid, MDBSongTags);

    // Update Style
    UpdateStyle(MDBAlbum.bgcolor, MDBAlbum.fgcolor, MDBAlbum.hlcolor);
}

function _ABV_CreateSongEntryNumber(songnumber)
{
    if(songnumber != 0)
        return "<span class=\"ABV_songnumber hlcolor\">"+songnumber+"</span>";
    else
        return "<span class=\"ABV_songnumber hlcolor\">⚪&#x0000FE0E;</span>";
}
function _ABV_CreateSongEntryName(songname, songid, disabled)
{
    var color = "";
    if(disabled)
        color = "hlcolor";
    else
        color = "fgcolor"; 

    var html = "";
    html += "<span id=ABVPS_"+songid+" class=\"ABV_songplaystate hlcolor\" data-playing=\"no\"></span>";
    html += "<span class=\"ABV_songname "+color+"\" title=\""+songname+"\">"+songname+"</span>";
    return html;
}
    
function _ABV_CreateSongEntryTags(MDBSongTags)
{
    var html = "";
    var boxid= "ABV_tagbox_" + MDBSongTags.songid;
    html += "<div id=\"" + boxid + "\" class=\"ABV_tagbox hlcolor\">";

    // Create a list of tags that are set
    var taglist = [];
    for(let tag of MDBSongTags.moods)
        taglist.push(tag.id);

    // Get all possible moods
    var moods;
    moods = Tagmanager_GetMoods();

    // Create icon-set
    for(let mood of moods)
    {
        if(taglist.indexOf(mood.id) >= 0 && mood.icon != null)
        {
            html += _ABV_CreateFlag(mood.name, mood.icon + "&#x0000FE0E;", mood.color);
        }
    }

    html += "</div>";
    return html;
}

function _ABV_CreateSongEntryButtonbox(MDBSong)
{
    var html = "";
    var boxid= "ABV_buttonbox_" + MDBSong.id;
    html += "<div id=\"" + boxid + "\" class=\"ABV_buttonbox hlcolor\">";

    if(MDBSong.favorite > 0)
        html += _ABV_CreateFlag("favorite", "<i class=\"fa fa-diamond\"></i>", "#A8A623");

    // Lyrics-button
    html += Button_Lyrics(MDBSong.lyricsstate,
        "_ABV_ShowLyrics(" + MDBSong.id + ", " + MDBSong.albumid + ");");
    
    if(MDBSong.favorite < 0 || MDBSong.disabled)
        html += "<span style=\"opacity:0.5\">";
    html += Button_AddSongToQueue(MDBSong.id);
    if(MDBSong.favorite < 0 || MDBSong.disabled)
        html += "</span>";
    
    html += "</div>";
    return html;
}
function _ABV_CreateFlag(name, icon, color)
{
    var html = "";
    var classname = "ABV_songflag_"+name;
    html += "<div class=\"ABV_songflag "+classname+" smallfont\"";
    if(color != null)
        html += " style=\"color:" + color + "\"";
    html += ">";
    html += icon;
    html += "</div>";
    return html;
}

function _ABV_CreateSongEntryLikeGraph(MDBSong)
{
    var html = "";

    // parameters
    var l       = MDBSong.likes;
    var d       = MDBSong.dislikes;
    var fav     = MDBSong.favorite
    var adds    = MDBSong.qadds;
    var radds   = MDBSong.qrndadds;
    var removes = MDBSong.qremoves;
    var skips   = MDBSong.qskips;
    
    // Make tooltip including some stats
    var tooltip = "";
    tooltip += l + " / " + d;

    // Calculation
    var h_l,h_d,h_max;
    h_max = 16;

    html += "<div class=\"ABV_likegraphbox hlcolor\" title=\"" + tooltip + "\">";

    // Numbers
    html += "<div class=\"ABV_likevaluebox hlcolor\">";
    html += "<div class=\"ABV_likevalue    tinyfont\">"+l+"</div>";
    html += "<div class=\"ABV_dislikevalue tinyfont\">"+d+"</div>";
    html += "</div>";

    // Graph
    if(l+d > 0)
    {
        h_l = Math.round((l/(l+d)) * h_max);
        h_d = h_max - h_l;

        html += "<div class=\"ABV_likegraph\">";
        html += "<div class=\"ABV_likebar\"    style=\"height: " + h_l + "px;\"></div>";
        html += "<div class=\"ABV_dislikebar\" style=\"height: " + h_d + "px;\"></div>";
        html += "</div>";
    }
    else
    {
        html += "<div class=\"ABV_likegraph\">";
        html += "<div class=\"ABV_unratedbar\" style=\"height: "+h_max+"px;\"></div>";
        html += "</div>";
    }

    html += "</div>";
    return html;
}


function _ABV_ShowLyrics(songid, albumid)
{
    // Replace songlist by lyrics meta-box
    ShowLyricsMetaBox("ABVSongs", songid, albumid);
    // Request lyrics
    MusicDB_Request("GetSongLyrics", "ShowLyrics", 
        {songid: songid}, 
        {parentid:"LMBLyrics", mode:"view"});
}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

