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

const STREAMSETTINGSHEADLINE = ["Description", "Settings", "Examples"];
const SST_DESCRIPTION_COLUMN = 0;
const SST_SETTINGS_COLUMN    = 1;
const SST_EXAMPLE_COLUMN     = 2;



class StreamSettingsTableRowBase extends TableRow
{
    constructor()
    {
        super(STREAMSETTINGSHEADLINE.length, ["StreamSettingsTableRow"]);
    }
}


class StreamSettingsTableHeadline extends StreamSettingsTableRowBase
{
    constructor()
    {
        super();
        for(let cellnum in STREAMSETTINGSHEADLINE)
        {
            let headline = document.createTextNode(STREAMSETTINGSHEADLINE[cellnum]);
            this.SetContent(cellnum, headline);
        }
    }
}



class StreamSettingsTableRow extends StreamSettingsTableRowBase
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



class StreamSettingsTable extends Table
{
    constructor()
    {
        super(["StreamSettingsTable"]);

        // Text Inputs
        this.addressinput  = new TextInput(()=>{return;});
        this.usernameinput = new TextInput(()=>{return;});
        this.passwordinput = new TextInput(()=>{return;});

        // Source: https://stackoverflow.com/questions/9719570/generate-random-password-string-with-requirements-in-javascript/9719815#comment103450423_9719570
        let randompassword = new Array(20).fill().map(() => String.fromCharCode(Math.random()*86+40)).join("")

        // Table
        this.headlinerow  = new StreamSettingsTableHeadline();
        this.addressrow   = new StreamSettingsTableRow(
            "Address (URL)",
            this.addressinput,
            `http://${location.hostname}:8000/stream or https://${location.hostname}:8000/stream`);
        this.usernamerow  = new StreamSettingsTableRow(
            "User Name",
            this.usernameinput,
            "max_power");
        this.passwordrow  = new StreamSettingsTableRow(
            "Password",
            this.passwordinput,
            `${randompassword}`);
        this.AddRow(this.headlinerow);
        this.AddRow(this.addressrow );
        this.AddRow(this.usernamerow);
        this.AddRow(this.passwordrow);
    }



    Update(url, username, password)
    {
        this.addressinput.SetValue(url);
        this.usernameinput.SetValue(username);
        this.passwordinput.SetValue(password);
    }
}




class StreamSettings extends MainSettingsView
{
    constructor()
    {
        super("StreamSettings", "Stream Settings", "Configure the connection settings to the audio stream managed by MusicDB. Username and Password are optional. These settings are used by the audio stream player integrated in the WebUI. It does not change any settings of the MusicDB server.");

        // Settings Table
        this.table = new StreamSettingsTable();

        // Test Player
        this.player = new AudioStreamPlayer();

        // Load / Save buttons
        let loadbutton = new SVGButton("Load", ()=>{this.Reload()});
        let savebutton = new SVGButton("Save", ()=>{this.Save()});
        loadbutton.SetTooltip("Reload audio stream settings form MusicDB server");
        savebutton.SetTooltip("Save audio stream settings");
        this.toolbar   = new ToolBar();
        this.toolbar.AddSpacer(true /*grow*/);
        this.toolbar.AddButton(new ToolGroup([loadbutton, savebutton]));

        this.AppendChild(this.table);
        this.AppendChild(this.player);
        this.AppendChild(this.toolbar);
    }



    Reload()
    {
        MusicDB_Request("LoadWebUIConfiguration", "ReloadStreamSettings");
    }
    Save()
    {
        this.settings["Stream"]["url"]      = this.table.addressinput.GetValue();
        this.settings["Stream"]["username"] = this.table.usernameinput.GetValue();
        this.settings["Stream"]["password"] = this.table.passwordinput.GetValue();
        MusicDB_Broadcast("SaveWebUIConfiguration", "UpdateConfig", {config: this.settings});
    }



    UpdateView(settings)
    {
        this.settings = settings;

        let url      = settings.Stream.url;
        let username = settings.Stream.username;
        let password = settings.Stream.password;

        this.table.Update(    url, username, password);
        this.player.Configure(url, username, password);
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        if(fnc == "LoadWebUIConfiguration" || fnc == "SaveWebUIConfiguration")
        {
            this.UpdateView(args);
        }
        return;
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

