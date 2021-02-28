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

class WebUISettings extends MainSettingsView
{
    constructor()
    {
        super("WebUISettings", "WebUI Settings", "Enable or disable features of the WebUI. These settings are applied to all clients. The behavior of the MusicDB server is not affected in any way.");

        this.videocheckbox = new SettingsCheckbox(
            "Video Mode",
            "This switch allows hiding or showing all WebUI elements corresponding to music videos.</br>This includes the Song/Video mode switch in the main menu.",
            (state)=>{
                if(state == true) this.ChangeSetting("WebUI", "videomode", "enabled");
                else              this.ChangeSetting("WebUI", "videomode", "disabled");
            }
        );

        this.lyricscheckbox = new SettingsCheckbox(
            "Lyrics",
            "When lyrics are disabled, the Lyrics-State icon of songs listed in the Album Views are hidden.</br>This switch will not remove any information, it just hides the related user interface elements.",
            (state)=>{
                if(state == true) this.ChangeSetting("WebUI", "lyrics", "enabled");
                else              this.ChangeSetting("WebUI", "lyrics", "disabled");
            }
        );

        let settingslist = new SettingsList();
        settingslist.AddEntry(this.videocheckbox);
        settingslist.AddEntry(this.lyricscheckbox);

        this.element.appendChild(settingslist.GetHTMLElement());
        this.settings = null;
    }



    UpdateView(settings)
    {
        this.settings = settings;

        this.videocheckbox.SetState( settings.WebUI.videomode == "enabled");
        this.lyricscheckbox.SetState(settings.WebUI.lyrics    == "enabled");
        return;
    }



    ChangeSetting(section, key, value)
    {
        this.settings[section][key] = value;
        MusicDB_Broadcast("SaveWebUIConfiguration", "UpdateConfig", {config: this.settings});
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

