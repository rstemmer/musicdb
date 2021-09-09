// MusicDB,  a music manager with web-bases UI that focus on music.
// Copyright (C) 2021-2021  Ralf Stemmer <ralf.stemmer@gmx.net>
// 
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
// 
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
// 
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.

"use strict";



// Expecting relative luminance as returned by CalculateRelativeLuminance
function CalculateContrast(RelLumLight, RelLumDark)
{
    // Calculate Accessibility (color contrast) to W3.org:
    // https://www.w3.org/TR/WCAG21/#contrast-minimum
    // Using the following formula:
    //      Source: https://www.w3.org/TR/WCAG21/#dfn-contrast-ratio
    //
    //      (L1 + 0.05) / (L2 + 0.05), where
    //
    //       · L1 is the relative luminance of the lighter of the colors, and
    //       · L2 is the relative luminance of the darker of the colors.
    //
    return (RelLumLight + 0.05) / (RelLumDark + 0.05);
}



// Expecting a html RGB code formatted as #rrggbb
function CalculateRelativeLuminance(htmlrgb)
{
    //  Relative luminance is defined in the source: https://www.w3.org/TR/WCAG21/#dfn-relative-luminance
    //  For the sRGB colorspace, the relative luminance of a color is defined as 
    //
    //  L = 0.2126 * R + 0.7152 * G + 0.0722 * B where R, G and B are defined as:
    //
    //  if RsRGB <= 0.03928 then R = RsRGB/12.92 else R = ((RsRGB+0.055)/1.055) ^ 2.4
    //  if GsRGB <= 0.03928 then G = GsRGB/12.92 else G = ((GsRGB+0.055)/1.055) ^ 2.4
    //  if BsRGB <= 0.03928 then B = BsRGB/12.92 else B = ((BsRGB+0.055)/1.055) ^ 2.4
    //
    //  and RsRGB, GsRGB, and BsRGB are defined as:
    //
    //  RsRGB = R8bit/255
    //  GsRGB = G8bit/255
    //  BsRGB = B8bit/255
    //
    let rgb = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(htmlrgb);

    function Preprocess(hexcolor)
    {
        let integer = parseInt(hexcolor, 16);
        let sRGB    = integer / 255.0;
        let color;
        if(sRGB <= 0.03928)
            color = sRGB / 12.92;
        else
            color = Math.pow((sRGB + 0.055) / 1.055, 2.4);
        return color;
    }

    let R = Preprocess(rgb[1]);
    let G = Preprocess(rgb[2]);
    let B = Preprocess(rgb[3]);
    let L = 0.2126 * R + 0.7152 * G + 0.0722 * B;
    return L;
}




// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

