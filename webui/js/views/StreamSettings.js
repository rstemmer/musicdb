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


class StreamSettingsTableSpanRow extends TableSpanRow
{
    constructor(content)
    {
        super(STREAMSETTINGSHEADLINE.length, ["StreamSettingsTableRow"], content);
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
    constructor(onchangecallback)
    {
        super(["StreamSettingsTable"]);
        this.onchangecallback = onchangecallback;

        // Error messages
        this.urlerror    = new MessageBarError();
        this.urlerror.HideCloseButton();
        this.urlerrorrow = new StreamSettingsTableSpanRow(this.urlerror);

        // Text Inputs
        this.addressinput  = new TextInput(
                (url)=>{
                    let isvalid = this.ValidateURL(url);
                    if(typeof this.onchangecallback === "function")
                        this.onchangecallback();
                    return isvalid;
                },
                "", "Enter the stream URL including protocol and port number"
            );
        this.usernameinput = new TextInput(
                (username)=>{
                    if(typeof this.onchangecallback === "function")
                        this.onchangecallback();
                    return;
                },
                "", "Enter your user name if the stream needs authentication");
        this.passwordinput = new TextInput(
                (password)=>{
                    if(typeof this.onchangecallback === "function")
                        this.onchangecallback();
                    return;
                },
                "", "Enter your password if the stream needs authentication");

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
        this.AddRow(this.urlerrorrow);
        this.AddRow(this.usernamerow);
        this.AddRow(this.passwordrow);
    }



    ValidateURL(url)
    {
        if(url.length <= 0)
        {
            this.urlerror.UpdateMessage("Please enter a stream address.");
            this.urlerror.Show();
            return false;
        }

        // Check Protocol
        let validprotocols = ["http", "https", "rtp", "srtp", "rtcp", "rtsp", "rtmp", "srt"];
        let protocol = url.substring(0, url.indexOf(":"));

        if(validprotocols.indexOf(protocol) < 0)
        {
            this.urlerror.UpdateMessage(`Unknown protocol "${protocol}". Please enter use one of those: ${validprotocols.join(", ")}`);
            this.urlerror.Show();
            return false;
        }

        // Check rest of the address
        let address  = url.substring(url.indexOf(":")+3); // Skip "://"

        if(address.length <= 0)
        {
            this.urlerror.UpdateMessage(`Protocol is valid, but rest of the address is missing.`);
            this.urlerror.Show();
            return false;
        }

        // Check host name
        let hostname;
        if(address.indexOf(":") > 0)
            hostname = address.substring(0, address.indexOf(":"));
        else if(address.indexOf("/") > 0)
            hostname = address.substring(0, address.indexOf("/"));
        else
            hostname = address;

        if(hostname <= 0)
        {
            this.urlerror.UpdateMessage(`Hostname is missing. Please enter the complete audio stream address.`);
            this.urlerror.Show();
            return false;
        }

        // Check port
        let portnumber = "";
        if(address.indexOf(":") > 0)
        {
            portnumber = address.substring(address.indexOf(":")+1); // Skip ":"
            if(portnumber.indexOf("/") > 0)
                portnumber = portnumber.substring(0, portnumber.indexOf("/"));
        }

        if(portnumber.length > 0 && isNaN(portnumber))
        {
            this.urlerror.UpdateMessage(`The given port number "${portnumber}" is not valid. Please enter a correct number for the port.`);
            this.urlerror.Show();
            return false;
        }

        // Everything is fine.
        this.urlerror.Hide();
        return true;
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
        this.table = new StreamSettingsTable(()=>{this.onSettingsChanged();});

        // TLS Information
        this.tlsinfo = new Element("div", ["Welcome"]);

        // Test Player
        this.player = new AudioStreamPlayer();
        this.player.SetErrorCallback((event)=>{this.onStreamError(event);});
        this.player.SetPlaysCallback((event)=>{this.onStreamPlays(event);});

        // Message bar for stream errors
        this.streamerror = new MessageBarError();
        this.streamerror.HideCloseButton();
        this.streamplays = new MessageBarConfirm("Connection to the stream seems to work technically.");

        this.saved   = new MessageBarConfirm("Audio stream connection settings successfully updated.");
        this.unsaved = new MessageBarWarning("Audio stream changed but not yet saved!");
        this.unsaved.HideCloseButton();

        // Load / Save buttons
        let loadbutton = new SVGButton("Load", ()=>{this.Reload()});
        let savebutton = new SVGButton("Save", ()=>{this.Save()});
        loadbutton.SetTooltip("Reload audio stream settings form MusicDB server");
        savebutton.SetTooltip("Save audio stream settings");
        this.toolbar   = new ToolBar();
        this.toolbar.AddSpacer(true /*grow*/);
        this.toolbar.AddButton(new ToolGroup([loadbutton, savebutton]));

        this.UpdateTLSInformation();

        this.AppendChild(this.table);
        this.AppendChild(this.player);
        this.AppendChild(this.streamerror);
        this.AppendChild(this.tlsinfo);
        this.AppendChild(this.streamplays);
        this.AppendChild(this.saved);
        this.AppendChild(this.unsaved);
        this.AppendChild(this.toolbar);
    }



    onStreamError(event)
    {
        // Get error code
        // Type: MediaError: https://developer.mozilla.org/en-US/docs/Web/API/MediaError
        let error = event.target.error;
        let code  = error.code;

        let message;
        switch(code)
        {
            case 1:
                message = "Connecting aborted by the user.";
                break;
            case 2:
                message = "Network connection error. Are you online? Is the URL correct (incl. protocol, port number)?";
                break;
            case 3:
                message = "Decoding failed. Is the URL actually addressing an audio stream? Is the port number correct?";
                break;
            case 4:
                message = "Media source not suitable. If it is a TLS secured stream (https://), does your browser trust the certificate?";
                break;
        }

        this.streamerror.UpdateMessage(`Error: ${message}`);
        this.streamerror.Show();
        this.streamplays.Hide();
    }
    onStreamPlays(event)
    {
        this.streamerror.Hide();
        this.streamplays.Show();
    }



    onSettingsChanged()
    {
        // During initializing the table, changes will be applied but the table object is not yet assigned.
        if(typeof this.table === "undefined")
            return;
        // Same for other objects
        if(typeof this.oldurl      === "undefined"
        || typeof this.oldusername === "undefined"
        || typeof this.oldpassword === "undefined")
            return;

        let newurl      = this.table.addressinput.GetValue();
        let newusername = this.table.usernameinput.GetValue();
        let newpassword = this.table.passwordinput.GetValue();

        // Check if things are different to the settings stored at the server
        // If not, just return
        if(this.oldurl      === newurl
        && this.oldusername === newusername
        && this.oldpassword === newpassword)
        {
            this.unsaved.Hide();
            return;
        }

        this.UpdateTLSInformation();
        this.player.Configure(newurl, newusername, newpassword);
        this.unsaved.Show();
    }



    UpdateTLSInformation()
    {
        let url = this.table.addressinput.GetValue();
        let message = "";
        message += "<p>If you use a self signed certificate to secure the audio stream";
        message += " you may have to confirm that this certificate can be trusted by the browser.";
        message += " To do so, please click the following URL to the audio stream";
        message += " and follow the instructions of the browser to confirm that you trust the server.</p>";
        message += `<p><b>Please follow this link:</b> <a href="${url}">${url}</a></p>`;
        message += "<p>Once the certificate has been confirmed the browser trusts the source.";
        message += " Any changes to the URL that do not lead to use a different certificate can be done";
        message += " without confirming the certificate again.</p>";

        this.tlsinfo.SetInnerHTML(message);
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

        this.oldurl      = url;
        this.oldusername = username;
        this.oldpassword = password;

        this.table.Update(    url, username, password);
        this.player.Configure(url, username, password);
        this.UpdateTLSInformation();
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        if(fnc == "LoadWebUIConfiguration" || fnc == "SaveWebUIConfiguration")
        {
            if(fnc == "SaveWebUIConfiguration")
                this.saved.Show();
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

