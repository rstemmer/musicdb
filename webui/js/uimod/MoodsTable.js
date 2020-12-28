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
        let numvideos   = null;
        if(typeof stats === "object")
        {
            numsongs    = stats["songs"];
            numvideos   = stats["videos"];
        }
        let usagetext = "";
        if(typeof numsongs  === "number" && numsongs  > 0) usagetext += `<span>${numsongs } Songs</span>`;
        if(typeof numvideos === "number" && numvideos > 0) usagetext += `<span>${numvideos} Videos</span>`;
        if(usagetext == "") usagetext = "<span class=\"hlcolor\">This tag is not used yet</span>"
        let usageelement = document.createElement("div");
        usageelement.innerHTML = usagetext;

        let removebutton = new SVGButton("Remove", ()=>{this.onDeleteMood(MDBMood);});
        let numdependencies = numsongs + numvideos;
        if(numdependencies > 0)
        {
            removebutton.SetColor("var(--color-red)");
            removebutton.GetHTMLElement().classList.add("hovpacity");
            removebutton.SetTooltip("Delete Mood-Flag and remove Flag from all songs, albums and videos");
        }
        else
        {
            removebutton.SetTooltip("Delete Mood-Flag");
        }

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
                icon.SetTooltip("Click so see appearance when flag is Set/Reset");
                icon.SetSelectionState(true);

                typename = "Unicode"
                break;
            default:
                window.console && console.error(`Unsupported mood icon type ${icontype}!`);
        }

        let colorstatebutton;
        let colorelement;
        if(color === null)
        {
            colorstatebutton = new SVGButton("Unchecked",    ()=>{this.onAddColor(MDBMood);});
            colorstatebutton.SetTooltip("Give this mood a fixed color");
            colorelement = document.createElement("span");
            colorelement.innerText = "No Color";
            colorelement.classList.add("hlcolor");
        }
        else
        {
            colorstatebutton = new SVGButton("Checked", ()=>{this.onRemoveColor(MDBMood);});
            colorstatebutton.SetTooltip("Remove color from mood so that is adopedt to the color scheme");
            let colorinput   = new ColorInput(null /*no label*/, "Change Flag-Color", color,
                ()=>{this.onChangeColor(MDBMood);},
                ()=>{this.onPreviewColor(MDBMood);}
                );
            colorelement = colorinput.GetHTMLElement();
            //colorelement = document.createElement("span");
            //colorelement.innerText   = color;
            //colorelement.style.color = color;
            icon.GetHTMLElement().style.color = color;
        }

        this.SetContent(ICON_COLUMN    , icon.GetHTMLElement());
        this.SetContent(ICONTYPE_COLUMN, document.createTextNode(typename));
        this.SetContent(MOODNAME_COLUMN, document.createTextNode(name));
        this.SetContent(HASCOLOR_COLUMN, colorstatebutton.GetHTMLElement());
        this.SetContent(COLOR_COLUMN   , colorelement); // TODO: Color-Button
        this.SetContent(USAGE_COLUMN   , usageelement);
        this.SetContent(DELETE_COLUMN  , removebutton.GetHTMLElement());
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


    onChangeColor(MDBMood)
    {
        window.console && console.log(`Change color from ${MDBMood.name}`);
    }


    onPreviewColor(MDBMood)
    {
        window.console && console.log(`Preview color from ${MDBMood.name}`);
    }
}



