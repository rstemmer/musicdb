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

class MenuButton extends SVGButton
{
    constructor(offset_top, offset_right, iconname, onclick, tooltip)
    {
        super(iconname, onclick, tooltip);
        this.element.classList.add("MenuButton");
        this.element.classList.add("hovpacity");

        this.element.style.top   = offset_top;
        this.element.style.right = offset_right;
    }
}



class MenuEntry extends Element
{
    constructor()
    {
        super("div", ["MenuEntry", "flex-row", "hoverframe"]);
    }


    Update(icon, label, onclick, tooltip)
    {
        let labelelement = document.createElement("label");
        labelelement.innerText = label;

        this.element.innerHTML = "";
        this.element.onclick = onclick;
        this.SetTooltip(tooltip);
        this.element.appendChild(icon.GetHTMLElement());
        this.element.appendChild(labelelement);
    }

    Hide()
    {
        this.element.style.display = "none";
    }
    Show()
    {
        this.element.style.display = "flex";
    }
}

class MenuEntryButton extends MenuEntry
{
    constructor(icon, label, onclick, tooltip)
    {
        super();
        this.Update(icon, label, onclick, tooltip)
    }
}

class MenuEntrySwitch extends MenuEntry
{
    constructor(icona, labela, onclicka, tooltipa,
                iconb, labelb, onclickb, tooltipb)
    {
        super();
        this.icona    = icona;
        this.labela   = labela;
        this.onclicka = onclicka;
        this.tooltipa = tooltipa;
        this.iconb    = iconb;
        this.labelb   = labelb;
        this.onclickb = onclickb;
        this.tooltipb = tooltipb;
        this.SwitchToA();
    }


    onClick()
    {
        if(this.switchstate === "a")
            this.onclicka();
        else
            this.onclickb();
        this.Toggle();
    }


    SwitchToA()
    {
        this.Update(this.icona, this.labela, ()=>{this.onClick();}, this.tootlipa)
        this.switchstate = "a";
    }
    SwitchToB()
    {
        this.Update(this.iconb, this.labelb, ()=>{this.onClick();}, this.tootlipb)
        this.switchstate = "b";
    }
    Toggle()
    {
        if(this.switchstate === "a")
            this.SwitchToB();
        else
            this.SwitchToA();
    }
}



class Menu extends Element
{
    constructor(classes=[], elementid=null)
    {
        super("div", ["Menu", "flex-column", ...classes], elementid);
        this.entries = new Object();
        this.HideMenu();
    }



    HideMenu()
    {
        this.element.style.display = "none";
        this.isopen = false;
    }

    ShowMenu()
    {
        this.element.style.display = "flex";
        this.isopen = true;
    }

    ToggleMenu()
    {
        if(this.isopen)
            this.HideMenu();
        else
            this.ShowMenu();
    }



    AddButton(name, icon, label, onclick, tooltip)
    {
        let entry = new MenuEntryButton(icon, label, ()=>{onclick(); this.ToggleMenu();}, tooltip);
        this.entries[name] = entry;
        this.element.appendChild(entry.GetHTMLElement());
        return
    }



    AddSwitch(name, icona, labela, onclicka, tooltipa,
                    iconb, labelb, onclickb, tooltipb)
    {
        let entry = new MenuEntrySwitch(icona, labela, onclicka, tooltipa,
                                        iconb, labelb, onclickb, tooltipb)
        this.entries[name] = entry;
        this.element.appendChild(entry.GetHTMLElement());
        return
    }



    AddSection(headlinetext, htmlelement)
    {
        htmlelement.classList.add("sectionbody");

        let sectiontitle = document.createElement("div");
        sectiontitle.innerText = headlinetext;
        sectiontitle.classList.add("sectiontitle");
        sectiontitle.classList.add("hlcolor");

        let element = document.createElement("div");
        element.classList.add("section");
        element.appendChild(sectiontitle);
        element.appendChild(htmlelement);
        this.element.appendChild(element);
    }



    // force can be "a" or "b".
    SwitchEntry(name, force=null)
    {
        let switchentry = this.entries[name];
        if(force === "a")
            switchentry.SwitchToA();
        else if(force === "b")
            switchentry.SwitchToB();
        else
            switchentry.Toggle();
        return;
    }



