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

const SONGFILESTABLEHEADLINE = ["CD", "Song Nr.", "Song Name", "New File Name"];
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
    constructor(fileinfos, maxcds)
    {
        super();

        this.fileinfos   = fileinfos;
        this.oldfilename = this.fileinfos.path.split("/").slice(-1)[0];
        this.maxcds      = maxcds;

        this.cdnumberinput   = new NumberInput();
        this.songnumberinput = new NumberInput();
        this.songnameinput   = new TextInput();
        let  newpathcontainer= new Element("div", ["songfilepath", "flex-middle"]);
        let  songfileicon    = new SVGIcon("SongFile");
        this.newpathelement  = new Element("span");
        newpathcontainer.AppendChild(songfileicon);
        newpathcontainer.AppendChild(this.newpathelement);

        this.cdnumberinput.SetValidateEventCallback(  (value)=>{return this.ValidateCDNumber(value);  });
        this.songnumberinput.SetValidateEventCallback((value)=>{return this.ValidateSongNumber(value);});
        this.songnameinput.SetValidateEventCallback(  (value)=>{return this.ValidateSongName(value);  });
        this.cdnumberinput.SetAfterValidateEventCallback(  (value, valid)=>{return this.EvaluateNewPath();});
        this.songnumberinput.SetAfterValidateEventCallback((value, valid)=>{return this.EvaluateNewPath();});
        this.songnameinput.SetAfterValidateEventCallback(  (value, valid)=>{return this.EvaluateNewPath();});

        // If there is just one CD, no CD number should be given
        if(this.maxcds == 1)
        {
            this.fileinfos.cdnumber = "";
            this.cdnumberinput.SetEnabled(false);
        }

        this.cdnumberinput.SetValue(  this.fileinfos.cdnumber);
        this.songnumberinput.SetValue(this.fileinfos.songnumber);
        this.songnameinput.SetValue(  this.fileinfos.songname);

        this.SetContent(SFT_CDNUMBER_COLUMN,   this.cdnumberinput);
        this.SetContent(SFT_SONGNUMBER_COLUMN, this.songnumberinput);
        this.SetContent(SFT_SONGNAME_COLUMN,   this.songnameinput);
        this.SetContent(SFT_NEWPATH_COLUMN,    newpathcontainer);
    }



    EvaluateNewPath()
    {
        const validspan = `<span style="color: var(--color-brightgreen)">`;
        const errorspan = `<span style="color: var(--color-brightred)">`;
        const grayspan  = `<span style="color: var(--color-gray)">`;
        const closespan = `</span>`;

        let newpathtext = "";
        let newpathhtml = "";

        // First part is the optional CD number
        if(this.maxcds > 1)
        {
            let cdnum = this.cdnumberinput.GetValue();
            if(this.cdnumberinput.GetValidState() === true)
                newpathhtml += validspan;
            else
                newpathhtml += errorspan;

            newpathtext += `${cdnum} - `;
            newpathhtml += `${cdnum} - ${closespan}`;
        }

        // Next the song number
        let songnum = this.songnumberinput.GetValue();
        if(this.songnumberinput.GetValidState() === true)
            newpathhtml += validspan;
        else
            newpathhtml += errorspan;

        if(songnum.length == 0)
            songnum = `??`;
        if(songnum.length == 1)
            songnum = `0${songnum}`;

        newpathtext += `${songnum} `;
        newpathhtml += `${songnum} ${closespan}`;

        // Next comes song name
        let songname = this.songnameinput.GetValue();
        songname.replace(" / ", " ∕ "/*division slash*/);
        if(this.songnameinput.GetValidState() === true)
            newpathhtml += validspan;
        else
            newpathhtml += errorspan;

        newpathtext += `${songname}`;
        newpathhtml += `${songname}${closespan}`;

        // Last is the extension
        let fileextension = this.fileinfos.path.split(".").slice(-1)[0];
        newpathtext += `.${fileextension}`;
        newpathhtml += `${grayspan}.${fileextension}${closespan}`;

        // Show old file name if the new one is different
        if(this.oldfilename != newpathtext)
            newpathhtml = `${errorspan}${this.oldfilename}${closespan}${grayspan} ➜ ${newpathhtml}${closespan}`;

        this.newpathelement.RemoveChilds();
        this.newpathelement.SetInnerHTML(newpathhtml);
        return newpathtext;
    }



    ValidateCDNumber(value)
    {
        if(value.length == 0 && this.maxcds > 1)
            return false;
        if(this.maxcds == 1 && value.length > 0)
            return false;

        value = parseInt(value, 10);
        if(value < 1 || value > this.maxcds)
            return false;
        return true;
    }
    ValidateSongNumber(value)
    {
        if(value.length == 0)
            return false;

        value = parseInt(value, 10);
        if(value < 1 || value > 1000)
            return false;
        return true;
    }
    ValidateSongName(value)
    {
        if(value.length == 0)
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
        // Sort
        files.sort((a,b)=>{return a.songnumber - b.songnumber;});

        // Get max CDs
        let allcdnumbers = files.map(a => a.cdnumber);
        let maxcds       = Math.max(...allcdnumbers);

        // Create new table
        this.Clear();
        this.AddRow(this.headlinerow);
        for(let file of files)
        {
            this.AddRow(new SongFilesTableRow(file, maxcds));
        }
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

