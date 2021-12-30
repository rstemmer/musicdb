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
 * This class handles song file names trying to follow the MusicDB naming scheme.
 * Whenever the class has to decide between information from meta data or from the original file name,
 * the information from the original file name is preferred.
 *
 * The file name includes the file extension.
 * By default, the initial file name gets not validated.
 */

/*
 * TODO:
 * Split into two classes: SongFileName and SongFileEditor
 * Instead of three internal parts, three SongFileName objects for old, tmp and new should exist.
 */

class SongFileName
{
    constructor(origname=null, maxcds=1, validate=false)
    {
        this.SetMaxCDs(maxcds);
        this.origname = origname;
        this.parts  = new Object();
        this.parts.cdnum = "";
        this.parts.track = "";
        this.parts.name  = "";
        this.parts.ext   = "";
        if(typeof origname === "string")
            this.parts  = this.DecomposeFileName(origname, validate);
    }



    SetMaxCDs(maxcds)
    {
        this.maxcds = parseInt(maxcds);
    }

    SetCDNumber(cdnumber)
    {
        //this.parts.cdnum = cdnumber;
        this.parts.cdnum = this.MakeValidCDNumber(cdnumber);
    }

    SetTrackNumber(tracknumber)
    {
        //this.parts.track = tracknumber;
        this.parts.track = this.MakeValidTrackNumber(tracknumber);
    }

    SetSongName(songname)
    {
        this.parts.name = songname;
    }

    SetFileExtension(extension)
    {
        //this.parts.ext = extension;
        this.parts.ext = this.MakeValidFileExtension(extension);
    }



    MakeValidCDNumber(cdnumber)
    {
        let validcdnum = "";

        if(typeof cdnumber === "number")
            validcdnum = `${cdnumber}`;
        
        if(cdnumber.length === 0 || isNaN(cdnumber))
            validcdnum = "";
        else
            validcdnum = cdnumber;

        return validcdnum;
    }


    MakeValidTrackNumber(tracknumber)
    {
        let validtracknumber = "00";

        if(typeof tracknumber === "number")
            validtracknumber = `${tracknumber}`;
        else if(!isNaN(tracknumber))
            validtracknumber = tracknumber;

        if(validtracknumber.length === 1)
            validtracknumber = `0${validtracknumber}`;

        return validtracknumber;
    }


    MakeValidSongName(songname)
    {
        let validsongname = songname.replaceAll("/", "∕"); // Division slash
        return validsongname;
    }


    MakeValidFileExtension(extension)
    {
        let validextension = extension.toLowerCase();
        return validextension;
    }



    /*
     * Check* returns null if the component is valid.
     * If not a string gets returned telling what is wrong.
     */
    CheckCDNumber(cdnumber=null)
    {
        if(cdnumber === null)
            cdnumber = this.parts.cdnum;

        if(cdnumber.length === 0)
        {
            if(this.maxcds <= 1)
                return null;
            else
                return `No CD number given. Number required because there exists ${this.maxcds} different CDs in the Album.`;
        }

        if(isNaN(cdnumber))
            return `CD number "${cdnumber}" is not an actual number.`;

        if(parseInt(cdnumber) <= 0)
            return `Track number "${cdnumber}" is ≤ 0.`;

        if(parseInt(cdnumber) > this.maxcds)
            return `CD number "${cdnumber}" is > ${this.maxcds}, the maximum of CDs in the Album.`;

        return null;
    }

    CheckTrackNumber(tracknumber=null)
    {
        if(tracknumber === null)
            tracknumber = this.parts.track;

        if(tracknumber.length === 0)
            return `No track number given.`;

        if(isNaN(tracknumber))
            return `Track number "${tracknumber}" is not an actual number.`;

        if(parseInt(tracknumber) <= 0)
            return `Track number "${tracknumber}" is ≤ 0.`;

        return null;
    }

    CheckSongName(songname=null)
    {
        if(songname === null)
            songname = this.parts.name;
        
        if(songname.length === 0)
            return `No song name given. A song name must have at least one character.`;
        
        return null;
    }



    DecomposeFileName(filename, validate=true)
    {
        let parts   = new Object();

        // Process prefix (CD number and track number)
        let prefix  = filename.split(" ")[0];

        if(prefix.indexOf("-") > -1)
        {
            parts.cdnum = prefix.split("-")[0];
            parts.track = prefix.split("-")[1];
        }
        else
        {
            parts.cdnum = "";
            parts.track = prefix;
        }

        // Process body (Song name)
        let body = filename.split(" ").slice(1).join(" ");
        body     = body.split(".").slice(0, -1).join(".");

        parts.name = body;

        // Process suffix (File type extension)
        let suffix = filename.split(".").slice(-1)[0];
        parts.ext  = suffix;

        if(validate)
        {
            parts.cdnum = this.MakeValidCDNumber(parts.cdnum);
            parts.track = this.MakeValidTrackNumber(parts.track);
            parts.name  = this.MakeValidSongName(parts.name);
            parts.ext   = this.MakeValidFileExtension(parts.ext);
        }

        return parts;
    }


    ComposeFileName()
    {
        let filename = "";

        if(this.maxcds > 1)
            filename += `${this.parts.cdnum}-`;
        filename += `${this.parts.track} ${this.parts.name}.${this.parts.ext}`;
        filename  = filename.replaceAll("/", "∕"); // Division slash

        return filename;
    }
}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

