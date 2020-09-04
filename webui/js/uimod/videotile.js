
"use strict";

/*
 *
 * Requirements:
 *   - JQuery
 *   - albumtile.css
 * Show:
 * Functions:
 * Callbacks:
 * Recommended Paths:
 * Trigger: (fnc -> sig)
 *   - GetVideo -> ShowVideo
 *
 */

function CreateVideoTile(MDBVideo, MDBAlbum, MDBArtist, topbuttonbox, bottombuttonbox = null, MDBTags = null)
{
    // Album is not used because it may be undefined very often
    let html        = "";
    let imgpath     = EncodeVideoThumbnailPath(MDBVideo.framesdirectory, MDBVideo.thumbnailfile, 150, 83);
    let anipath     = EncodeVideoThumbnailPath(MDBVideo.framesdirectory, MDBVideo.previewfile,   150, 83);
    let videoname   = MDBVideo.name.replace(" - ", " – ");
    let videoid     = MDBVideo.id;
    let artistname  = MDBArtist.name;
    let artistid    = MDBArtist.id;
    let videorelease= MDBVideo.release;
    let videorequest= "MusicDB_Request(\'GetVideo\', \'ShowVideo\', {videoid:"+videoid+"});";

    html += "<div class=\"ST_tile\">"; // main box

    // Artwork
    html += "<div class=\"VT_videocover\" data-size=\"small\">";
        html += "<img class=\"\" ";
        html += " src=\"" + imgpath + "\" ";
        html += " onmouseover=\"this.src=\'"+anipath+"\'\"";
        html += " onmouseout =\"this.src=\'"+imgpath+"\'\"";
        html += " onClick=\"" + videorequest + "\"";
        html += " title=\"Show this video\"";
        html += ">";
    html += "</div>";

    // Body
    html += "<div class=\"ST_body\">";
    html += "<div class=\"ST_row\">";
        // Video name
        html += "<div";
        html += " class=\"ST_songname fgcolor\">";
        html += videoname;
        html += "</div>";
    html += "</div>";
    html += "<div class=\"ST_row\">";
        // Artist name
        html += "<div class=\"ST_subtitle smallfont\">";
        html += "<span ";
        html += " onClick=\'ScrollToArtist("+artistid+");\'";
        html += " title=\"Scroll to this artist\"";
        html += " class=\"ST_artistname hlcolor\">";
        html += artistname;
        html += "</span>";
        html += "</div>";
    html += "</div>";
    html += "</div>";

    // Tagsbox (must be updated from external, only the empty divs are created
    html += "<div class=\"ST_tagbox hovpacity\">";
    html += "<div class=\"ST_row\">";
        html += "<div id=\"VideoTileGenre_"+videoid+"\" class=\"hlcolor\"></div>";
    html += "</div>";
    html += "<div class=\"ST_row\">";
        html += "<div id=\"VideoTileSubgenre_"+videoid+"\" class=\"hlcolor\"></div>";
    html += "</div>";
    html += "</div>";

    // Buttonbox
    html += "<div class=\"ST_buttonbox\">";
    html += "<div class=\"ST_row\">";
        html += "<div";
        html += " class=\"hlcolor\">";
        html += topbuttonbox;
        html += "</div>";
    html += "</div>";
    html += "<div class=\"ST_row\">";
        if(bottombuttonbox)
        {
            html += "<div";
            html += " class=\"hlcolor\">";
            html += bottombuttonbox;
            html += "</div>";
        }
    html += "</div>";
    html += "</div>";

    html += "</div>"; // main box

    return html;
}



class SmallVideoTile
{
    constructor(MDBVideo, onclick)
    {
        this.imgpath     = EncodeVideoThumbnailPath(MDBVideo.framesdirectory, MDBVideo.thumbnailfile, 150, 83);
        this.anipath     = EncodeVideoThumbnailPath(MDBVideo.framesdirectory, MDBVideo.previewfile,   150, 83);
        let videoid      = MDBVideo.id;
        let videoname    = MDBVideo.name;
        let videorelease = MDBVideo.release;

        this.imagebox                 = document.createElement("div");
        this.imageelement             = document.createElement("img");
        this.imageelement.src         = this.imgpath;
        this.imageelement.onmouseover = ()=>{this.imageelement.src = this.anipath;};
        this.imageelement.onmouseout  = ()=>{this.imageelement.src = this.imgpath;};
        this.imagebox.appendChild(this.imageelement);

        this.titleelement             = document.createElement("span");
        this.titleelement.textContent = videoname;
        this.titleelement.classList.add("hlcolor");
        this.titleelement.classList.add("smallfont");

        this.element                  = document.createElement("div");
        this.element.classList.add("smallvideotile");
        this.element.appendChild(this.imagebox);
        this.element.appendChild(this.titleelement);
        this.element.onclick = onclick;
    }



    GetHTMLElement()
    {
        return this.element;
    }
}

function CreateSmallVideoTile(MDBVideo, buttonbox)
{
    let html        = "";
    let imgpath     = EncodeVideoThumbnailPath(MDBVideo.framesdirectory, MDBVideo.thumbnailfile, 150, 83);
    let anipath     = EncodeVideoThumbnailPath(MDBVideo.framesdirectory, MDBVideo.previewfile,   150, 83);
    let videoid     = MDBVideo.id;
    let videoname   = MDBVideo.name;
    let videorelease= MDBVideo.release;
    let videorequest= "MusicDB_Request(\'GetVideo\', \'ShowVideo\', {videoid:"+videoid+"});";
    let datawidth   = "data-size=\"" + "medium" + "\"";

    html += "<div";
    html += " class=\"VT_videoentry\"";
    html += " " + datawidth;
    html += " onClick=\"" + videorequest + "\"";
    html += ">";

    if(buttonbox)
    {
        html += "<div class=\"VT_videobuttons\" " + datawidth + ">";
        html += "<span";
        html += " class=\"hlcolor\">";
        html += buttonbox;
        html += "</span>";
        html += "</div>";
    }

    // Cover
    html += "<div title=\"Show this Video\" class=\"VT_videocover\" " + datawidth + ">";
    html += "  <img src=\"" + imgpath + "\"";
    html += "    onmouseover=\"this.src=\'"+anipath+"\'\"";
    html += "    onmouseout =\"this.src=\'"+imgpath+"\'\"";
    html += "  \">";
    html += "</div>";

    // Meta Data
    html += "<div class=\"VT_videometadata\">";
    //html += "<span class=\"VT_videorelease hlcolor smallfont\">" + videorelease + "</span>";
    html += "<span class=\"VT_videoname fgcolor smallfont\" title=\""+videoname+"\">" + videoname + "</span>";
    html += "</div>";

    html += "</div>";

    return html;
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

