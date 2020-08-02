
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
    ClearPlaytime();

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
        AddPlaytime(MDBMusic.playtime);
        
        // Create Entry

        let buttonbox = Button_QueueEntryControls(MDBMusic.id, entryid, pos, queuetype);

        html += "<div";
        html += " id=Q_drag_" + pos;
        html += " class=\"Q_entry\"";
        html += " draggable=\"true\"";
        html += " data-pos=\""     + pos        + "\"";
        html += " data-songid=\""  + MDBMusic.id + "\"";
        html += " data-entryid=\"" + entryid    + "\"";
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

        let attrid = "#" + e.target.id;
        let dstpos  = $(attrid).attr("data-entryid");
        let srcpos  = e.originalEvent.dataTransfer.getData("srcpos");
        let videoid = e.originalEvent.dataTransfer.getData("videoid");

        MusicDB_Call("MoveVideoInQueue", {entryid:srcpos, afterid:dstpos});
    });

    // the entries itself need some DnD-handler too
    $(dragelement).on("dragstart", function(e){
        e.target.style.opacity = "0.5";

        // get data needed for queue-move and set it as dataTransfer
        let attrid = "#" + e.originalEvent.originalTarget.id;

        let entryid = $(attrid).attr("data-entryid");
        let videoid = $(attrid).attr("data-videoid");

        // Set data that will be transferred (mandatory to make DnD work)
        e.originalEvent.dataTransfer.setData("srcpos", entryid);
        e.originalEvent.dataTransfer.setData("videoid", videoid);
    });
    $(dragelement).on("dragend", function(e){
        e.target.style.opacity = "1.0";
    });
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

