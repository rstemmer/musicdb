
"use strict";

var lastbgcolor = "#181819";
var lastfgcolor = "#CCCCCC";
var lasthlcolor = "#777799";

// If no arguments, default values (last color setup) will be used
function UpdateStyle(bgcolor, fgcolor, hlcolor)
{
    lastbgcolor = bgcolor || lastbgcolor;
    lastfgcolor = fgcolor || lastfgcolor;
    lasthlcolor = hlcolor || lasthlcolor;

    document.documentElement.style.setProperty("--fgcolor", lastfgcolor);
    document.documentElement.style.setProperty("--bgcolor", lastbgcolor);
    document.documentElement.style.setProperty("--hlcolor", lasthlcolor);
    document.documentElement.style.setProperty("--fmcolor", lasthlcolor);
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

