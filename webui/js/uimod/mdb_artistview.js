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
        let MDBArtist      = MDBArtistList[i].artist;
        let MDBContentList = undefined;
        let MDBContentType = undefined;
        if(MDBArtistList[i].albums !== undefined)
        {
            MDBContentList = MDBArtistList[i].albums;
            MDBContentType = "audio";
        }
        else if(MDBArtistList[i].videos !== undefined)
        {
            MDBContentList = MDBArtistList[i].videos;
            MDBContentType = "video";
        }

        // if there is no content, skip this artist (This should not happen with modern backend)
        if(MDBContentList.length == 0)
            continue;

        // Set jump mark if this is the first artist of a letter in the alphabet
        var artistname = MDBArtist.name;
        if(artistname.charAt(0) != firstchar)
        {
            firstchar = artistname.charAt(0).toUpperCase();
            html += "<div id="+firstchar+"_mark class=\"ATV_mark\"></div>";
        }

        if(MDBContentType == "audio")
            html += _ATV_CreateArtistEntryWithAlbums(MDBArtist, MDBContentList);
        else if(MDBContentType == "video")
            html += _ATV_CreateArtistEntryWithVideos(MDBArtist, MDBContentList);
    }
    
    html += "<span id=BTM_mark class=\"ATV_mark\"></span>";
    html += "</div>"; // main box

    // Create Element
    $("#"+parentID).html(html);
    $(".nano").nanoScroller();          // update scrollbars
}


function _ATV_CreateArtistEntryWithAlbums(MDBArtist, MDBAlbumList)
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


function _ATV_CreateArtistEntryWithVideos(MDBArtist, MDBVideoList)
{
    var html = "";
    var label= "Artist_" + MDBArtist.id;    // Label for ScrollToArtist

    html += "<div id=" + label + " class=\"ATV_artistentry\">";

    html += "<span class=\"ATV_artistname fgcolor\">";
    html += MDBArtist.name;
    html += "</span>";
   
    // Create the overview of the artists albums
    html += "<div class=\"ATV_albumlist\">"; // FIXME: A different class may be better
    for(var i in MDBVideoList)
    {
        let MDBVideo = MDBVideoList[i].video;
        html += CreateSmallVideoTile(MDBVideo);
    }
    html += "</div>"; // close albumlist div

    html += "</div>"; // close artistentry div

    return html;
}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

