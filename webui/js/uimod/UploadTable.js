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

const UPLOADTABLEHEADLINE = ["Source Path", "Upload Progress", "Status", "Controls"];
const UT_PATH_COLUMN      = 0;
const UT_PROGRESS_COLUMN  = 1;
const UT_STATUS_COLUMN    = 2;
const UT_BUTTON_COLUMN    = 3;



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
        let stateelement = this._CreateStateElement(state);

        //// Control buttons
        // TODO: Pause/Continue
        //let importbutton = new SVGButton("Remove", ()=>{this.onRemove();}, "Delete this uploaded file");
        //let buttonbox    = new ButtonBox()
        //buttonbox.AddButton(importbutton);

        // Update progress
        let progress = Math.round((offset / filesize) * 100);
        this.progressbar.SetProgress(progress);

        // Set cells
        this.SetContent(UT_PATH_COLUMN,     pathelement);
        this.SetContent(UT_PROGRESS_COLUMN, this.progressbar.GetHTMLElement());
        this.SetContent(UT_STATUS_COLUMN,   stateelement.GetHTMLElement());
        //this.SetContent(UT_BUTTON_COLUMN, buttonbox.GetHTMLElement());
    }



    _CreateStateElement(state)
    {
        return new UploadStatusText(state);
    }



    onRemove()
    {
        event.preventDefault();
        event.stopPropagation();
        //MusicDB_Request("DeleteTag", "UpdateTags", {tagid: MDBMood.id}, {origin: "MoodSettings"});
        window.console && console.log("Remove Upload");
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

        this.entries       = new Object();
        this.hascontextrow = false;
    }



    Clear()
    {
        super.Clear();
        this.AddRow(this.headline);
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
            this.RemoveRow(tablerow, this.hascontextrow); // Remove row including context row
            delete this.entries[key];
        }
        else
        {
            // Update the row and, if available, the controls form
            this.entries[key].row.Update(upload);
            this.entries[key].form?.UpdateUploadTask(upload);
            this.entries[key].form?.ValidateForm();
        }
        // TODO: Update annotations
    }



    CreateNewRow(upload)
    {
        // Create row showing the uploaded file
        let  newrow = new UploadTableRow(upload);
        this.AddRow(newrow);

        // Check/define meta information about the file
        let artistname = "Unknown Artist"; // TODO
        let sourcefile = upload.sourcefilename;
        let extindex   = sourcefile.lastIndexOf(".")
        let musicname  = sourcefile.slice(0, extindex);
        let origin     = "Internet";
        let release    = 2000;
        if("annotations" in upload)
        {
            let annotations = upload.annotations;
            if("artistname" in annotations)
                artistname = annotations.artistname;
            if("name" in annotations)
                musicname = annotations.name;
            if("origin" in annotations)
                origin = annotations.origin;
            if("release" in annotations)
                release = annotations.release;
        }

        // Create import form
        let importform = null;
        switch(upload.contenttype)
        {
            case "video":
                importform = new VideoImportForm(artistname, musicname, origin, release, upload);
                break;
        }

        if(importform != null)
        {
            this.hascontextrow = true;
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

