
"use strict";

/*
 *
 * Requirements:
 *   - JQuery
 *   - queuecontrol.css
 *   - tools/hovpacoty.css
 * Show:
 * Functions:
 * Callbacks:
 * Recommended Paths:
 * Trigger: (fnc -> sig)
 *
 */

function ShowQueueControls(parentID)
{
    var html = "";

    html += "<div id=QueueControls>"; // main box
    // Frame
    html += "<div id=QCMainFrame class=\"hovpacity hlcolor\">";
    
    html += Button_AddRandomSongToQueue();

    html += "</div>"; // frame
    html += "</div>"; // main box

    // Create Element
    $("#"+parentID).html(html);
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

