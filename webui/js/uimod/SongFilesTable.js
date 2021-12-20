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

const SONGFILESTABLEHEADLINE = ["CD", "Song Nr.", "Song Name", "Status", "Song File Name"];
const SFT_CDNUMBER_COLUMN   = 0;
const SFT_SONGNUMBER_COLUMN = 1;
const SFT_SONGNAME_COLUMN   = 2;
const SFT_STATUS_COLUMN     = 3;
const SFT_NEWPATH_COLUMN    = 4;



class SongFilesTableRowBase extends TableRow
{
    constructor()
    {
        super(SONGFILESTABLEHEADLINE.length, ["SongFilesTableRow"]);
    }
}


class SongFilesTableHeadline extends SongFilesTableRowBase
{
    constructor()
    {
        super();
        this.AddCSSClass("TableHeadline");

        for(let cellnum in SONGFILESTABLEHEADLINE)
        {
            let headline = new Element("span");
            headline.SetInnerText(SONGFILESTABLEHEADLINE[cellnum]);
            this.SetContent(cellnum, headline);
        }
    }
}


class SongFilesTableRow extends SongFilesTableRowBase
{
    // validationstatuscallback if a function called whenever data is validated.
    // It gets one argument (boolean) that, if true, tells that all data in this table is valid.
    constructor(fileinfos, maxcds, validationstatuscallback)
    {
        super();
        
        // Song File Information
        this.infosfrommeta = fileinfos.frommeta;
        this.infosfromfile = fileinfos.fromfile;
        this.maxcds       = maxcds;
        this.filepath     = fileinfos.path;
        this.oldsongfile  = new SongFileName(this.filepath.split("/").slice(-1)[0], maxcds);
        this.newsongfile  = new SongFileName(this.filepath.split("/").slice(-1)[0], maxcds); // gets updated by user

        // Control Elements
        this.namestatus  = new StatusText();
        this.diffelement = new SongFileNameDiff();

        this.cdnumberinput   = new NumberInput();
        this.songnumberinput = new NumberInput();
        this.songnameinput   = new TextInput();

        let  diffcontainer   = new Element("div", ["songfilepath", "flex-middle"]);
        let  songfileicon    = new SVGIcon("SongFile");
        diffcontainer.AppendChild(songfileicon);
        diffcontainer.AppendChild(this.diffelement);

        this.cdnumberinput.SetValidateEventCallback(  (value)=>{return this.ValidateCDNumber(value);  });
        this.songnumberinput.SetValidateEventCallback((value)=>{return this.ValidateSongNumber(value);});
        this.songnameinput.SetValidateEventCallback(  (value)=>{return this.ValidateSongName(value);  });
        this.cdnumberinput.SetAfterValidateEventCallback(  (value, valid)=>{this.EvaluateNewPath();});
        this.songnumberinput.SetAfterValidateEventCallback((value, valid)=>{this.EvaluateNewPath();});
        this.songnameinput.SetAfterValidateEventCallback(  (value, valid)=>{this.EvaluateNewPath();});


        // First set initial data, that work with the callback function
        this.validationstatuscallback = null;
        this.songnumberinput.SetValue(this.infosfrommeta.songnumber || this.infosfromfile.songnumber);
        this.songnameinput.SetValue(  this.infosfrommeta.songname   || this.infosfromfile.songname);
        this.UpdateMaxCDs(maxcds); // also updates cdumerinput
        this.validationstatuscallback = validationstatuscallback;

        // Set Cell Content
        this.SetContent(SFT_CDNUMBER_COLUMN,   this.cdnumberinput);
        this.SetContent(SFT_SONGNUMBER_COLUMN, this.songnumberinput);
        this.SetContent(SFT_SONGNAME_COLUMN,   this.songnameinput);
        this.SetContent(SFT_STATUS_COLUMN,     this.namestatus);
        this.SetContent(SFT_NEWPATH_COLUMN,    diffcontainer);
    }



    UpdateMaxCDs(maxcds)
    {
        this.maxcds = maxcds;
        this.newsongfile.SetMaxCDs(this.maxcds);

        if(this.maxcds <= 1) // If there is just one CD, no CD number should be given
        {
            this.cdnumberinput.SetEnabled(false);
            this.cdnumberinput.SetValue("");
        }
        else
        {
            this.cdnumberinput.SetEnabled(true);
            this.cdnumberinput.SetValue(this.infosfrommeta.cdnumber || this.infosfromfile.cdnumber);
        }
    }



    EvaluateNewPath()
    {
        // Get Parts
        let cdnum = this.cdnumberinput.GetValue();
        let track = this.songnumberinput.GetValue();
        let name  = this.songnameinput.GetValue();

        // Set Parts
        this.newsongfile.SetCDNumber(cdnum);
        this.newsongfile.SetTrackNumber(track);
        this.newsongfile.SetSongName(name);

        // Check Parts
        let cdnumerror = this.newsongfile.CheckCDNumber();
        let trackerror = this.newsongfile.CheckTrackNumber();
        let nameerror  = this.newsongfile.CheckSongName();

        // Compose Error Message
        let errors = "";
        if(cdnumerror)
            errors += `${cdnumerror} `;
        if(trackerror)
            errors += `${trackerror} `;
        if(nameerror)
            errors += `${nameerror}`;

        // Set Error is existing
        if(errors.length > 0)
            this.namestatus.SetStatus("bad", errors);
        else
            this.namestatus.SetStatus("good", "File name is valid.");

        // Show current renaming status
        this.diffelement.UpdateDiff(this.oldsongfile, this.newsongfile);

        // Give error status to the parent
        let validationstatus = this.CheckIfValid();
        if(typeof this.validationstatuscallback === "function")
            this.validationstatuscallback(validationstatus);
    }



