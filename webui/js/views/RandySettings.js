// MusicDB,  a music manager with web-bases UI that focus on music.
// Copyright (C) 2017 - 2022  Ralf Stemmer <ralf.stemmer@gmx.net>
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

const RANDYSETTINGSHEADLINE = ["Description", "Settings", "Examples"];
const RST_DESCRIPTION_COLUMN = 0;
const RST_SETTINGS_COLUMN    = 1;
const RST_EXAMPLE_COLUMN     = 2;



class RandySettingsTableRowBase extends TableRow
{
    constructor()
    {
        super(RANDYSETTINGSHEADLINE.length, ["RandySettingsTableRow"]);
    }
}


class RandySettingsSubHeadline extends TableSpanRow
{
    constructor(text)
    {
        let content = new Element("span");
        content.SetInnerText(text);
        super(RANDYSETTINGSHEADLINE.length, ["RandySettingsTableRow", "RandySettingsTableSubHeadline"], content);
    }
}


class RandySettingsTableHeadline extends RandySettingsTableRowBase
{
    constructor()
    {
        super();
        this.AddCSSClass("TableHeadline");
        for(let cellnum in RANDYSETTINGSHEADLINE)
        {
            let headline = document.createTextNode(RANDYSETTINGSHEADLINE[cellnum]);
            this.SetContent(cellnum, headline);
        }
    }
}



class RandySettingsTableRow extends RandySettingsTableRowBase
{
    constructor(description, inputelement, example="")
    {
        super();
        let descriptionnode = document.createTextNode(description);
        let examplenode     = document.createTextNode(example);
        this.SetContent(SST_DESCRIPTION_COLUMN, descriptionnode);
        this.SetContent(SST_SETTINGS_COLUMN,    inputelement);
        this.SetContent(SST_EXAMPLE_COLUMN,     examplenode);
    }
}