class MoodsTableEditRow extends MoodsTableRowBase
{
    constructor(MDBMood)
    {
        super();
        this.iconinput        = document.createElement("input");
        this.iconinput.style.color = "var(--hlcolor)";
        this.nameinput        = document.createElement("input");
        this.colorinput       = new ColorInput(null /*no label*/, "Change Flag-Color", "#FFFFFF",
            ()=>{this.onPreviewColor();},
            ()=>{this.onPreviewColor();}
            );
        this.colorstatebutton = new SVGCheckBox((newstate)=>{this.onToggleColor(newstate);});
        this.colorstatebutton.SetTooltip("Give this mood a fixed color");
        this.confirmbutton    = new SVGButton("Save", ()=>{this.onSave();});
        this.confirmbutton.SetTooltip("Create new Flag with the given attributes");

        this.iconinput.oninput = ()=>{this.Validate();}
        this.nameinput.oninput = ()=>{this.Validate();}
        this.Validate();

        if(typeof MDBMood === "object" && MDBMood != null)
        {
            // Initialize everything
            this.iconinput.value = MDBMood.icon;
            this.nameinput.value = MDBMood.name;
            this.colorinput.SetColor(MDBMood.color);
            this.posx            = MDBMood.posx;
            this.posy            = MDBMood.posy;
        }
        else
        {
            this.posx = 0;
            this.posy = 0;
        }

        this.SetContent(ICON_COLUMN    , this.iconinput); 
        this.SetContent(ICONTYPE_COLUMN, document.createTextNode("Unicode"));
        this.SetContent(MOODNAME_COLUMN, this.nameinput);
        this.SetContent(HASCOLOR_COLUMN, this.colorstatebutton.GetHTMLElement());
        this.SetContent(COLOR_COLUMN   , document.createTextNode("No Color")); // TODO: Color-Button
        this.SetContent(USAGE_COLUMN   , document.createTextNode("This Flag does not exists yet"));
        this.SetContent(DELETE_COLUMN  , this.confirmbutton.GetHTMLElement());
    }



    SetMoodPosition(posx, posy)
    {
        if(typeof posx === "number")
            this.posx = posx;
        if(typeof posy === "number")
            this.posy = posy;
        return;
    }



    Validate()
    {
        let valid = true;
        if(this.ValidateIcon() !== true)
            valid = false;
        if(this.ValidateName() !== true)
            valid = false;

        if(valid === true)
            this.confirmbutton.Show();
        else
            this.confirmbutton.Hide();
    }

    ValidateIcon()
    {
        let icon  = this.iconinput.value;
        let valid = false;
        if(typeof icon === "string" && icon.length == 1)
            valid = true;

        this.iconinput.dataset.valid = valid;
        return valid;
    }
    ValidateName()
    {
        let name  = this.nameinput.value;
        let valid = false;
        if(typeof name === "string" && name.length > 0)
            valid = true;
        // TODO: Check if name already exists

        this.nameinput.dataset.valid = valid;
        return valid;
    }



    onToggleColor(newstate)
    {
        window.console && console.log(`New color state: ${newstate}`);
        if(newstate == false)
        {
            this.SetContent(COLOR_COLUMN, document.createTextNode("No Color"));
            this.iconinput.style.color = "var(--hlcolor)";
            return;
        }

        // Color enabled
        this.SetContent(COLOR_COLUMN, this.colorinput.GetHTMLElement());
        this.onPreviewColor();
        return;
    }
    onPreviewColor()
    {
        let color = this.colorinput.GetColor();
        this.iconinput.style.color = color;
        return;
    }



    onSave()
    {
        let name  = this.nameinput.value;
        let icon  = this.iconinput.value;
        let color = null;
        let posx  = this.posx;
        let posy  = this.posy;

        if(this.colorstatebutton.GetSelectionState())
            color = this.colorinput.GetColor();

        window.console && console.log(`AddMoodFlag(${name}, ${icon}, ${color}, ${posx}, ${posy});`)
        MusicDB_Call("AddMoodFlag", {name: name, icon: icon, color: color, posx: posx, posy: posy});
    }
}



class MoodsTable extends Table
{
    constructor(MDBMoods)
    {
        super(["MoodsTable"]);
        this.headline = new MoodsTableHeadline();
        this.editrow  = new MoodsTableEditRow();
        this.Update(MDBMoods);
    }



    // MDBMoods is allowed to be [] -> List will be emptied
    // MDBMoodStats is allowed to be {} -> No stats will be shown
    Update(MDBMoods, MDBMoodStats)
    {
        this.Clear();
        this.AddRow(this.headline);

        if(typeof MDBMoods !== "object" || MDBMoods === null)
            return;

        let maxposx = 0;
        for(let MDBMood of MDBMoods)
        {
            let moodid = MDBMood.id;
            let posx   = MDBMood.posx;
            let stats  = MDBMoodStats[moodid];
            this.AddRow(new MoodsTableRow(MDBMood, stats));

            if(maxposx < posx)
                maxposx = posx;
        }

        this.editrow.SetMoodPosition(maxposx+1, 0);
        this.AddRow(this.editrow);
        return;
    }
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

