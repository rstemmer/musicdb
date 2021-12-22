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


class AlbumDirectoryNameDiff extends NameDiffBase
{
    constructor()
    {
        super(["AlbumDirectoryNameDiff"]);
    }



    // Expects object of class AlbumDirectoryName
    UpdateDiff(oldname, newname)
    {
        this.ClearDiff();

        // Release Year
        this.AddDiffPart(
            oldname.CheckReleaseYear() == null,
            newname.CheckReleaseYear() == null,
            oldname.parts.year,
            newname.parts.year);
        if(oldname.parts.year.length > 0)
            this.AddDiffText("&nbsp;-&nbsp;");
        else
            this.newdiff += this.FormatValid("&nbsp;-&nbsp;");

        // Name
        this.AddDiffPart(
            oldname.CheckAlbumName() == null,
            newname.CheckAlbumName() == null,
            oldname.parts.name,
            newname.parts.name);

        let diff = `${this.olddiff}&nbsp;➜&nbsp;${this.newdiff}`;
        this.SetInnerHTML(diff);
        return diff;
    }
}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