class RandySettingsTable extends Table
{
    constructor(onchangecallback)
    {
        super(["RandySettingsTable"]);
        this.onchangecallback = onchangecallback;

        //// Error messages
        //this.urlerror    = new MessageBarError();
        //this.urlerrorrow = new RandySettingsTableSpanRow(this.urlerror);

        // Inputs
        this.nodisabledinput = new BooleanInput(
                (value)=>
                {
                    this.onSettingsChanged("Constraints", "NoDisabled", value);
                    return true; // Data is Valid
                },
                null,
                "Do not include albums that have been disabled.");

        this.nohatedinput = new BooleanInput(
                (value)=>
                {
                    this.onSettingsChanged("Constraints", "NoHated", value);
                    return true; // Data is Valid
                },
                null,
                "Do not include music that have been flagged as hated.");

        this.nobadfileinput = new BooleanInput(
                (value)=>
                {
                    this.onSettingsChanged("Constraints", "NoBadFile", value);
                    return true; // Data is Valid
                },
                null,
                "Do not include music that have been flagged as Bad File / Bad Audio.");

        this.nolivemusicinput = new BooleanInput(
                (value)=>
                {
                    this.onSettingsChanged("Constraints", "NoLiveMusic", value);
                    return true; // Data is Valid
                },
                null,
                "Do not include music that have been flagged as live music / live recording.");

        this.minleninput = new NumberInput(
                (value)=>
                {
                    if(value < 0)
                        return false;

                    this.onSettingsChanged("Constraints", "MinSongLength", value);
                    return true; // Data is Valid
                },
                null,
                "Do not include music with a play time less than the given value in seconds.");

        this.maxleninput = new NumberInput(
                (value)=>
                {
                    if(value < 1)
                        return false;

                    this.onSettingsChanged("Constraints", "MaxSongLength", value);
                    return true; // Data is Valid
                },
                null,
                "Do not include music with a play time more than the given value in seconds.");


        this.songlistlengthinput = new NumberInput(
                (value)=>
                {
                    if(value < 1)
                        return false;

                    this.onSettingsChanged("BlackLists", "SongListLength", value);
                    return true; // Data is Valid
                },
                null,
                "Number of songs until the same song can be played again.");

        this.albumlistlengthinput = new NumberInput(
                (value)=>
                {
                    if(value < 1)
                        return false;

                    this.onSettingsChanged("BlackLists", "AlbumListLength", value);
                    return true; // Data is Valid
                },
                null,
                "Number of albums until a song of the same album can be played again.");

        this.artistlistlengthinput = new NumberInput(
                (value)=>
                {
                    if(value < 1)
                        return false;

                    this.onSettingsChanged("BlackLists", "ArtistListLength", value);
                    return true; // Data is Valid
                },
                null,
                "Number of artists until a song of the same song can be played again.");

        this.maxageinput = new NumberInput(
                (value)=>
                {
                    if(value < 1)
                        return false;

                    this.onSettingsChanged("BlackLists", "MaxAge", value);
                    return true; // Data is Valid
                },
                null,
                "Age of an entry inside the black lists until they get removed. (In Minutes)");


        this.maxtriesinput = new NumberInput(
                (value)=>
                {
                    if(value < 1)
                        return false;

                    this.onSettingsChanged("Limits", "MaxTries", value);
                    return true; // Data is Valid
                },
                null,
                "Number of tries to find a new random song until Randy gives up.");


        // Create Table
        this.headlinerow    = new RandySettingsTableHeadline();

        this.nodisabledrow  = new RandySettingsTableRow(
            "No Disabled Albums",
            this.nodisabledinput,
            this.nodisabledinput.GetTooltip());
        this.nohatedrow     = new RandySettingsTableRow(
            "No Hated Music",
            this.nohatedinput,
            this.nohatedinput.GetTooltip());
        this.nobadfilerow   = new RandySettingsTableRow(
            "No Bad Audio",
            this.nobadfileinput,
            this.nobadfileinput.GetTooltip());
        this.nolivemusicrow = new RandySettingsTableRow(
            "No Live Music",
            this.nolivemusicinput,
            this.nolivemusicinput.GetTooltip());
        this.minlenrow      = new RandySettingsTableRow(
            "Min. Song Length",
            this.minleninput,
            this.minleninput.GetTooltip());
        this.maxlenrow      = new RandySettingsTableRow(
            "Max. Song Length",
            this.maxleninput,
            this.maxleninput.GetTooltip());

        this.songlenrow     = new RandySettingsTableRow(
            "Song List Length",
            this.songlistlengthinput,
            this.songlistlengthinput.GetTooltip());
        this.albumlenrow    = new RandySettingsTableRow(
            "Album List Length",
            this.albumlistlengthinput,
            this.albumlistlengthinput.GetTooltip());
        this.artistlenrow   = new RandySettingsTableRow(
            "Artist List Length",
            this.artistlistlengthinput,
            this.artistlistlengthinput.GetTooltip());
        this.maxagerow      = new RandySettingsTableRow(
            "Max. Age",
            this.maxageinput,
            this.maxageinput.GetTooltip());

        this.maxtriesrow    = new RandySettingsTableRow(
            "Max. Tries",
            this.maxtriesinput,
            this.maxtriesinput.GetTooltip());

        this.AddRow(this.headlinerow);

        this.AddRow(new RandySettingsSubHeadline("Constraints"));
        this.AddRow(this.nodisabledrow);
        this.AddRow(this.nohatedrow);
        this.AddRow(this.nobadfilerow);
        this.AddRow(this.nolivemusicrow);
        this.AddRow(this.minlenrow);
        this.AddRow(this.maxlenrow);

        this.AddRow(new RandySettingsSubHeadline("Black Lists"));
        this.AddRow(this.songlenrow);
        this.AddRow(this.albumlenrow);
        this.AddRow(this.artistlenrow);
        this.AddRow(this.maxagerow);

        this.AddRow(new RandySettingsSubHeadline("Limits"));
        this.AddRow(this.maxtriesrow);
    }



    onSettingsChanged(category, entry, value)
    {
        this.onchangecallback?.(category, entry, value);
    }



