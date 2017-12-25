
var SONGID = -1;    // context of all action is this song

function onMusicDBConnectionOpen()
{
    window.console && console.log("[MDB] Open");

    function getParameterByName(name) 
    {
        url       = window.location.href;
        name      = name.replace(/[\[\]]/g, "\\$&");
        var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
        results   = regex.exec(url);
        if (!results)       return null;
        if (!results[2])    return '';
        return decodeURIComponent(results[2].replace(/\+/g, " "));
    }

    var songid;
    songid = getParameterByName("songid");
    if(songid)
    {
        SONGID = songid;
        MusicDB_Request("GetSongLyrics", "ShowLyrics", {songid: songid});
    }

}
function onMusicDBConnectionError()
{
    window.console && console.log("[MDB] Error");
}
function onMusicDBWatchdogBarks()
{
    window.console && console.log("[MDB] WD Barks");
}
function onMusicDBConnectionClosed()
{
    window.console && console.log("[MDB] Closed");
}

function onMusicDBNotification(fnc, sig, rawdata)
{
}
function onMusicDBMessage(fnc, sig, args, pass)
{

    // Handle Messages form the server
    if(sig == "ShowLyrics") 
        ShowLyrics(args.songid, args.lyricsstate, args.lyrics);
    else if(sig == "ShowCrawlerCache") 
        ShowCrawlerCache(args.songid, args.lyricscache);
}


window.onload = function ()
{
    var cogs;
    cogs = "<i class=\"fa fa-cog fa-spin fa-fw\"></i>";
    $("#LyricsTab").html(cogs);

    ConnectToMusicDB();
}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

