
"use strict";

var lastbgcolor = "#181819";
var lastfgcolor = "#CCCCCC";
var lasthlcolor = "#777799";

// If no arguments, default values (last color setup) will be used
function UpdateStyle(bgcolor, fgcolor, hlcolor)
{
    // Old concept
    lastbgcolor = bgcolor || lastbgcolor;
    lastfgcolor = fgcolor || lastfgcolor;
    lasthlcolor = hlcolor || lasthlcolor;
    $(".bgcolor").css("background-color", lastbgcolor);
    $(".fgcolor").css("color",            lastfgcolor);
    $(".hlcolor").css("color",            lasthlcolor);
    $(".fmcolor").css("border-color",     lasthlcolor);

    // New concept
    //let styles = window.getComputedStyle(document.documentElement);
    /*
    styles.setProperty('--fgcolor', lastfgcolor);
    styles.setProperty('--hlcolor', lasthlcolor);
    styles.setProperty('--bgcolor', lastbgcolor);
    */
}

function GetHLColor()
{
    return lasthlcolor;
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

