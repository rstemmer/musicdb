
"use strict";

/**
 * onchange: send color to database
 * preview: apply current selection to UI
 */
function CreateColorInput(id, color, onchange, previewfunction)
{
    var html = "";
    html += "<input type=color class=\"ColorInput\" id=" + id + " value=\"" + color + "\" ";
    //html += " data-previewfunction=" + previewfunction.name;
    html += " onChange=\"" + onchange + "\"";
    html += " onInput=\""  + previewfunction.name + "(this.id, this.value)\">";
    //html += " onBlur=\""   + onblur   + "\">";
    return html;
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

