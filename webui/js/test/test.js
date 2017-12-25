

function onMusicDBConnectionOpen()
{
    window.console && console.log("[MDB] Open");

    MusicDB_Request("GetTags", "UpdateTagsCache");
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
    console.log(">> fnc: "+fnc+"; sig: "+sig);
    if(fnc == "GetTags")
    {
        Tagmanager_onGetTags(args);
        MusicDB_Request("GetSong",  "ShowSong",  {songid:2137});
        MusicDB_Request("GetAlbum", "ShowAlbum", {albumid:174});
    }
    else if(fnc == "GetSong" && sig == "ShowSong")
    {
        let html = "";
        console.log(" !! Working on "+args.song.path+" !! ");
        
        html = Taginput_Create("moodinputid", args.song.id, "Mood", "Song");
        $("#MainViewContent1").html(html);
        Taginput_Update("moodinputid", args.tags);

        html = Taginput_Create("subgenreinputid", args.song.id, "Subgenre", "Song");
        $("#MainViewContent2").html(html);
        Taginput_Update("subgenreinputid", args.tags);

        html = Taginput_Create("genreinputid", args.song.id, "Genre", "Song");
        $("#MainViewContent3").html(html);
        Taginput_Update("genreinputid", args.tags);
    }
    else if(sig == "UpdateTagInput")
    {
        console.log("Updateing "+pass.taginputid);
        Taginput_Update(pass.taginputid, args.tags);
    }
    else if(fnc == "GetAlbum" && sig == "ShowAlbum")
    {
        let html = "";
        console.log(" !! Working on "+args.album.path+" !! ");

        html = Taginput_Create("albumsubgenreinputid", args.album.id, "Subgenre", "Album");
        $("#MainViewContent4").html(html);
        Taginput_Update("albumsubgenreinputid", args.tags);

        html = Taginput_Create("albumgenreinputid", args.album.id, "Genre", "Album");
        $("#MainViewContent5").html(html);
        Taginput_Update("albumgenreinputid", args.tags);
    }
}


window.onload = function ()
{
    var cogs;
    cogs = "<i class=\"fa fa-cog fa-spin fa-fw\"></i>";
    $("#MainViewContent1").html(cogs);
    $("#MainViewContent2").html(cogs);
    $("#MainViewContent3").html(cogs);
    $("#MainViewContent4").html(cogs);
    $("#MainViewContent5").html(cogs);
    ConnectToMusicDB();

}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

