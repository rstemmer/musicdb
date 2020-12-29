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


const VIDEOIMPORTTABLEHEADLINE = ["Artist Name", "Release", "Video Name", "Full Path", "Controls"];
const VIT_ARTIST_COLUMN     = 0;
const VIT_RELEASE_COLUMN    = 1;
const VIT_NAME_COLUMN       = 2;
const VIT_PATH_COLUMN       = 3;
const VIT_BUTTON_COLUMN     = 4;


class VideoImportTableRowBase extends TableRow
{
    constructor()
    {
        super(VIDEOIMPORTTABLEHEADLINE.length, ["VideoImportTableRow"]); // Row with n cells
    }
}


class VideoImportTableHeadline extends VideoImportTableRowBase
{
    constructor(MDBMood)
    {
        super();
        for(let cellnum in VIDEOIMPORTTABLEHEADLINE)
        {
            let headline = document.createTextNode(VIDEOIMPORTTABLEHEADLINE[cellnum]);
            this.SetContent(cellnum, headline);
        }
    }
}



class VideoImportTableRow extends VideoImportTableRowBase
{
    constructor(videopath)
    {
        super();
        this.Update(videopath)
    }



    Update(videopath)
    {
        // Get all data
        let artistname;
        let videoname;
        let release;

        // Create cells
        let  artistelement = document.createTextNode(artistname);
        this.releaseinput  = document.createElement("input");
        this.releaseinput.oninput   = ()=>{onReleaseInput();};
        this.releaseinput.type      = "number";
        this.releaseinput.value     = release;
        this.nameinput     = document.createElement("input");
        this.nameinput.oninput  = ()=>{onNameInput();};
        this.nameinput.type     = "text";
        this.nameinput.value    = videoname;
        let  pathelement      = document.createTextNode(videopath);

        // Control buttons
        let importbutton = new SVGButton("Save", ()=>{this.onImport();});
        let buttonbox    = new ButtonBox()
        buttonbox.AddButton(importbutton);

        // Set cells
        this.SetContent(VIT_ARTIST_COLUMN,    artistelement);
        this.SetContent(VIT_RELEASE_COLUMN,   this.releaseinput);
        this.SetContent(VIT_NAME_COLUMN,      this.nameinput);
        this.SetContent(VIT_PATH_COLUMN,      pathelement);
        this.SetContent(VIT_BUTTON_COLUMN,    buttonbox.GetHTMLElement());
    }



    onReleaseInput()
    {
    }
    onNameInput()
    {
    }


    onImport()
    {
        //MusicDB_Request("DeleteTag", "UpdateTags", {tagid: MDBMood.id}, {origin: "MoodSettings"});
    }
}




class VideoImportTable extends Table
{
    constructor(videopaths)
    {
        super(["MoodsTable"]);
        this.headline   = new VideoImportTableHeadline();
        this.videopaths = null;
        this.Update(videopaths);
    }



    Update(videopaths)
    {
        this.Clear();
        this.AddRow(this.headline);

        if(typeof videopaths !== "object" || videopaths === null)
            return;

        this.videopaths = videopaths;

        let maxposx = 0;
        for(let videopath of this.videopaths)
        {
            this.AddRow(new VideoImportTableRow(videopath));
        }

        return;
    }

}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

