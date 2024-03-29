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


const MOODTABLEHEADLINE = ["Icon", "Icon Type", "Mood Name", "Own Color", "Mood Color", "Usage", "Controls"];
const ICON_COLUMN       = 0;
const ICONTYPE_COLUMN   = 1;
const MOODNAME_COLUMN   = 2;
const HASCOLOR_COLUMN   = 3;
const COLOR_COLUMN      = 4;
const USAGE_COLUMN      = 5;
const BUTTON_COLUMN     = 6;


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
        this.AddCSSClass("TableHeadline");
        for(let cellnum in MOODTABLEHEADLINE)
        {
            let headline = document.createTextNode(MOODTABLEHEADLINE[cellnum]);
            this.SetContent(cellnum, headline);
        }
    }
}



class MoodsTableRow extends MoodsTableRowBase
{
    constructor(MDBMood, MDBTagStats, onmovemood)
    {
        super();
        this.onmovemood = onmovemood;
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

        let editbutton   = new SVGButton("Edit",   ()=>{this.onEdit(MDBMood);});
        editbutton.SetTooltip("Edit this Mood-Flag entry");

        let numdependencies = numsongs + numvideos;
        this.confirmmessage = new MessageBarConfirmDelete(
		`Do you want to delete all ${numdependencies} associations to the "${MDBMood.name}" Flag?<br>Enter "${numdependencies}" and confirm with <i>Enter</i>`,
		`${numdependencies}`, ()=>{this.onDelete(MDBMood);});
        let removebutton    = new SVGButton("Remove", ()=>{this.onDelete(MDBMood, numdependencies);});
        if(numdependencies > 0)
        {
            removebutton.SetColor("var(--color-brightred)");
            removebutton.AddCSSClass("hovepacity");
            removebutton.SetTooltip("Delete Mood-Flag and remove Flag from all songs, albums and videos");
        }
        else
        {
            removebutton.SetTooltip("Delete Mood-Flag");
        }

        let moveleftbutton  = new SVGButton("MoveLeft",  ()=>{this.onMove(MDBMood, "left");});
        let moverightbutton = new SVGButton("MoveRight", ()=>{this.onMove(MDBMood, "right");});
        let posyswitch      = new SVGSwitch("MoveToBottomRow", "MoveToTopRow", (state)=>
            {
                if(state=="a")
                    this.onMove(MDBMood, "up");
                else
                    this.onMove(MDBMood, "down");
            });

        if(MDBMood.posy === 1)
        {
            posyswitch.SetSelectionState("b");
        }
        posyswitch.SetTooltip("Switch between top and bottom row");
        if(MDBMood.posx === 0)
        {
            moveleftbutton.Disable();
            moveleftbutton.SetTooltip("Icon already on the very left");
        }
        else
        {
            moveleftbutton.SetTooltip("Move icon to the left");
        }
        moverightbutton.SetTooltip("Move icon to the right");

        let buttonbox = new ButtonBox()
        buttonbox.AddButton(moveleftbutton);
        buttonbox.AddButton(moverightbutton);
        buttonbox.AddButton(posyswitch);
        buttonbox.AddButton(editbutton);
        buttonbox.AddButton(removebutton);

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

        let colorstateicon;
        let colorelement;
        if(color === null)
        {
            colorstateicon = new SVGIcon("StatusBad");
            colorelement   = new Element("span", ["hlcolor"]);
            colorelement.SetInnerText("No Color");
        }
        else
        {
            colorstateicon = new SVGIcon("StatusGood");
            colorelement   = new Element("span");
            colorelement.SetInnerText(color.toUpperCase());

            colorelement.SetColor(color);
            colorstateicon.SetColor(color);
            icon.SetColor(color);
        }

        let controls = new Element("div", ["flex-column"]);
        controls.AppendChild(buttonbox);
        controls.AppendChild(this.confirmmessage);

        this.SetContent(ICON_COLUMN    , icon);
        this.SetContent(ICONTYPE_COLUMN, document.createTextNode(typename));
        this.SetContent(MOODNAME_COLUMN, document.createTextNode(name));
        this.SetContent(HASCOLOR_COLUMN, colorstateicon);
        this.SetContent(COLOR_COLUMN   , colorelement);
        this.SetContent(USAGE_COLUMN   , usageelement);
        this.SetContent(BUTTON_COLUMN  , controls);
    }



    onMove(MDBMood, direction)
    {
        if(typeof this.onmovemood === "function")
            this.onmovemood(MDBMood, direction);
    }



    onDelete(MDBMood, numdependencies=0)
    {
        // Ask for confirmation
        if(numdependencies > 0)
        {
            this.confirmmessage.Show();
            return;
        }

        // Delete
        MusicDB.Request("DeleteTag", "UpdateTags", {tagid: MDBMood.id}, {origin: "MoodSettings"});
        return;
    }

