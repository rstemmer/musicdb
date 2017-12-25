
function ShowLyrics(songid, lyricsstate, lyrics)
{
    var html = "";
    var lyricstextarea = "LyricsTextArea";

    html += "<div id=\"LyricsContentbox\">";
    
    // Button-Box
    html += "<div class=\"lyricsbuttonbox\">";
    // state-selection
    html += "<div id=\"LyricsStateInputBox\">";
    html += "<span class=\"optionname\">State: </span>"
    html += "<select id=LyricsStateInput class=\"bgcolor hlcolor\">";
    html += " <option value=0>Empty</option>";
    html += " <option value=1>From File</option>";
    html += " <option value=2>From Net</option>";
    html += " <option value=3>From User</option>";
    html += " <option value=4>Instrumental</option>";
    html += "</select>";
    html += "</div>";
    html += "<span class=\"buttonseparator\"></span>"
    // hl-button
    html += "<span class=\"button triggerbutton\" id=\"InsertHighlightButton\" ";
    html += "data-state=untriggered ";
    html += "onClick=\"InsertText(\'"+lyricstextarea+"\', \'<<>>\')\">";
    html += "Add Highlight</span>";
    // refrain-button
    html += "<span class=\"button triggerbutton\" id=\"InsertRefrainButton\" ";
    html += "data-state=untriggered ";
    html += "onClick=\"InsertText(\'"+lyricstextarea+"\', \':: ref\')\">";
    html += "Add Refrain</span>";
    // comment-button
    html += "<span class=\"button triggerbutton\" id=\"InsertCommentButton\" ";
    html += "data-state=untriggered ";
    html += "onClick=\"InsertText(\'"+lyricstextarea+"\', \':: comment\')\">";
    html += "Add Comment</span>";
    html += "<span class=\"buttonseparator\"></span>"
    // undo-button (reload)
    html += "<span class=\"button triggerbutton\" id=\"UndoButton\" ";
    html += "data-state=triggered ";
    html += "onClick=\"MusicDB_Request(\'GetSongLyrics\', \'ShowLyrics\', {songid:" + songid + "});\">";
    html += "Reload From Server</span>";
    // save-button
    html += "<span class=\"button triggerbutton\" id=\"SaveButton\" ";
    html += "data-state=triggered ";
    html += "onClick=\"SaveLyrics(" + songid + ")\">";
    html += "Save Changes</span>";
    html += "<span class=\"buttonseparator\"></span>"
    // Get lyrics from crawler 
    html += "<span class=\"button triggerbutton\" id=\"LCCacheButton\" ";
    html += "data-state=untriggered ";
    html += "onClick=\"MusicDB_Request(\'GetLyricsCrawlerCache\', \'ShowCrawlerCache\', {songid:" + songid + "});\">";
    html += "Read Crawler Cache</span>";
    // Run Crawler 
    html += "<span class=\"button triggerbutton\" id=\"CrawlerButton\" ";
    html += "data-state=untriggered ";
    html += "onClick=\"TriggerCrawler(" + songid + ")\">";
    html += "Run Crawler</span>";
    // End of buttonbox
    html += "</div>";

    // Data
    html += "<div class=\"databox\">";

    // Lyrics
    html += "<div id=\"LyricsInputBox\">";
    html += "<textarea id=\'"+lyricstextarea+"\' rows=\"28\" cols=\"80\">";
    if(lyrics != null)
    {
        var lines = lyrics.split('\n');
        for(var i = 0; i < lines.length; i++)
        {
            html += lines[i];
            if(i < lines.length - 1) // next line ahead
                html += "\n";
        }
    }
    html += "</textarea>";
    html += "</div>"; // lyrics

    // Crawler-Cache
    html += "<div id=\"CrawlerBox\">";
    html += "To get some suggestions read out the crawler cache or run the Crawlers.";
    html += "</div>"; // crawlerbox

    html += "</div>"; // databox 

    html += "</div>"; // Contentbox 
    $("#LyricsTab").html(html);

    // Select correct value in lyrics-state selection box
    $("#LyricsStateInput").val(lyricsstate);
    $("#LyricsStateInput").on('keyup blur', function() {
                $("#UndoButton").attr("data-state", "untriggered");
                $("#SaveButton").attr("data-state", "untriggered");
            });

    // Change undo/save button state if lyrics are changed
    $("#"+lyricstextarea).on('keyup blur', function() {
                $("#UndoButton").attr("data-state", "untriggered");
                $("#SaveButton").attr("data-state", "untriggered");
            });
}


