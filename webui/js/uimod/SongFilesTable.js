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

const SONGFILESTABLEHEADLINE = ["CD", "Song Nr.", "Song Name", "New Path"];
const SFT_CDNUMBER_COLUMN   = 0;
const SFT_SONGNUMBER_COLUMN = 1;
const SFT_SONGNAME_COLUMN   = 2;
const SFT_NEWPATH_COLUMN    = 3;



class SongFilesTableRowBase extends TableRow
{
    constructor()
    {
        super(SONGFILESTABLEHEADLINE.length, ["SongFilesTableRow"]);
    }



    SetContent(cellnum, element)
    {
        let htmlelement = element.GetHTMLElement();
        super.SetContent(cellnum, htmlelement);
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
    constructor(fileinfos)
    {
        super();

        this.fileinfos = fileinfos

        this.cdnumberinput   = new NumberInput((value)=>{return this.ValidateCDNumber(value); });
        this.songnumberinput = new NumberInput((value)=>{return this.ValidateSongNumber(value); });
        this.songnameinput   = new TextInput(  (value)=>{return this.ValidateSongName(value);  });
        this.newpathelement  = new Element("span");

        this.cdnumberinput.SetValue(  this.fileinfos.cdnumber);
        this.songnumberinput.SetValue(this.fileinfos.songnumber);
        this.songnameinput.SetValue(  this.fileinfos.songname);

        this.SetContent(SFT_CDNUMBER_COLUMN,   this.cdnumberinput);
        this.SetContent(SFT_SONGNUMBER_COLUMN, this.songnumberinput);
        this.SetContent(SFT_SONGNAME_COLUMN,   this.songnameinput);
        this.SetContent(SFT_NEWPATH_COLUMN,    this.newpathelement);
    }



    ValidateCDNumber(value)
    {
        if(value < 1 && value > 100)
            return false;
        return true;
    }
    ValidateSongNumber(value)
    {
        if(value < 1 && value > 1000)
            return false;
        return true;
    }
    ValidateSongName(value)
    {
        if(value.length <= 0)
            return false;
        return true;
    }
}



class SongFilesTable extends Table
{
    constructor()
    {
        super(["SongFilesTable"]);


        // Table
        this.headlinerow = new SongFilesTableHeadline();
        this.AddRow(this.headlinerow);
    }



    Update(files)
    {
        this.Clear();
        this.AddRow(this.headlinerow);
        for(let file of files)
        {
            this.AddRow(new SongFilesTableRow(file));
        }
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

