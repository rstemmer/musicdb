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

const UPLOADTABLEHEADLINE = ["Source File Name", "Upload Progress", "Status"];
const UT_PATH_COLUMN      = 0;
const UT_PROGRESS_COLUMN  = 1;
const UT_STATUS_COLUMN    = 2;



class UploadTableRowBase extends TableRow
{
    constructor()
    {
        super(UPLOADTABLEHEADLINE.length, ["UploadTableRow"]); // Row with n cells
    }
}



class UploadTableHeadline extends UploadTableRowBase
{
    constructor()
    {
        super();
        this.AddCSSClass("TableHeadline");
        for(let cellnum in UPLOADTABLEHEADLINE)
        {
            let headline = document.createTextNode(UPLOADTABLEHEADLINE[cellnum]);
            this.SetContent(cellnum, headline);
        }
    }
}


class UploadTableRow extends UploadTableRowBase
{
    constructor(upload)
    {
        super();
        this.progressbar = new ProgressBar();
        this.Update(upload);
    }



    Update(upload)
    {
        let path     = upload.sourcefilename;
        let state    = upload.state;
        let filesize = upload.filesize;
        let offset   = upload.offset;

        // Create text cells
        let pathelement  = document.createTextNode(path);
        let stateelement = new UploadStatusText(state)

        // Update progress
        let progress = Math.round((offset / filesize) * 100);
        this.progressbar.SetProgress(progress);

        // Set cells
        this.SetContent(UT_PATH_COLUMN,     pathelement);
        this.SetContent(UT_PROGRESS_COLUMN, this.progressbar);
        this.SetContent(UT_STATUS_COLUMN,   stateelement);
    }
}



class UploadTable extends Table
{
    constructor()
    {
        super(["UploadTable"]);
        this.headline = new UploadTableHeadline();
        this.Clear();

        this.entries = new Object();
    }



    Clear()
    {
        super.Clear();
        this.AddRow(this.headline);
    }



    // Check if all upload tasks have been uploaded to 100%
    CheckCompleteness()
    {
        for(let key in this.entries)
        {
            let row      = this.entries[key].row;
            let progress = row.progressbar.GetProgress();

            if(progress < 100)
                return false;
        }
        return true;
    }



    GetAllUploadIDs()
    {
        return Object.keys(this.entries);
    }



    Update(uploads)
    {
        if(typeof uploads !== "object" || uploads === null)
            return;

        for(let upload of uploads)
            this.UpdateRow(upload);

        return;
    }



    UpdateRow(upload)
    {
        let key   = upload.id;
        let state = upload.state;

        if((key in this.entries) == false)
                this.CreateNewRow(upload);

        if(state == "remove")
        {
            let tablerow = this.entries[key].row;
            this.RemoveRow(tablerow);
            delete this.entries[key];
        }
        else
        {
            this.entries[key].row.Update(upload);
        }
    }



    CreateNewRow(upload)
    {
        // Create row showing the uploaded file
        let  newrow = new UploadTableRow(upload);
        this.AddRow(newrow);

        // Save row
        let key = upload.id;
        this.entries[key] = new Object();
        this.entries[key].row  = newrow;
    }
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