// Based on: http://stackoverflow.com/questions/11076975/insert-text-into-textarea-at-cursor-position-javascript
function InsertText(textareaid, myValue) 
{
    console.log(myValue);
    myField = document.getElementById(textareaid);
    if (myField.selectionStart || myField.selectionStart == '0') 
    {
        var startPos = myField.selectionStart;
        var endPos = myField.selectionEnd;
        myField.value = myField.value.substring(0, startPos)
            + myValue
            + myField.value.substring(endPos, myField.value.length);
    } 
    else 
    {
        myField.value += myValue;
    }
}


function SaveLyrics(songid)
{
    // Get values
    var lyrics = $("#LyricsTextArea").val();
    var state  = $("#LyricsStateInput").val();

    // Set button das triggers meaning server and client are sync.
    $("#UndoButton").attr("data-state", "triggered");
    $("#SaveButton").attr("data-state", "triggered");

    // send lyrics back to server to store them for ever
    MusicDB_Call("SetSongLyrics", {songid:songid, lyrics:lyrics, lyricsstate:state});
}



function TriggerCrawler(songid)
{
    $("#CrawlerButton").attr("data-state", "triggered");
    $("#LCCacheButton").attr("data-state", "triggered");
    $("#CrawlerBox").html("<i class=\"fa fa-cog fa-spin fa-fw\"></i> Crawling for Lyrics …");
    MusicDB_Request("RunLyricsCrawler", "ShowCrawlerCache", {songid: songid});
}

function ShowCrawlerCache(songid, cache)
{
    var html = "";

    if(cache.length == 0)
    {
        html = "No date in cache. Run Crawler to find Lyrics.";
    }
    else
    {
        html += "<table id=\"CrawlerCacheList\">";
        html += "<tr>";
        html += "<th>Crawler</th>";
        html += "<th>Date</th>";
        html += "<th>Lyrics</th>";
        html += "<th>Use</th>";
        html += "</tr>";
        for(var i = 0; i < cache.length; i++)
        {
            var entry = cache[i];
            var date = new Date(entry.updatetime * 1000);
            html += "<tr>";
            html += "<td>" + entry.crawler + "</td>";
            html += "<td>" + date.toLocaleString() + "</td>";
            html += "<td>";
                html += "<span ";
                html += "id=\"TriggerCachedLyricsVisibility_" + entry.id + "\" ";
                html += "data-state=\"untriggered\" ";
                html += "class=\"button triggerbutton TriggerCachedLyricsVisibility\" ";
                html += "onclick=\"TriggerCachedLyricsVisibility(" + entry.id + ");\"";
                html += ">Preview Lyrics";
                html += "</span>";
                html += "<div id=\"CachedLyrics_" + entry.id + "\" class=\"cachedlyrics\" >";
                html += entry.lyrics.replace(/(?:\r\n|\r|\n)/g, "<br />");
                html += "</div>";
            html += "</td>";
            html += "<td>";
                html += "<span class=\"button triggerbutton\" id=\"CopyButton\" ";
                html += "data-state=untriggered ";
                // Escape controls
                var lyricsentry = entry.lyrics;
                lyricsentry = lyricsentry.replace(/\n/g, "\\n");
                lyricsentry = lyricsentry.replace(/\t/g, "\\t");
                lyricsentry = lyricsentry.replace(/"/g,  '\\"');
                lyricsentry = lyricsentry.replace(/'/g,  "\\'");

                // clean up raw cashed stuff
                var div = document.createElement("div");
                div.innerHTML = lyricsentry;
                var lyricstext = div.textContent || div.innerText || "";

                console.log(lyricstext)
                lyricstext = lyricstext.replace(/\"/g, '&quot;');
                html += "onClick=\"InsertText(\'LyricsTextArea\', \'" + lyricstext + "\')\">";
                html += "Insert Lyrics</span>";
            html += "</td>";
            html += "</tr>";
        }
        html += "</table>";
    }
    $("#CrawlerBox").html(html);
    $("#CrawlerButton").attr("data-state", "untriggered");
    $("#LCCacheButton").attr("data-state", "untriggered");
}

function TriggerCachedLyricsVisibility(cacheid)
{
    var buttonid = "#TriggerCachedLyricsVisibility_" + cacheid;
    var boxid    = "#CachedLyrics_" + cacheid;
    if($(buttonid).attr("data-state") == "triggered")
    {
        $(buttonid).attr("data-state", "untriggered");
        $(boxid).css("display", "none");
    }
    else
    {
        $(buttonid).attr("data-state", "triggered");
        $(boxid).css("display", "block");
    }
}
// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

