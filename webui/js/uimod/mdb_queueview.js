
"use strict";

/*
 * This class provides the artistloader.
 * It is possible to select a set of genres and/or to reload the artists-list
 *
 * Requirements:
 *   - JQuery
 *   - mdb_queue.css
 *   - mdbstate.js (for timing)
 * Show:
 *   - ShowQueue(parentID)
 * Functions:
 * Callbacks:
 * Recommended Paths:
 * Trigger: (fnc -> sig)
 *
 */

function ShowQueue(parentID, MDBQueue)
{
    let html = "";

    // Reset timer
    if(MDBQueue[0].song !== undefined)
    {
        queuetimemanager.ClearTime("audio");
    }
    else if(MDBQueue[0].video !== undefined)
    {
        queuetimemanager.ClearTime("video");
    }

    html += "<div id=QMainBox>"; // main box
    for(let pos in MDBQueue)
    {
        let entryid     = MDBQueue[pos].entryid;
        let MDBAlbum    = MDBQueue[pos].album;
        let MDBArtist   = MDBQueue[pos].artist;

        let MDBMusic    = null;
        let queuetype   = null;
        if(MDBQueue[pos].song !== undefined)
        {
            MDBMusic  = MDBQueue[pos].song;
            queuetype = "audio"
        }
        else if(MDBQueue[pos].video !== undefined)
        {
            MDBMusic  = MDBQueue[pos].video;
            queuetype = "video"
        }
        else
            continue;   // No song and no video? Should never happen, but who knows…

        // Update timer
        queuetimemanager.AddTime(queuetype, MDBMusic.playtime);
        
        // Create Entry

        let buttonbox = Button_QueueEntryControls(MDBMusic.id, entryid, pos, queuetype);

        html += "<div";
        html += " id=Q_drag_" + pos;
        html += " class=\"Q_entry\"";
        html += " draggable=\"true\"";
        html += " data-pos=\""     + pos         + "\"";
        html += " data-musicid=\"" + MDBMusic.id + "\"";
        html += " data-entryid=\"" + entryid     + "\"";
        html += " data-musictype=\"" + queuetype + "\"";
        html += ">";
        if(queuetype == "audio")
            html += CreateSongTile(MDBMusic, MDBAlbum, MDBArtist, buttonbox)
        else if(queuetype == "video")
            html += CreateVideoTile(MDBMusic, MDBAlbum, MDBArtist, buttonbox)
        html += "</div>";

        html += "<div";
        html += " id=Q_drop_" + pos;
        html += " class=\"Q_separator\"";
        html += " data-entryid=\"" + entryid + "\"";
        html += "></div>";
    }
    
    html += "</div>"; // main box

    // Create Element
    $("#"+parentID).html(html);
    $(".nano").nanoScroller();          // update scrollbars
    UpdateStyle();


    // make all dropentrys useful by adding event handler to them
    let dropelement = ".Q_separator";
    let dragelement = ".Q_entry";

    $(dropelement).on("dragover", function(e){
        e.preventDefault();
        //e.originalEvent.dataTransfer.dropEffect = 'move';
    });
    $(dropelement).on("dragenter", function(e){
        e.preventDefault();
        $(this).addClass("Q_hldropzone");
    });
    $(dropelement).on("dragleave", function(e){
        e.preventDefault();
        $(this).removeClass("Q_hldropzone");
    });
    $(dropelement).on("drop", function(e){
        e.preventDefault();
        $(this).removeClass("Q_hldropzone");

        let attrid    = "#" + e.target.id;
        let dstpos    = $(attrid).attr("data-entryid");
        let srcpos    = e.originalEvent.dataTransfer.getData("srcpos");
        let musicid   = e.originalEvent.dataTransfer.getData("musicid");
        let musictype = e.originalEvent.dataTransfer.getData("musictype");

        if(musictype == "video")
            MusicDB_Call("MoveVideoInQueue", {entryid:srcpos, afterid:dstpos});
        else if(musictype == "audio")
            MusicDB_Call("MoveSongInQueue", {entryid:srcpos, afterid:dstpos});
        else
            window.console && console.log("Unknown music type"+musictype)
    });

    // the entries itself need some DnD-handler too
    $(dragelement).on("dragstart", function(e){
        e.target.style.opacity = "0.5";

        // get data needed for queue-move and set it as dataTransfer
        let attrid = "#" + e.originalEvent.originalTarget.id;

        let entryid   = $(attrid).attr("data-entryid");
        let musicid   = $(attrid).attr("data-musicid");
        let musictype = $(attrid).attr("data-musictype");

        // Set data that will be transferred (mandatory to make DnD work)
        e.originalEvent.dataTransfer.setData("srcpos",    entryid);
        e.originalEvent.dataTransfer.setData("musicid",   musicid);
        e.originalEvent.dataTransfer.setData("musictype", musictype);
    });
    $(dragelement).on("dragend", function(e){
        e.target.style.opacity = "1.0";
    });
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

