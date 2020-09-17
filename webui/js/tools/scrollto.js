

function ScrollToArtist(artistid)
{
    window.console && console.log("Deprecated! Use artistsview.ScrollToArtist");
    let element = document.getElementById("Artist_" + artistid);
    element.scrollIntoView({behavior: "smooth"});
    return;
}

function ScrollToMarker(marker)
{
    let id      = marker + "_mark";
    let element = document.getElementById(id);
    element.scrollIntoView({behavior: "smooth"});
    return;
}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

