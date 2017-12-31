
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
        let  el = document.documentElement,
            rfs = el.requestFullscreen
               || el.webkitRequestFullScreen
               || el.mozRequestFullScreen
               || el.msRequestFullscreen 
            ;

        rfs.call(el);
        $("#FSB").attr("data-fsstate", "fullscreen");
    }
    else
    {
        let  el = window.document,
            rfs = el.exitFullscreen
               || el.webkitExitFullscreen
               || el.mozCancelFullScreen
               || el.msExitFullscreen 
            ;

        rfs.call(el);
        $("#FSB").attr("data-fsstate", "normal");
    }
};


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

