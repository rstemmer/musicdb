
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
        var MDBSong     = MDBQueue[pos].song;
        var MDBAlbum    = MDBQueue[pos].album;
        var MDBArtist   = MDBQueue[pos].artist;

        // Update timer
        AddPlaytime(MDBSong.playtime);
        
        // Create Entry

        var buttonbox   = Button_QueueEntryControls(MDBSong.id, pos);

        html += "<div";
        html += " id=Q_drag_" + pos;
        html += " class=\"Q_entry\"";
        html += " draggable=\"true\"";
        html += " data-pos=\"" + pos + "\"";
        html += " data-songid=\""+MDBSong.id+"\"";
        html += ">";
        html += CreateSongTile(MDBSong, MDBAlbum, MDBArtist, buttonbox)
        html += "</div>";

        html += "<div";
        html += " id=Q_drop_" + pos;
        html += " class=\"Q_separator\"";
        html += " data-pos=\"" + pos + "\"";
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

        var entryid = "#" + e.target.id;
        var dstpos  = parseInt( $(entryid).attr("data-pos") );
        var srcpos  = parseInt( e.originalEvent.dataTransfer.getData("srcpos") );
        var songid  = e.originalEvent.dataTransfer.getData("songid");

        // if a song gets move up, it shall be inserted BEHIND the other entry.
        // for example: if song 5 gets moved to position 2 it shall be behing song 2.
        //              so the new id would be 3
        if(dstpos < srcpos)
            dstpos += 1;

        MusicDB_Call("MoveSongInQueue", {songid:songid, srcpos:srcpos, dstpos:dstpos});
    });

    // the entries itself need some DnD-handler too
    $(dragelement).on("dragstart", function(e){
        e.target.style.opacity = "0.5";

        // get data needed vor queue-move and set it as dataTransfer
        var entryid = "#" + e.originalEvent.originalTarget.id;

        var position = $(entryid).attr("data-pos");
        var songid   = $(entryid).attr("data-songid");

        // Set data that will be transfared (mandatory to make DnD work)
        e.originalEvent.dataTransfer.setData("srcpos", position);
        e.originalEvent.dataTransfer.setData("songid", songid);
    });
    $(dragelement).on("dragend", function(e){
        e.target.style.opacity = "1.0";
    });
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

