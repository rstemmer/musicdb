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

const UPLOADTABLEHEADLINE = ["Source Path", "Status", "Controls"];
const UT_PATH_COLUMN   = 0;
const UT_STATUS_COLUMN = 1;
const UT_BUTTON_COLUMN = 2;



class UploadTableRowBase extends TableRow
{
    constructor()
    {
        super(UPLOADTABLEHEADLINE.length, ["UploadTableRow"]); // Row with n cells
    }
}



class UploadTableHeadline extends UploadTableRowBase
{
    constructor(MDBMood)
    {
        super();
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
        this.Update(upload);
    }



    Update(upload)
    {
        let path  = upload.sourcefilename;
        let state = upload.state;

        // Create cells
        let pathelement  = document.createTextNode(path);
        let stateelement = document.createTextNode(state);

        // Control buttons
        let importbutton = new SVGButton("Remove", ()=>{this.onRemove();}, "Delete this uploaded file");
        let buttonbox    = new ButtonBox()
        buttonbox.AddButton(importbutton);

        // Set cells
        this.SetContent(UT_PATH_COLUMN,   pathelement);
        this.SetContent(UT_STATUS_COLUMN, stateelement);
        this.SetContent(UT_BUTTON_COLUMN, buttonbox.GetHTMLElement());
    }



    onRemove()
    {
        //MusicDB_Request("DeleteTag", "UpdateTags", {tagid: MDBMood.id}, {origin: "MoodSettings"});
        window.console && console.log("Import Upload");
    }
}



class UploadTable extends Table
{
    constructor(uploads=null)
    {
        super(["UploadTable"]);
        this.headline = new UploadTableHeadline();
        this.Clear();
        this.AddRow(this.headline);

        this.entries = new Object();
    }



    Update(uploads)
    {
        if(typeof uploads !== "object" || uploads === null)
            return;

        for(let upload of uploads)
        {
            if(! this.TryUpdateRow(upload))
            {
                this.CreateNewRow(upload);
            }
        }

        // TODO: Remove row of no longer existing uploads

        return;
    }



    TryUpdateRow(upload)
    {
        let key = upload.id;
        if(! (key in this.entries))
            return false;

        this.entries[key].row.Update(upload);
        this.entries[key].form.UpdateUploadTask(upload);
        this.entries[key].form.ValidateForm();

        return true;
    }



    CreateNewRow(upload)
    {
        let  newrow = new UploadTableRow(upload);
        this.AddRow(newrow);

        let importform = null;
        switch(upload.contenttype)
        {
            case "video":
                importform = new VideoImportForm("Unknown Artist", upload.sourcefilename, "Internet", 2000, upload);
                break;
        }

        if(importform != null)
        {
            this.AddContextView(importform.GetHTMLElement());
            importform.ValidateForm();
        }

        // Save row
        let key = upload.id;
        this.entries[key] = new Object();
        this.entries[key].row  = newrow;
        this.entries[key].form = importform;
    }
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

