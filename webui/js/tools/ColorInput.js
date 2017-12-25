
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

// var alreadyinit = 0;
// function UpdateColorInputs(colorpreset)
// {
//     var elementid = "input.ColorInput";
//     var options   =
//         {
//             customBG:       '#222',
//             readOnly:       true,
//             draggable:      true,
//             size:           3,
//             noAlpha:        true,
//             appendTo:       document.body,
//             memoryColors:   colorpreset,
//             init:           function(elm, colors) 
//                 { // colors is a different instance (not connected to colorPicker)
//                     elm.style.backgroundColor = elm.value;
//                     elm.style.color           = colors.rgbaMixCustom.luminance > 0.22 ? '#222' : '#ddd';
//                 },
//             actionCallback: function(event, type)
//                 {
//                 },
//             convertCallback: function(colors, type)
//                 {
//                     // this callback gets called whenever colors are converted.
//                     // This is the only usefull callback available, so I had to use this one.
//                     
//                     if(this.input === null)
//                         return;
// 
//                     var color= "#" + colors.HEX;
//                     var id   = "#" + this.input.id;
//                     var previewfnc = $(id).attr("data-previewfunction");
//                     window[previewfnc](this.input.id, color);
//                 }
//         };
// 
//     var colorpicker = $(elementid).colorPicker(options);
// }

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

