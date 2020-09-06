
"use strict";
/*
 * This class provides the mdbstate view consisting of the following components:
 *
 * Requirements:
 *   - JQuery
 *   - lyrics.css
 *   - tools/hovpacity
 *   - colors
 * Show:
 * Functions:
 * Callbacks:
 * Recommended Paths:
 * Trigger: (fnc -> sig)
 *
 * IDEE:
 * Eine art metabox:
 * | headline        |
 * | lyrics | editor |
 * Man kann dann erst die Metabox irgendwo einfügen (ggf mit buttons)
 * Anschließend die lyrics von server anfordern
 * Und in einem 3. schritt den editor/crawler einblenden
 */

function ShowLyricsMetaBox(parentID, songid, albumid)
{
    var html = "";
    html += "<div id=\"LyricsMetaBox\">";
    html += "<div id=\"LMBHeadline\" class=\"hlcolor\">";
    html += Button_LyricsViewControls(songid, albumid);
    html += "</div>";

    html += "<div id=\"LMBBody\">";
    html += "<div id=\"LMBLyrics\"></div>";
    html += "<div id=\"LMBManager\"></div>";
    html += "</div>";
    html += "</div>";
    $("#"+parentID).html(html);
}

function ShowLyrics(parentID, MDBLyrics, mode)
{
    var html = "";

    html += "<div class=\"MDBLyricsBox\">";
    if(mode == "view")
        html += RenderLyrics(MDBLyrics.lyrics);
    else if(mode == "edit")
        html += LyricsTextbox(MDBLyrics.lyrics);
    else
        html += "Invalid Lyrics Mode!<br>Valid modes are \"view\" and \"edit\", not \""+mode+"\"";
    html += "</div>";
    
    // Create Element
    $("#"+parentID).html(html);
    UpdateStyle();
}

function LyricsTextbox(lyricscode)
{
    var html = "";
    html += "<textarea id=\"LMBLyricsCode\" rows=\"28\" cols=\"80\">";
    if(lyricscode != null)
    {
        var lines = lyricscode.split('\n');
        for(var i = 0; i < lines.length; i++)
        {
            html += lines[i];
            if(i < lines.length - 1) // next line ahead
                html += "\n";
        }
    }
    html += "</textarea>";
    return html;
}

function RenderLyrics(lyricscode)
{
    var html = "";
    html += "<div class=\"lyrics fgcolor seriffont\">";

    // if there are no lyrics, we are done now
    if(lyricscode === null)
    {
        html += "</div>";
        return html;
    }

    var lyrics = "<p>";                     // translated lyrics
    var lines  = lyricscode.split('\n');    // each line of the lyrics code
    var line;
    var intag  = "none";                    // name of the tag we are in ("none","refrain","comment")
    var inpar  = true;                      // flag if a paragraph is open

    for(var i=0; i<lines.length; i++)
    {
        line = lines[i];

        if(line.indexOf("::") == 0) // Tag
        {
            if(line.indexOf("ref") > -1)
            {
                lyrics += "<span class=\"refrain\">";
                intag   = "refrain";
            }
            else if(line.indexOf("comment") > -1)
            {
                lyrics += "<span class=\"comment\">";
                intag   = "comment";
            }
            else // empty tag = close-tag
            {
                if(intag == "refrain" || intag == "comment")
                {
                    if(inpar)
                    {
                        lyrics += "</p><!--p0-->";
                        inpar   = false;
                    }
                    lyrics += "</span>";
                    intag   = "";
                }
            }
        }
        else                        // Normal line
        {
            if(line.length == 0 && inpar) // Empty line inside a paragraph
            {
                lyrics += "</p><!--p1-->";
                inpar   = false;
            }
            else if(line.length == 0 && !inpar) // Empty line outside a paragraph (will be ignored)
            {
            }
            else
            {
                if(!inpar)
                {
                    lyrics += "<p>";
                    inpar   = true;
                }
                line    = line.replace(/<</g,  "<span class=\"hlcolor\">");
                line    = line.replace(/>>/g, "</span>");
                lyrics += line + "<br />";
            }
        }
    }
    lyrics += "</p>";

    html += lyrics;
    html += "</div>"; // lyrics
    return html;
}




// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