    onEdit(MDBMood)
    {
        // Replace this Row with an Edit-Row
        let editrow = new MoodsTableEditRow(MDBMood);
        this.ReplaceWith(editrow);
    }
}



class MoodsTableEditRow extends MoodsTableRowBase
{
    constructor(MDBMood)
    {
        super();
        this.iconinput  = new TextInput(()=>{this.Validate();}, "", "Set a singe Unicode Icon");
        this.iconinput.SetColor("var(--hlcolor)");
        this.nameinput  = new TextInput(()=>{this.Validate();}, "", "Provide a desriptive Name");
        this.colorinput = new ColorInput(null /*no label*/, "Change Flag-Color", "#FFFFFF",
            ()=>{this.onPreviewColor();},
            ()=>{this.onPreviewColor();}
            );
        this.colorstatebutton = new SVGCheckBox((newstate)=>{this.onToggleColor(newstate);});
        this.colorstatebutton.SetTooltip("Give this mood a fixed color");
        this.confirmbutton    = new SVGButton("Save", ()=>{this.onSave();});
        this.confirmbutton.SetTooltip("Create new Flag with the given attributes");

        if(typeof MDBMood === "object" && MDBMood != null)
        {
            // Initialize everything
            this.iconinput.SetValue(MDBMood.icon);
            this.nameinput.SetValue(MDBMood.name);
            this.posx             = MDBMood.posx;
            this.posy             = MDBMood.posy;
            this.mood             = MDBMood;
            if(typeof MDBMood.color === "string")
            {
                this.colorinput.SetColor(MDBMood.color);
                this.colorstatebutton.SetSelectionState(true);
                this.SetContent(COLOR_COLUMN, this.colorinput.GetHTMLElement());
            }
            else
            {
                this.SetContent(COLOR_COLUMN, document.createTextNode("No Color"));
            }
        }
        else
        {
            this.posx = 0;
            this.posy = 0;
            this.SetContent(COLOR_COLUMN, document.createTextNode("No Color"));
            this.mood = null;
        }

        this.Validate();

        this.SetContent(ICON_COLUMN    , this.iconinput); 
        this.SetContent(ICONTYPE_COLUMN, document.createTextNode("Unicode"));
        this.SetContent(MOODNAME_COLUMN, this.nameinput);
        this.SetContent(HASCOLOR_COLUMN, this.colorstatebutton);
        this.SetContent(USAGE_COLUMN   , document.createTextNode("This Flag does not exists yet"));
        this.SetContent(BUTTON_COLUMN  , this.confirmbutton);
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
        // During early initialization validation, some objects may not exist
        // Only validate when all required objects exist
        if(typeof this.iconinput !== "object")
            return;
        if(typeof this.nameinput !== "object")
            return;
        if(typeof this.confirmbutton !== "object")
            return;

        let valid = true;
        if(this.ValidateIcon() !== true)
            valid = false;
        if(this.ValidateName() !== true)
            valid = false;

        if(valid === true)
        {
            this.confirmbutton.Enable();
            this.confirmbutton.SetTooltip("Create new Flag with the given attributes");
        }
        else
        {
            this.confirmbutton.Disable();
            this.confirmbutton.SetTooltip("Set an unicode icon and define a name to create a new Mood-Flag");
        }

        return;
    }

    ValidateIcon()
    {
        let icon  = this.iconinput.GetValue();
        let valid = false;
        if(typeof icon === "string" && icon.length == 1)
            valid = true;

        this.iconinput.SetValidState(valid);
        return valid;
    }
    ValidateName()
    {
        let name  = this.nameinput.GetValue();
        let valid = false;
        if(typeof name === "string" && name.length > 0)
            valid = true;
        // TODO: Check if name already exists

        this.nameinput.SetValidState(valid);
        return valid;
    }



