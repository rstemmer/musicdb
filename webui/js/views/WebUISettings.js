// MusicDB,  a music manager with web-bases UI that focus on music.
// Copyright (C) 2017-2021  Ralf Stemmer <ralf.stemmer@gmx.net>
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
            "Enable Video Mode",
            "This switch allows hiding or showing all WebUI elements corresponding to music videos.</br>This includes the Song/Video mode switch in the main menu.</br><span style=\"color:red\">Experimental Feature!</span>",
            (state)=>{
                if(state == true) this.ChangeSetting("WebUI", "videomode", "enabled");
                else              this.ChangeSetting("WebUI", "videomode", "disabled");
            }
        );

        this.lyricscheckbox = new SettingsCheckbox(
            "Enable Lyrics",
            "When lyrics are disabled, the Lyrics-State icon of songs listed in the Album Views are hidden.</br>This switch will not remove any information, it just hides the related user interface elements.",
            (state)=>{
                if(state == true) this.ChangeSetting("WebUI", "lyrics", "enabled");
                else              this.ChangeSetting("WebUI", "lyrics", "disabled");
            }
        );

        this.avshowreleasecheckbox = new SettingsCheckbox(
            "Show album release date in Artists View",
            "If set, the release date of an album is shown next to its name in the Artists View. If false, the release date will not be shown.</br>In any case, the albums of an artist are sorted by their release date.</br><span style=\"color:red\">Requires reloading the WebUI!</span> (Press F5)",
            (state)=>{
                if(state == true) this.ChangeSetting("ArtistsView", "showrelease", true);
                else              this.ChangeSetting("ArtistsView", "showrelease", false);
            }
        );

        this.gsvshowothercheckbox= new SettingsCheckbox(
            "Show \"Other\" genre in the gere lists of the Genre Selection View",
            "If set, the default genre \"Other\" is listed in the set of selectable genres.</br>This setting does not hide the default genre from the list of genres to tag a song or album with.</br><span style=\"color:red\">Requires reloading the WebUI!</span> (Press F5)",
            (state)=>{
                if(state == true) this.ChangeSetting("GenreSelectionView", "showother", true);
                else              this.ChangeSetting("GenreSelectionView", "showother", false);
            }
        );

        this.showstreamplayercheckbox = new SettingsCheckbox(
            "Show Audio Stream Player inside the Main Menu",
            "If set, an audio stream player is shown in the main menu. This player connects to the configured audio stream. With this audio player it is possible to listen to the MusicDB audio stream directly from the browser.",
            (state)=>{
                if(state == true) this.ChangeSetting("MainMenu", "showstreamplayer", true);
                else              this.ChangeSetting("MainMenu", "showstreamplayer", false);
            }
        );

        this.showsystemstatuscheckbox = new SettingsCheckbox(
            "Show System Status inside the Main Menu",
            "If set, the system status is shown in the main menu."+
            " It shows if the connection between the MusicDB Server and Icecast is up and if data gets streamed."+
            " These information are not mandatory to know but help you to quickly identify issues with the audio stream.",
            (state)=>{
                if(state == true) this.ChangeSetting("MainMenu", "showsystemstatus", true);
                else              this.ChangeSetting("MainMenu", "showsystemstatus", false);
            }
        );

        let settingslist = new SettingsList();
        settingslist.AddEntry(this.videocheckbox);
        settingslist.AddEntry(this.lyricscheckbox);
        settingslist.AddEntry(this.avshowreleasecheckbox);
        settingslist.AddEntry(this.gsvshowothercheckbox);
        settingslist.AddEntry(this.showstreamplayercheckbox);
        settingslist.AddEntry(this.showsystemstatuscheckbox);

        this.AppendChild(settingslist);
        this.settings = null;
    }



    UpdateView(settings)
    {
        this.settings = settings;

        this.videocheckbox.SetState( settings.WebUI.videomode == "enabled");
        this.lyricscheckbox.SetState(settings.WebUI.lyrics    == "enabled");
        this.avshowreleasecheckbox.SetState(settings.ArtistsView.showrelease == true);
        this.gsvshowothercheckbox.SetState(settings.GenreSelectionView.showother == true);
        this.showstreamplayercheckbox.SetState(settings.MainMenu.showstreamplayer == true);
        this.showsystemstatuscheckbox.SetState(settings.MainMenu.showsystemstatus == true);
        return;
    }



    ChangeSetting(section, key, value)
    {
        this.settings[section][key] = value;
        MusicDB.Broadcast("SaveWebUIConfiguration", "UpdateConfig", {config: this.settings});
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