    ValidateCDNumber(value)
    {
        let error = this.newsongfile.CheckCDNumber(value);
        if(error === null)
            return true;
        return false;
    }
    ValidateSongNumber(value)
    {
        let error = this.newsongfile.CheckTrackNumber(value);
        if(error === null)
            return true;
        return false;
    }
    ValidateSongName(value)
    {
        let error = this.newsongfile.CheckSongName(value);
        if(error === null)
            return true;
        return false;
    }



    // Returns an object with two attributes: .oldname, .newname
    // If new and old paths are the same, null gets returned
    GetRenameRequest()
    {
        let retval = new Object();
        retval.oldname  = this.oldsongfile.origname;
        retval.newname  = this.newsongfile.ComposeFileName();
        retval.htmldiff = this.diffelement.UpdateDiff(this.oldsongfile, this.newsongfile);

        // No rename request when the names are still equal
        if(retval.oldname == retval.newname)
            return null;

        return retval;
    }



    GetNewSongFileName()
    {
        return this.newsongfile.ComposeFileName();
    }



    CheckIfValid()
    {
        // First part is the optional CD number
        if(this.maxcds > 1)
        {
            if(this.cdnumberinput.GetValidState() !== true)
                return false;
        }

        if(this.songnumberinput.GetValidState() !== true)
            return false;
        if(this.songnameinput.GetValidState() !== true)
            return false;
        return true;
    }
}



class SongFilesTable extends Table
{
    // validationstatuscallback if a function called whenever data is validated.
    // It gets one argument (boolean) that, if true, tells that all data in this table is valid.
    constructor(validationstatuscallback)
    {
        super(["SongFilesTable"]);
        this.validationstatuscallback = validationstatuscallback;

        this.datainvalidmessage = new MessageBarError("Invalid Song Settings. Check red input fields.");

        // Table
        this.headlinerow = new SongFilesTableHeadline();
        this.bottomrow   = new TableSpanRow(SONGFILESTABLEHEADLINE.length, [], this.datainvalidmessage.GetHTMLElement());
        this.AddRow(this.headlinerow);
        this.AddRow(this.bottomrow);
    }



    // Returns a array of objects with two attributes: .newname, .oldname
    GetRenameRequests()
    {
        let renamerequests = new Array();
        for(let row of this.rows)
        {
            if(typeof row.GetRenameRequest === "function")
            {
                let renamerequest = row.GetRenameRequest();
                if(renamerequest !== null)
                    renamerequests.push(renamerequest);
            }
        }
        return renamerequests;
    }



    GetNewSongFileNames()
    {
        let filenames = new Array();
        for(let row of this.rows)
        {
            if(typeof row.GetNewSongFileName === "function")
            {
                let filename = row.GetNewSongFileName();
                if(filename !== null)
                    filenames.push(filename);
            }
        }
        return filenames;
    }



    onValidationUpdate()
    {
        let validationstatus = this.CheckIfValid();
        if(validationstatus === true)
            this.datainvalidmessage.Hide();
        else
            this.datainvalidmessage.Show();

        if(typeof this.validationstatuscallback === "function")
            this.validationstatuscallback(validationstatus);
    }



    CheckIfValid()
    {
        for(let row of this.rows)
        {
            if(typeof row.CheckIfValid === "function")
            {
                if(row.CheckIfValid() !== true)
                    return false;
            }
        }
        return true;
    }



    // Tries to figure out how many CDs the album has.
    // This method considers the meta data as well as the file name.
    GetMaxCDs(files)
    {
        let cdnumbers = new Array();
        for(let file of files)
        {
            let frommeta = file.frommeta;
            let fromfile = file.fromfile;

            let cdnumfrommeta = 0;
            if(typeof frommeta?.cdnumber !== "undefined")
                cdnumfrommeta = frommeta.cdnumber;

            let cdnumfromfile = 0;
            if(typeof fromfile?.cdnumber !== "undefined")
                cdnumfromfile = fromfile.cdnumber;

            let cdnum = Math.max(cdnumfromfile, cdnumfrommeta);
            cdnumbers.push(cdnum);
        }

        let maxcds = Math.max(...cdnumbers);
        return maxcds;
    }



    SetMaxCDs(maxcds)
    {
        for(let row of this.rows)
        {
            if(typeof row.UpdateMaxCDs === "function")
                row.UpdateMaxCDs(maxcds);
        }
    }



    Update(files)
    {
        // Try to Sort
        files.sort((a,b)=>{return a.frommeta.songnumber - b.frommeta.songnumber;});

        // Get max CDs
        let maxcds = this.GetMaxCDs(files);

        // Create new table
        this.Clear();
        this.AddRow(this.headlinerow);
        for(let file of files)
        {
            let row = new SongFilesTableRow(file, maxcds, (isvalid)=>{this.onValidationUpdate();});
            this.AddRow(row);
        }
        this.AddRow(this.bottomrow);
        this.onValidationUpdate(); // Refresh validation
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