    HideEntry(entryname)
    {
        if(!(entryname in this.entries))
        {
            window.console && console.warn(`Invalid menu entry name ${entryname}`);
            return;
        }
        this.entries[entryname].Hide();
    }
    ShowEntry(entryname)
    {
        if(!(entryname in this.entries))
        {
            window.console && console.warn(`Invalid menu entry name ${entryname}`);
            return;
        }
        this.entries[entryname].Show();
    }
}



class MainMenu extends Menu
{
    constructor(curtain=null)
    {
        super(["frame"], "MainMenu");

        this.curtain     = curtain;
        if(this.curtain)
            this.curtain.AddClickEvent(()=>{this.HideMenu();});

        this._AddFullscreenSwitch();
        this._AddModeSwitch();
        this._AddReloadButton();
        this._AddSettingsButton();
        this._AddAboutButton();
        this._AddDisconnectSwitch();

        // Clicks propagated through Buttons and Switches shall lead to closing the menu
        this.element.onclick = ()=>{this.HideMenu();};
    }



    HideMenu()
    {
        if(this.curtain)
            this.curtain.Hide();
        super.HideMenu();
    }

    ShowMenu()
    {
        if(this.curtain)
            this.curtain.Show();
        super.ShowMenu();
    }



    _AddFullscreenSwitch()
    {
        this.AddSwitch("fullscreen",
            new SVGIcon("EnterFullscreen"),
            "Enter Fullscreen",
            ()=>
            {
                fullscreenmanager.EnterFullscreen();
            },
            "Switch browser into fullscreen mode",

            new SVGIcon("LeaveFullscreen"),
            "Leave Fullscreen",
            ()=>
            {
                fullscreenmanager.LeaveFullscreen();
            },
            "Switch browser into window mode");
    }
    
    _AddModeSwitch()
    {
        this.AddSwitch("modeswitch",
            new SVGIcon("Switch2Video"),
            "Switch to Video Mode",
            ()=>
            {
                mdbmodemanager.SetVideoMode();
            },
            "Switch MusicDB WebUI to Video Mode",

            new SVGIcon("Switch2Audio"),
            "Switch to Audio Mode",
            ()=>
            {
                mdbmodemanager.SetAudioMode();
            },
            "Switch MusicDB WebUI to Audio Mode");
    }

    _AddReloadButton()
    {
        this.AddButton("reload",
            new SVGIcon("Reload"),
            "Reload Artists",
            ()=>
            {
                if(mdbmodemanager.GetCurrentMode() == "audio")
                    MusicDB_Request("GetFilteredArtistsWithAlbums", "ShowArtists");
                else
                    MusicDB_Request("GetFilteredArtistsWithVideos", "ShowArtists");
            },
            "Reload list with artists and their albums/videos");
    }

    _AddSettingsButton()
    {
        this.AddButton("settings",
            new SVGIcon("Settings"),
            "MusicDB Manager",
            ()=>
            {
                leftviewmanager.ShowSettingsMenu();
                mainviewmanager.ShowAboutMusicDB(); // TODO: Show a different view
            },
            "Show Settings and Management Tools for the WebUI and Music Content");
    }

    _AddAboutButton()
    {
        this.AddButton("about",
            new SVGIcon("MusicDB"),
            "About MusicDB",
            ()=>
            {
                mainviewmanager.ShowAboutMusicDB();
            },
            "Show information about MusicDB including version numbers");
    }

    _AddDisconnectSwitch()
    {
        this.AddSwitch("disconnect",
            new SVGIcon("Disconnect"),
            "Disconnect",
            ()=>
            {
                DisconnectFromMusicDB();
            },
            "Close connection to the MusicDB WebSocket Server",

            new SVGIcon("Reconnect"),
            "Reconnect",
            ()=>
            {
                ConnectToMusicDB();
            },
            "Reconnect to the MusicDB WebSocket Server");
    }


    /* Templates
    _AddReloadButton()
    {
        this.AddButton("",
            new SVGIcon(""),
            "",
            ()=>
            {
            },
            "");
    }

    _AddModeSwitch()
    {
        this.AddSwitch("",
            new SVGIcon(""),
            "",
            ()=>
            {
            },
            "",

            new SVGIcon(""),
            "",
            ()=>
            {
            },
            "");
    }
    */



    onMusicDBMessage(fnc, sig, args, pass)
    {
        if(fnc == "LoadWebUIConfiguration" || sig == "UpdateConfig")
        {
            if(args.WebUI.videomode == "enabled")
                this.ShowEntry("modeswitch");
            else
                this.HideEntry("modeswitch");
        }

        return;
    }
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

