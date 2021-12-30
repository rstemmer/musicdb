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



class SongFilesTableSettingsRow extends SongFilesTableRowBase
{
    // validationstatuscallback if a function called whenever data is validated.
    // It gets one argument (boolean) that, if true, tells that all data in this table is valid.
    constructor(cdnum, tracknum, songname, path, maxcds, validationstatuscallback)
    {
        super();

        // Song File Information
        this.maxcds         = maxcds;
        this.oldpath        = path;
        this.oldcdnum       = cdnum;
        this.oldtracknum    = tracknum;
        this.oldsongname    = songname;

        let oldfilename      = this.oldpath.split("/").slice(-1)[0];
        let oldfileextension = this.oldpath.split(".").slice(-1)[0];

        this.oldsongfile  = new SongFileName(oldfilename, this.maxcds);
        this.newsongfile  = new SongFileName(); // gets updated by user
        this.newsongfile.SetMaxCDs(this.maxcds);
        this.newsongfile.SetCDNumber(this.oldcdnum);
        this.newsongfile.SetTrackNumber(this.oldtracknum);
        this.newsongfile.SetSongName(this.oldsongname);
        this.newsongfile.SetFileExtension(oldfileextension);

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
        this.songnumberinput.SetValue(this.oldtracknum);
        this.songnameinput.SetValue(this.oldsongname)
        this.UpdateMaxCDs(maxcds, this.oldcdnum); // also updates cdumerinput
        this.validationstatuscallback = validationstatuscallback;

        // Set Cell Content
        this.SetContent(SFT_CDNUMBER_COLUMN,   this.cdnumberinput);
        this.SetContent(SFT_SONGNUMBER_COLUMN, this.songnumberinput);
        this.SetContent(SFT_SONGNAME_COLUMN,   this.songnameinput);
        this.SetContent(SFT_STATUS_COLUMN,     this.namestatus);
        this.SetContent(SFT_NEWPATH_COLUMN,    diffcontainer);
    }



    UpdateMaxCDs(maxcds, cdnumber=null)
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
            if(cdnumber!== null)
                this.cdnumberinput.SetValue(cdnumber);
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



    GetNewSongFileName()
    {
        return this.newsongfile.ComposeFileName();
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


class SongFilesTableRowFromEntry extends SongFilesTableSettingsRow
{
    constructor(MDBSong, maxcds, validationstatuscallback)
    {
        let oldpath     = MDBSong.path;
        let oldcdnum    = MDBSong.cd;
        let oldtracknum = MDBSong.number;
        let oldsongname = MDBSong.name;
        super(oldcdnum, oldtracknum, oldsongname, oldpath, maxcds, validationstatuscallback);
    }
}


class SongFilesTableRowFromFile extends SongFilesTableSettingsRow
{
    constructor(fileinfos, maxcds, validationstatuscallback)
    {
        let infosfrommeta = fileinfos.frommeta;
        let infosfromfile = fileinfos.fromfile;

        let oldpath     = fileinfos.path;
        let oldcdnum    = infosfrommeta.cdnumber   || infosfromfile.cdnumber;
        let oldtracknum = infosfrommeta.songnumber || infosfromfile.songnumber;
        let oldsongname = infosfrommeta.songname   || infosfromfile.songname;
        super(oldcdnum, oldtracknum, oldsongname, oldpath, maxcds, validationstatuscallback);
    }
}



class SongFilesTableBase extends Table
{
    // validationstatuscallback if a function called whenever data is validated.
    // It gets one argument (boolean) that, if true, tells that all data in this table is valid.
    constructor(validationstatuscallback)
    {
        super(["SongFilesTable"]);
        this.validationstatuscallback = validationstatuscallback;

        this.datainvalidmessage = new MessageBarError("Invalid Song Settings. Check red input fields.");

        this.multicdsetting     = new SettingsCheckbox(
            "Multiple CDs",
            "Check checkbox, if the album consists of more than one CD.",
            (ischecked)=>{this.onChangeMultiCDSettings(ischecked);});

        // Table
        this.multicdrow  = new TableSpanRow(SONGFILESTABLEHEADLINE.length, [], this.multicdsetting);
        this.headlinerow = new SongFilesTableHeadline();
        this.bottomrow   = new TableSpanRow(SONGFILESTABLEHEADLINE.length, [], this.datainvalidmessage);
        this.AddRow(this.multicdrow);
        this.AddRow(this.headlinerow);
        this.AddRow(this.bottomrow);
    }



    onChangeMultiCDSettings(ischecked)
    {
        if(ischecked)
            this.SetMaxCDs(1000);
        else
            this.SetMaxCDs(0);
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



    SetMaxCDs(maxcds)
    {
        for(let row of this.rows)
        {
            if(typeof row.UpdateMaxCDs === "function")
                row.UpdateMaxCDs(maxcds);
        }
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



    // Tries to figure out how many CDs the album has.
    // This method considers the meta data as well as the file name.
    GetMaxCDs(datalist)
    {
        window.console?.error("GetMaxCDs must be implemented by derived class!");
    }
    Update(datastructure)
    {
        window.console?.error("Update must be implemented by derived class!");
    }
}



class SongFilesTableFromFilesystem extends SongFilesTableBase
{
    constructor(validationstatuscallback)
    {
        super(validationstatuscallback);
    }



    // This interface must be implemented
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



    // This interface must be implemented
    Update(files)
    {
        // Try to Sort
        files.sort((a,b)=>{return a.frommeta.songnumber - b.frommeta.songnumber;});

        // Get max CDs
        let maxcds = this.GetMaxCDs(files);

        // Create new table
        this.Clear();
        this.AddRow(this.multicdrow);
        this.AddRow(this.headlinerow);
        for(let file of files)
        {
            let row = new SongFilesTableRowFromFile(file, maxcds, (isvalid)=>{this.onValidationUpdate();});
            this.AddRow(row);
        }
        this.AddRow(this.bottomrow);

        // Refresh state
        if(maxcds > 1)
            this.multicdsetting.SetState(true);
        else
            this.multicdsetting.SetState(false);
        this.onValidationUpdate();
    }
}



class SongFilesTableFromDatabase extends SongFilesTableBase
{
    constructor(validationstatuscallback)
    {
        super(validationstatuscallback);
    }



    // This interface must be implemented
    GetMaxCDs(MDBAlbum)
    {
        return MDBAlbum.numofcds;
    }



    // This interface must be implemented
    Update(MDBAlbum, MDBCDs)
    {
        let maxcds = this.GetMaxCDs(MDBAlbum);
        let songs  = new Array();
        for(let cdindex in MDBCDs)
        {
            for(let cdentry of MDBCDs[cdindex])
                songs.push(cdentry.song);
        }

        // Create new table
        this.Clear();
        this.AddRow(this.multicdrow);
        this.AddRow(this.headlinerow);
        for(let song of songs)
        {
            let row = new SongFilesTableRowFromEntry(song, maxcds, (isvalid)=>{this.onValidationUpdate();});
            this.AddRow(row);
        }
        this.AddRow(this.bottomrow);

        // Refresh state
        if(maxcds > 1)
            this.multicdsetting.SetState(true);
        else
            this.multicdsetting.SetState(false);
        this.onValidationUpdate();
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

