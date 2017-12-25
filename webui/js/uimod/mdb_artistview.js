/*
 * This class provides the HUD consisting of the following components:
 *
 * Requirements:
 *   - JQuery
 *   - mdb_artistview.css
 *   - Set to each artist an id "Artist_[artistid]"
 * Show:
 *   - ShowArtists(parentID, MDBArgs);
 * Functions:
 * Callbacks:
 * Recommended Paths:
 * Trigger: (fnc -> sig)
 *   - GetAlbum -> ShowAlbum
 */

function ShowArtists(parentID, MDBArtistList)
{
    var html = "";

    html += "<div id=ArtistViewBox>"; // main box
    html += "<span id=TOP_mark class=\"ATV_mark\"></span>";
    
    // For each Arist
    var firstchar  = " ";   // track first letter of the artistname to set jumpmarks
    for(var i in MDBArtistList)
    {
        var MDBArtist    = MDBArtistList[i].artist;
        var MDBAlbumList = MDBArtistList[i].albums;

        // if there are no albums, skip this artist
        if(MDBAlbumList.length == 0)
            continue;

        // Set jump mark if this is the first artist of a letter in the alphabet
        var artistname = MDBArtist.name;
        if(artistname.charAt(0) != firstchar)
        {
            firstchar = artistname.charAt(0).toUpperCase();
            html += "<div id="+firstchar+"_mark class=\"ATV_mark\"></div>";
        }

        html += _ATV_CreateArtistEntry(MDBArtist, MDBAlbumList);
    }
    
    html += "<span id=BTM_mark class=\"ATV_mark\"></span>";
    html += "</div>"; // main box

    // Create Element
    $("#"+parentID).html(html);
    $(".nano").nanoScroller();          // update scrollbars
}


function _ATV_CreateArtistEntry(MDBArtist, MDBAlbumList)
{
    var html = "";
    var label= "Artist_" + MDBArtist.id;    // Label for ScrollToArtist

    html += "<div id=" + label + " class=\"ATV_artistentry\">";

    html += "<span class=\"ATV_artistname fgcolor\">";
    html += MDBArtist.name;
    html += "</span>";
   
    // Create the overview of the artists albums
    html += "<div class=\"ATV_albumlist\">";
    for(var i in MDBAlbumList)
    {
        var MDBAlbum   = MDBAlbumList[i].album;
        html += CreateAlbumTile(MDBAlbum);
    }
    html += "</div>"; // close albumlist div

    html += "</div>"; // close artistentry div

    return html;
}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

