// MusicDB,  a music manager with web-bases UI that focus on music.
// Copyright (C) 2017 - 2021  Ralf Stemmer <ralf.stemmer@gmx.net>
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


class NameDiffBase extends Element
{
    constructor(classes)
    {
        super("span", classes);
        this.olddiff = "";
        this.newdiff = "";
    }



    FormatNormal(textpart)
    {
        return `<span style="color: var(--color-gray)">${textpart}</span>`;
    }
    FormatValid(textpart)
    {
        return `<span style="color: var(--color-brightgreen)">${textpart}</span>`;
    }
    FormatDifferent(textpart)
    {
        return `<span style="color: var(--color-brightyellow)">${textpart}</span>`;
    }
    FormatInvalid(textpart)
    {
        return `<span style="color: var(--color-brightred)">${textpart}</span>`;
    }



    // Situations:
    // Old     | New     | Diff      | Format
    // --------+---------+-----------+-------------
    // valid   | valid   | equal     | gray/gray
    // valid   | valid   | different | yellow/green
    // valid   | invalid | *         | yellow/red
    // invalid | valid   | *         | red/green
    // invalid | invalid | *         | red/red
    AddDiffPart(oldvalid, newvalid, oldvalue, newvalue)
    {
        if(oldvalid && newvalid && oldvalue == newvalue)
        {
            this.olddiff += this.FormatNormal(oldvalue);
            this.newdiff += this.FormatNormal(newvalue);
        }
        else if(oldvalid && newvalid && oldvalue != newvalue)
        {
            this.olddiff += this.FormatDifferent(oldvalue);
            this.newdiff += this.FormatValid(newvalue);
        }
        else if(oldvalid && !newvalid)
        {
            this.olddiff += this.FormatDifferent(oldvalue);
            this.newdiff += this.FormatInvalid(newvalue);
        }
        else if(!oldvalid && newvalid)
        {
            this.olddiff += this.FormatInvalid(oldvalue);
            this.newdiff += this.FormatValid(newvalue);
        }
        else
        {
            this.olddiff += this.FormatInvalid(oldvalue);
            this.newdiff += this.FormatInvalid(newvalue);
        }
    }

    AddDiffText(text)
    {
        this.olddiff += this.FormatNormal(text);
        this.newdiff += this.FormatNormal(text);
    }

    ClearDiff()
    {
        this.olddiff = "";
        this.newdiff = "";
    }

}



class SongFileNameDiff extends NameDiffBase
{
    constructor()
    {
        super(["SongFileNameDiff"]);
    }



    // Expects object of class SongFileName
    UpdateDiff(oldname, newname)
    {
        this.ClearDiff();

        // CD Prefix
        if(newname.maxcds > 1)
        {
            this.AddDiffPart(
                oldname.CheckCDNumber() == null,
                newname.CheckCDNumber() == null,
                oldname.parts.cdnum,
                newname.parts.cdnum);
            if(oldname.parts.cdnum.length > 0)
                this.AddDiffText("-");
            else
                this.newdiff += this.FormatValid("-");
        }
        else if(oldname.maxcds > 1)
        {
            this.olddiff += this.FormatInvalid(oldname.parts.cdnum);
            this.olddiff += this.FormatInvalid("-");
        }
        
        // Track Number
        this.AddDiffPart(
            oldname.CheckTrackNumber() == null,
            newname.CheckTrackNumber() == null,
            oldname.parts.track,
            newname.parts.track);
        this.AddDiffText("&nbsp;");

        // Name
        this.AddDiffPart(
            oldname.CheckSongName() == null,
            newname.CheckSongName() == null,
            oldname.parts.name,
            newname.parts.name);
        this.AddDiffText(`.${newname.parts.ext}`);

        let diff = `${this.olddiff}&nbsp;➜&nbsp;${this.newdiff}`;
        this.SetInnerHTML(diff);
        return diff;
    }
}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

