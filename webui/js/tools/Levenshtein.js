
// MusicDB,  a music manager with web-bases UI that focus on music.
// Copyright (C) 2017-2020  Ralf Stemmer <ralf.stemmer@gmx.net>
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

// SOURCE: https://stackoverflow.com/questions/10473745/compare-strings-javascript-return-of-likely

function Similarity(s1, s2)
{
    let longer  = s1;
    let shorter = s2;
    if(s1.length < s2.length)
    {
        longer  = s2;
        shorter = s1;
    }

    let longerLength = longer.length;
    if(longerLength == 0)
    {
        return 1.0;
    }

    return (longerLength - LevenshteinDistance(longer, shorter)) / parseFloat(longerLength);
}


function LevenshteinDistance(s1, s2)
{
    s1 = s1.toLowerCase();
    s2 = s2.toLowerCase();

    let costs = new Array();
    for(let i = 0; i <= s1.length; i++)
    {
        let lastValue = i;
        for(let j = 0; j <= s2.length; j++)
        {
            if(i == 0)
                costs[j] = j;
            else
            {
                if(j > 0)
                {
                    let newValue = costs[j - 1];
                    if(s1.charAt(i - 1) != s2.charAt(j - 1))
                    newValue = Math.min(Math.min(newValue, lastValue),
                    costs[j]) + 1;
                    costs[j - 1] = lastValue;
                    lastValue = newValue;
                }
            }
        }
        if(i > 0)
            costs[s2.length] = lastValue;
    }
    return costs[s2.length];
}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