    Update(settings)
    {
        this.nodisabledinput.SetValue(settings["Constraints"]["NoDisabled"]);
        this.nohatedinput.SetValue(settings["Constraints"]["NoHated"]);
        this.nobadfileinput.SetValue(settings["Constraints"]["NoBadFile"]);
        this.nolivemusicinput.SetValue(settings["Constraints"]["NoLiveMusic"]);
        this.minleninput.SetValue(settings["Constraints"]["MinSongLength"]);
        this.maxleninput.SetValue(settings["Constraints"]["MaxSongLength"]);
        this.songlistlengthinput.SetValue(settings["BlackLists"]["SongListLength"]);
        this.albumlistlengthinput.SetValue(settings["BlackLists"]["AlbumListLength"]);
        this.artistlistlengthinput.SetValue(settings["BlackLists"]["ArtistListLength"]);
        this.maxageinput.SetValue(settings["BlackLists"]["MaxAge"]);
        this.maxtriesinput.SetValue(settings["Limits"]["MaxTries"]);
    }
}




class RandySettings extends MainSettingsView
{
    constructor()
    {
        super("RandySettings", "Randy Settings", "Configuration for the Random Song Selection Algorithm (Randy).");

        // Settings Table
        this.table = new RandySettingsTable((category, entry, value)=>{this.onSettingsChanged(category, entry, value);});

        this.saved   = new MessageBarConfirm("Randy settings successfully updated.");
        this.saved.ShowCloseButton();
        this.unsaved = new MessageBarWarning("Randy settings changed but not yet saved!");

        this.oldsettings = null;
        this.newsettings = null;

        // Load / Save buttons
        let loadbutton = new SVGButton("Load", ()=>{this.Reload();});
        let savebutton = new SVGButton("Save", ()=>{this.Save();});
        loadbutton.SetTooltip("Reload Randy settings form MusicDB server");
        savebutton.SetTooltip("Save Randy settings");
        this.toolbar   = new ToolBar();
        this.toolbar.AddSpacer(true /*grow*/);
        this.toolbar.AddButton(new ToolGroup([loadbutton, savebutton]));

        this.AppendChild(this.toolbar);
        this.AppendChild(this.saved);
        this.AppendChild(this.unsaved);
        this.AppendChild(this.table);
    }



    onSettingsChanged(category, entry, value)
    {
        // During initializing the table, changes will be applied but the table object is not yet assigned.
        if(typeof this.table === "undefined")
            return;
        if(typeof this.newsettings !== "object")
            return;
        if(typeof this.oldsettings !== "object")
            return;

        this.newsettings[category][entry] = value;

        // Check if things are different to the settings stored at the server
        if(this.HaveSettingsChanged())
        {
            this.unsaved.Show();
        }
        else
        {
            this.unsaved.Hide();
        }
        return;
    }



    HaveSettingsChanged()
    {
        for(let category in this.oldsettings)
        {
            for(let entry in this.oldsettings[category])
            {
                let oldvalue = this.oldsettings[category][entry];
                let newvalue = this.newsettings[category][entry];
                if(newvalue != oldvalue)
                    return true;
            }
        }
        return false;
    }





    Reload()
    {
        MusicDB.Request("LoadRandyConfiguration", "ReloadRandySettings");
    }
    Save()
    {
        if(this.HaveSettingsChanged())
        {
            MusicDB.Broadcast("SaveRandyConfiguration", "ReloadRandySettings", {config: this.newsettings});
        }
    }



    UpdateView(settings)
    {
        // Reset settings
        this.oldsettings = structuredClone(settings);
        this.newsettings = structuredClone(settings);
        this.table.Update(settings);
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        if(fnc == "LoadRandyConfiguration" || fnc == "SaveRandyConfiguration")
        {
            if(fnc == "SaveRandyConfiguration")
            {
                this.saved.Show();
            }
            else
            {
                this.saved.Hide();
                this.unsaved.Hide();
            }
            this.UpdateView(args);
        }
        return;
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

