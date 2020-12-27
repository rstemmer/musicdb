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


const MOODTABLEHEADLINE = ["Icon", "Icon Type", "Mood Name", "Own Color", "Mood Color", "Usage", "Delete"];
const ICON_COLUMN       = 0;
const ICONTYPE_COLUMN   = 1;
const MOODNAME_COLUMN   = 2;
const HASCOLOR_COLUMN   = 3;
const COLOR_COLUMN      = 4;
const USAGE_COLUMN      = 5;
const DELETE_COLUMN     = 6;


class MoodsTableRowBase extends TableRow
{
    constructor()
    {
        super(MOODTABLEHEADLINE.length, ["MoodsTableRow"]); // Row with n cells
    }
}


class MoodsTableHeadline extends MoodsTableRowBase
{
    constructor(MDBMood)
    {
        super();
        for(let cellnum in MOODTABLEHEADLINE)
        {
            let headline = document.createTextNode(MOODTABLEHEADLINE[cellnum]);
            this.SetContent(cellnum, headline);
        }
    }
}



class MoodsTableRow extends MoodsTableRowBase
{
    constructor(MDBMood, MDBTagStats)
    {
        super();
        this.Update(MDBMood, MDBTagStats);
    }



    Update(MDBMood, stats)
    {
        let numsongs    = null;
        let numalbums   = null;
        let numvideos   = null;
        if(typeof stats === "object")
        {
            numsongs    = stats["songs"];
            numalbums   = stats["albums"];
            numvideos   = stats["videos"];
        }
        let usagetext = "";
        if(typeof numsongs  === "number" && numsongs  > 0) usagetext += `<span>${numsongs } Songs</span>`;
        if(typeof numalbums === "number" && numalbums > 0) usagetext += `<span>${numalbums} Albums</span>`;
        if(typeof numvideos === "number" && numvideos > 0) usagetext += `<span>${numvideos} Videos</span>`;
        if(usagetext == "") usagetext = "<span>This tag is not used yet</span>"
        let usageelement = document.createElement("div");
        usageelement.innerHTML = usagetext;
        let numdependencies     = numsongs + numalbums + numvideos;

        let name    = MDBMood.name;
        let moodid  = MDBMood.id;
        let icontype= MDBMood.icontype;
        let color   = MDBMood.color
            /*
             * mood.icontype:
             *      1: Unicode Character
             *      2: HTML code
             *      3: png \_ not yet specified in detail
             *      4: svg /
             *
             * mood.color: HTML color code or null
             */

        let icon;
        let typename;
        switch(MDBMood.icontype)
        {
            case 1: // Unicode Character
                icon = new UnicodeToggleButton(MDBMood.icon, null); // no click handler
                icon.SetTooltip(MDBMood.name);

                typename = "Unicode"
                break;
            default:
                window.console && console.error(`Unsupported mood icon type ${icontype}!`);
        }

        let colorstatebutton;
        if(color === null)
        {
            colorstatebutton = new SVGButton("Unchecked",    ()=>{this.onAddColor(MDBMood);});
            colorstatebutton.SetTooltip("Give this mood a fixed color");
        }
        else
        {
            colorstatebutton = new SVGButton("Checked", ()=>{this.onRemoveColor(MDBMood);});
            colorstatebutton.SetTooltip("Remove color from mood so that is adopedt to the color scheme");
        }

        this.SetContent(ICON_COLUMN    , icon.GetHTMLElement());
        this.SetContent(ICONTYPE_COLUMN, document.createTextNode(typename));
        this.SetContent(MOODNAME_COLUMN, document.createTextNode(name));
        this.SetContent(HASCOLOR_COLUMN, colorstatebutton.GetHTMLElement());
        this.SetContent(COLOR_COLUMN   , document.createTextNode(color)); // TODO: Color-Button
        this.SetContent(USAGE_COLUMN   , usageelement);
        this.SetContent(DELETE_COLUMN  , new SVGButton("Remove", ()=>{this.onDeleteMood(MDBMood);}).GetHTMLElement());
    }



    onDeleteMood(MDBMood)
    {
        window.console && console.log(`Delete ${MDBMood.name}`);
    }


    onAddColor(MDBMood)
    {
        window.console && console.log(`Add color to ${MDBMood.name}`);
    }


    onRemoveColor(MDBMood)
    {
        window.console && console.log(`Remove color from ${MDBMood.name}`);
    }
}



class MoodsTable extends Table
{
    constructor(MDBMoods)
    {
        super(["MoodsTable"]);
        this.headline = new MoodsTableHeadline();
        this.Update(MDBMoods);
    }



    // MDBMoods is allowed to be [] -> List will be emptied
    // MDBMoodStats is allowed to be {} -> No stats will be shown
    Update(MDBMoods, MDBMoodStats)
    {
        this.Clear();
        this.AddRow(this.headline);

        if(typeof MDBMoods !== "object")
            return;

        for(let MDBMood of MDBMoods)
        {
            let moodid = MDBMood.id;
            let stats  = MDBMoodStats[moodid];
            this.AddRow(new MoodsTableRow(MDBMood, stats));
        }
        return;
    }
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

