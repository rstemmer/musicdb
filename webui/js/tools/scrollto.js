
function ScrollTo(id)
{
    var id = "#" + id;

    $(".nano").nanoScroller({ scrollTo: $(id) });

    /* Alternative method
    location.href = "#";    // workaroud for webkit-bug
    location.href = id;
    */
}

function ScrollToArtist(artistid)
{
    var id = "Artist_"+artistid;
    ScrollTo(id);
}

function ScrollToMarker(marker)
{
    var id = marker + "_mark";
    // For some reason nanoscroller does not work in this situation
    location.href = "#";    // workaroud for webkit-bug
    location.href = "#"+id;
}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

