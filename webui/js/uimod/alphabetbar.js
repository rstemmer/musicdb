
"use strict";
/*
 * This class provides the mdbstate view consisting of the following components:
 *
 * Requirements:
 *   - JQuery
 *   - alphabetbar.css
 *   - mdb_button.css
 *   - tools/scrollto.js
 * Show:
 * Functions:
 * Callbacks:
 * Recommended Paths:
 * Trigger: (fnc -> sig)
 *
 */

function ShowAlphabetBar(parentID)
{
    var html = "";

    html += "<div id=MDBAlphabetBar class=\"hlcolor smallfont BTN_button\">";
    
    html += "<span class=\"AB_Jumpchar AB_Arrow\" onclick=\"ScrollToMarker('TOP')\">";
    html += "<i class=\"fa fa-arrow-up\"></i></span>";

    var alphabet = ["A","B","C","D",
                    "E","F","G","H",
                    "I","J","K","L",
                    "M","N","O","P",
                    "Q","R","S","T",
                    "U","V","W","X",
                    "Y","Z"];
    for(var i in alphabet)
    {
        var chr = alphabet[i];
        html += "<span class=\"AB_Jumpchar\"";
        html += " onclick=\"ScrollToMarker('" + chr + "')\">";
        html += chr;
        html += "</span>";
    }

    html += "<span class=\"AB_Jumpchar AB_Arrow\" onclick=\"ScrollToMarker('BTM')\">";
    html += "<i class=\"fa fa-arrow-down\"></i></span>";


    html += "</div>";
    
    // Create Element
    $("#"+parentID).html(html);
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

