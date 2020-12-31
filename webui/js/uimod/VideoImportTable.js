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


const VIDEOIMPORTTABLEHEADLINE = ["Artist Name", "Release", "Video Name", "Source Path", "Controls"];
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
    constructor(video)
    {
        super();
        this.Update(video)
    }



    Update(video)
    {
        // Get all data
        let artistname = video.artistname;
        let videoname  = video.videoname;
        let release    = video.release;
        let videopath  = video.path;

        // Create cells
        let artistelement = document.createTextNode(artistname);
        let releaseinput  = new NumberInput(()=>{this.onReleaseInput();}, release);
        let nameinput     = new TextInput(()=>{this.onNameInput();}, videoname);
        let pathelement   = document.createTextNode(videopath);

        // Control buttons
        let importbutton = new SVGButton("Save", ()=>{this.onImport();});
        let buttonbox    = new ButtonBox()
        buttonbox.AddButton(importbutton);

        // Set cells
        this.SetContent(VIT_ARTIST_COLUMN,  artistelement);
        this.SetContent(VIT_RELEASE_COLUMN, releaseinput.GetHTMLElement());
        this.SetContent(VIT_NAME_COLUMN,    nameinput.GetHTMLElement());
        this.SetContent(VIT_PATH_COLUMN,    pathelement);
        this.SetContent(VIT_BUTTON_COLUMN,  buttonbox.GetHTMLElement());
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
        window.console && console.log("Import Video");
    }
}



class VideoImportTable extends Table
{
    constructor(videos=null)
    {
        super(["VideoImportTable"]);
        this.headline = new VideoImportTableHeadline();
        this.videos   = null;
        this.Update(videos);
    }



    Update(videos)
    {
        this.Clear();
        this.AddRow(this.headline);

        if(typeof videos !== "object" || videos === null)
            return;

        this.videos = videos;

        for(let video of this.videos)
        {
            this.AddRow(new VideoImportTableRow(video));
        }

        return;
    }

}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

