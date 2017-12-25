
"use strict";

/*
 * This class provides the artistloader.
 *
 * Requirements:
 *   - JQuery
 * Show:
 * Functions:
 * Callbacks:
 * Recommended Paths:
 * Trigger: (fnc -> sig)
 *
 */

function ShowFullscreenButton()
{
    var html = "";

    html += "<div id=FSBBox>"; // main box
    
    // Pause/Play
    html += "<div";
    html += " id=FSB";
    html += " title=\"Toggle fullscreen mode\"";
    html += " class=\"hlcolor hovpacity\"";
    html += " data-fsstate=\"normal\""; // {normal, fullscreen}
    html += " onClick=\"ToggleFullscreen();\">";
    html += "</div>";

    html += "</div>"; // main box

    // Create Element
    //$("#"+parentID).html(html);
    $("body").append(html);
}

function ToggleFullscreen()
{
    var state = $("#FSB").attr("data-fsstate");

    if(state == "normal")
    {
        document.documentElement.mozRequestFullScreen();
        $("#FSB").attr("data-fsstate", "fullscreen");
    }
    else
    {
        document.mozCancelFullScreen();
        $("#FSB").attr("data-fsstate", "normal");
    }
};


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

