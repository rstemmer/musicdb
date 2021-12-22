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

/*
 * This class handles album directory names trying to follow the MusicDB naming scheme.
 * Whenever the class has to decide between information from meta data or from the original file name,
 * the information from the original file name is preferred.
 *
 * By default, the initial file name gets not validated.
 */

class ArtistDirectoryName
{
    constructor(origname=null, validate=false)
    {
        this.origname = origname;
        this.parts  = new Object();
        this.parts.name = "";
        if(typeof origname === "string")
            this.parts = this.DecomposeDirectoryName(origname, validate);
    }



    SetArtistName(artistname)
    {
        this.parts.name = artistname;
    }



    MakeValidArtistName(name)
    {
        let validname = name.replace(/\//g,"∕"); // Division slash
        return validname;
    }



    /*
     * Check* returns null if the component is valid.
     * If not a string gets returned telling what is wrong.
     */
    CheckArtistName(name=null)
    {
        if(name === null)
            name = this.parts.name;
        
        if(name.length === 0)
            return `No artist name given. An artist name must have at least one character.`;
        
        return null;
    }



    DecomposeArtistName(name, validate=true)
    {
        let parts   = new Object();

        parts.name = name;

        if(validate)
        {
            parts.name = this.MakeValidAlbumName(parts.name);
        }

        return parts;
    }


    ComposeArtistName()
    {
        let name = `${this.parts.name}`;
        return name;
    }
}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

