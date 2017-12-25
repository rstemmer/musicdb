
"use strict";

/*
 * This class provides the artistloader.
 * It is possible to select a set of genres and/or to reload the artists-list
 *
 * Requirements:
 *   - JQuery
 *   - tools/hovpacoty.css
 * Show:
 * Functions:
 * Callbacks:
 * Recommended Paths:
 * Trigger: (fnc -> sig)
 *
 */

function ShowMPDControls(parentID)
{
    var html = "";

    html += "<div id=MPDControls>"; // main box
    // Frame
    html += "<div id=MPDCMainFrame class=\"fmcolor frame hovpacity\">";
    
    // Pause/Play
    html += "<div";
    html += " id=MPDCPauseButton";
    html += " title=\"Play/Pause music\"";
    html += " class=\"MPDC_button hlcolor\"";
    html += " onClick=\"MusicDB_Call(\'SetMPDState\', {mpdstate:\'playpause\'});\">";
    html += "Pause/Play";
    html += "</div>";

    // Next
    html += "<div";
    html += " id=MPDCNextButton";
    html += " title=\"Play next song from queue\"";
    html += " class=\"MPDC_button hlcolor\"";
    html += " onClick=\"MusicDB_Call(\'PlayNextSong\');\">";
    html += "Next";
    html += "</div>";

    html += "</div>"; // frame
    html += "</div>"; // main box

    // Create Element
    $("#"+parentID).html(html);
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