    onToggleColor(newstate)
    {
        if(newstate == false)
        {
            this.SetContent(COLOR_COLUMN, document.createTextNode("No Color"));
            this.iconinput.SetColor("var(--hlcolor)");
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
        this.iconinput.SetColor(color);
        return;
    }



    onSave()
    {
        // Get all data
        let name  = this.nameinput.GetValue();
        let icon  = this.iconinput.GetValue();
        let color = null;
        let posx  = this.posx;
        let posy  = this.posy;

        if(this.colorstatebutton.GetSelectionState())
            color = this.colorinput.GetColor();

        // If mood does not exist, create one.
        // Otherwise just updated changes
        if(this.mood == null)
        {
            MusicDB.Request("AddMoodFlag", "UpdateTags", {name: name, icon: icon, color: color, posx: posx, posy: posy}, {origin: "MoodSettings"});
        }
        else
        {
            let tagid = this.mood.id;

            if(name != this.mood.name)
                MusicDB.Call("ModifyTag", {tagid: tagid, attribute: "name", value: name});
            if(icon != this.mood.icon)
                MusicDB.Call("ModifyTag", {tagid: tagid, attribute: "icon", value: icon});
            if(color != this.mood.color)
                MusicDB.Call("ModifyTag", {tagid: tagid, attribute: "color", value: color});
            MusicDB.Request("GetTags", "UpdateTags", {}, {origin: "MoodSettings"});
        }

        // Clear inputs for new data
        this.posx += 1;
        this.iconinput.SetValue("");
        this.nameinput.SetValue("");
        this.colorinput.SetColor("#ffffff");
        this.colorstatebutton.SetSelectionState(false);
        this.Validate();
        return;
    }
}



class MoodsTable extends Table
{
    constructor(MDBMoods)
    {
        super(["MoodsTable"]);
        this.headline = new MoodsTableHeadline();
        this.editrow  = new MoodsTableEditRow();
        this.moods    = null;
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

        this.moods = MDBMoods;

        let maxposx = 0;
        for(let MDBMood of MDBMoods)
        {
            let moodid = MDBMood.id;
            let posx   = MDBMood.posx;
            let stats  = MDBMoodStats[moodid];
            this.AddRow(new MoodsTableRow(MDBMood, stats, (mood, direction)=>{this.onMoveMood(mood, direction);}));

            if(maxposx < posx)
                maxposx = posx;
        }

        this.editrow.SetMoodPosition(maxposx+1, 0);
        this.AddRow(this.editrow);
        return;
    }



    onMoveMood(MDBMood, direction)
    {
        let neighbour;
        switch(direction)
        {
            case "left":
                neighbour = this.MoveIconLeft(MDBMood);
                break;
            case "right":
                neighbour = this.MoveIconRight(MDBMood);
                break;
            case "up":
                neighbour = this.MoveIconUp(MDBMood);
                break;
            case "down":
                neighbour = this.MoveIconDown(MDBMood);
                break;
            default:
                return;
        }

        if(direction == "left" || direction == "right") // update posx
        {
            MusicDB.Call("ModifyTag", {tagid: MDBMood.id, attribute: "posx", value: MDBMood.posx});
            if(neighbour != null)
                MusicDB.Call("ModifyTag", {tagid: neighbour.id, attribute: "posx", value: neighbour.posx});
        }
        else if(direction == "up" || direction == "down") // update posy
        {
            MusicDB.Call("ModifyTag", {tagid: MDBMood.id, attribute: "posy", value: MDBMood.posy});
            if(neighbour != null)
                MusicDB.Call("ModifyTag", {tagid: neighbour.id, attribute: "posy", value: neighbour.posy});
        }

        MusicDB.Request("GetTags", "UpdateTags", {}, {origin: "MoodSettings"});
        return;
    }


    GetMoodByPosition(x, y)
    {
        for(let mood of this.moods)
        {
            if(mood.posx == x && mood.posy == y)
                return mood;
        }
        return null;
    }



    MoveIconUp(MDBMood)
    {
        if(MDBMood == null)
            return null;

        let posx = MDBMood.posx;
        let posy = MDBMood.posy;

        if(posy == 0)   // is already up
            return null;

        let neighbour  = this.GetMoodByPosition(posx, 0);
        if(neighbour != null)
            neighbour.posy = 1;
        MDBMood.posy   = 0;
        return neighbour;
    }

    MoveIconDown(MDBMood)
    {
        if(MDBMood == null)
            return;

        let posx = MDBMood.posx;
        let posy = MDBMood.posy;

        if(posy == 1)   // is already down
            return;

        let neighbour  = this.GetMoodByPosition(posx, 1);
        if(neighbour != null)
            neighbour.posy = 0;
        MDBMood.posy   = 1;
        return neighbour;
    }

    MoveIconLeft(MDBMood)
    {
        if(MDBMood == null)
            return null;

        let posx = MDBMood.posx;
        let posy = MDBMood.posy;

        if(posx == 0)   // already very left
            return null;

        let neighbour  = this.GetMoodByPosition(posx-1, posy);
        if(neighbour != null)
            neighbour.posx++;
        MDBMood.posx--;
        return neighbour;
    }

    MoveIconRight(MDBMood)
    {
        if(MDBMood == null)
            return null;

        let posx = MDBMood.posx;
        let posy = MDBMood.posy;

        let neighbour  = this.GetMoodByPosition(posx+1, posy);
        if(neighbour != null)
            neighbour.posx--;
        MDBMood.posx++;
        return neighbour;
    }
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

