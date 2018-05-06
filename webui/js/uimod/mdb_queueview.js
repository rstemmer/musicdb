
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
    var html = "";

    // Reset timer
    ClearPlaytime();

    html += "<div id=QMainBox>"; // main box
    for(var pos in MDBQueue)
    {
        var entryid     = MDBQueue[pos].entryid;
        var MDBSong     = MDBQueue[pos].song;
        var MDBAlbum    = MDBQueue[pos].album;
        var MDBArtist   = MDBQueue[pos].artist;

        // Update timer
        AddPlaytime(MDBSong.playtime);
        
        // Create Entry

        var buttonbox   = Button_QueueEntryControls(MDBSong.id, entryid, pos);

        html += "<div";
        html += " id=Q_drag_" + pos;
        html += " class=\"Q_entry\"";
        html += " draggable=\"true\"";
        html += " data-pos=\""     + pos        + "\"";
        html += " data-songid=\""  + MDBSong.id + "\"";
        html += " data-entryid=\"" + entryid    + "\"";
        html += ">";
        html += CreateSongTile(MDBSong, MDBAlbum, MDBArtist, buttonbox)
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


    // make all dropentrys usefull by adding event handler to them
    var dropelement = ".Q_separator";
    var dragelement = ".Q_entry";

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

        var attrid = "#" + e.target.id;
        var dstpos  = $(attrid).attr("data-entryid");
        var srcpos  = e.originalEvent.dataTransfer.getData("srcpos");
        var songid  = e.originalEvent.dataTransfer.getData("songid");

        MusicDB_Call("MoveSongInQueue", {entryid:srcpos, afterid:dstpos});
    });

    // the entries itself need some DnD-handler too
    $(dragelement).on("dragstart", function(e){
        e.target.style.opacity = "0.5";

        // get data needed vor queue-move and set it as dataTransfer
        var attrid = "#" + e.originalEvent.originalTarget.id;

        var entryid = $(attrid).attr("data-entryid");
        var songid  = $(attrid).attr("data-songid");

        // Set data that will be transferred (mandatory to make DnD work)
        e.originalEvent.dataTransfer.setData("srcpos", entryid);
        e.originalEvent.dataTransfer.setData("songid", songid);
    });
    $(dragelement).on("dragend", function(e){
        e.target.style.opacity = "1.0";
    });
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

