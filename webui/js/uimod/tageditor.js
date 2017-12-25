
"use strict";

//function Taginput_UpdateTags();
//

/*
 * on fnc:GetSong/GetAlbum, sig:UpdateTagInput
 *      Taginput_Update(pass.taginputid, args.tags);
 *
 */

/**
 * @param {string} tageditorid - id of the input element
 * @param {string} tagclass - ``"Genre"``, ``"Subgenre"``, ``"Mood"``
 *
 * @returns {string} HTML code of the Taginput control
 */
function Tageditor_Create(tageditorid, tagclass)
{
    var html = "";
    html += "<div id=\"" + tageditorid + "\"";
    html += " data-tagclass=\'" + tagclass + "\'";
    html += " class=\"TAGE_Container\">";


    html += "</div>";
    return html;
}

/**
 *
 * @param {string} tageditid - ID of the tageditor that shall be updated
 *
 * @returns *nothing*
  */
function Tageditor_Update(tageditid)
{

    var jqid = "#"+tageditid;
    var tagclass = $(jqid).attr("data-tagclass");

    var taglist;
    if(tagclass == "Genre")
        taglist = Tagmanager_GetGenres()
    else if(tagclass == "Subgenre")
        taglist = Tagmanager_GetSubgenres()
    else if(tagclass == "Mood")
        taglist = Tagmanager_GetMoods()
    else
    {
        window.console && console.log("Error: Invalid tagclass: "+tagclass);
        return;
    }

    var html = "";
    for(let tag of taglist)
    {
        html += tag.name;
        html += "<br>";
    }

    $(jqid).html(html);
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

