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

class SettingsMenu extends LeftView
{
    constructor()
    {
        super("SettingsMenu");
        this.entries = new Array();
        this.views   = new Array();
        // ! The index of a view must match the index of an menu entry !

        this.views.push(null);
        this.AddMenuEntry(
            new SVGIcon("Back"),
            "Back to Music", 
            ()=>{
                this.UnlockView();
                WebUI.GetManager("LeftView").ShowArtistsView();
                let modemanager = WebUI.GetManager("MusicMode");
                let musicmode   = modemanager.GetCurrentMode();
                if(musicmode == "audio")
                {
                    let albumid = modemanager.GetCurrentAlbumID();
                    MusicDB.Request("GetAlbum", "ShowAlbum", {albumid: albumid});
                }
                else
                {
                    let videoid = modemanager.GetCurrentVideoID();
                    MusicDB.Request("GetVideo", "ShowVideo", {videoid: videoid});
                }
                },
            "Hide Management menu and go back to the Music Views");

        this.views.push(WebUI.GetView("WebUISettings"));
        this.AddMenuEntry(
            new SVGIcon("Settings"),
            "WebUI Settings",
            ()=>{
                MusicDB.Request("LoadWebUIConfiguration", "ShowWebUISettings");
                },
            "Show WebUI Settings");

        this.views.push(WebUI.GetView("StreamSettings"));
        this.AddMenuEntry(
            new SVGIcon("Song"),
            "Stream Settings",
            ()=>{
                MusicDB.Request("LoadWebUIConfiguration", "ShowStreamSettings");
                },
            "Show Stream Settings");

        this.views.push(WebUI.GetView("RandySettings"));
        this.AddMenuEntry(
            new SVGIcon("Randy"),
            "Randy Settings",
            ()=>{
                MusicDB.Request("LoadRandyConfiguration", "ShowRandySettings");
                },
            "Show Randy Settings");

        this.views.push(WebUI.GetView("GenreSettings"));
        this.AddMenuEntry(
            new SVGIcon("Tags"),
            "Genre Manager",
            ()=>{
                MusicDB.Request("GetTags", "ShowGenreSettings");
                MusicDB.Request("GetTagsStatistics", "UpdateTagsStatistics");
                },
            "Manage, Add and Remove Genres and Subgenres");

        this.views.push(WebUI.GetView("MoodSettings"));
        this.AddMenuEntry(
            new SVGIcon("Tags"),
            "Mood Manager",
            ()=>{
                MusicDB.Request("GetTags", "ShowMoodManager");
                MusicDB.Request("GetTagsStatistics", "UpdateTagsStatistics");
                },
            "Manage, Add and Remove Mood Flags");

        this.views.push(WebUI.GetView("HiddenAlbums"));
        this.AddMenuEntry(
            new SVGIcon("Hide"),
            "Hidden Albums",
            ()=>{
                MusicDB.Request("GetHiddenAlbums", "ShowHiddenAlbums");
                },
            "Show list of hidden albums that can be made visible again");

        this.views.push(WebUI.GetView("AlbumImport"));
        this.AddMenuEntry(
            new SVGIcon("Import"),
            "Import Album",
            ()=>{
                MusicDB.Request("FindNewContent", "ShowAlbumImport");
                },
            "Import Music Album");

        this.views.push(WebUI.GetView("VideoImport"));
        this.AddMenuEntry(
            new SVGIcon("Import"),
            "Import Video",
            ()=>{
                MusicDB.Request("FindNewContent", "ShowVideoImport");
                },
            "Upload and/or Import Music Videos");

        this.views.push(WebUI.GetView("Repair"));
        this.AddMenuEntry(
            new SVGIcon("Repair"),
            "Repair Database",
            ()=>{
                MusicDB.Request("InitiateFilesystemScan", "ShowRepairView");
                },
            "Show Invalid Database Enties");

        this.views.push(WebUI.GetView("TaskList"));
        this.AddMenuEntry(
            new SVGIcon("TaskList"),
            "Task List",
            ()=>{
                MusicDB.Request("GetCurrentTasks", "ShowCurrentTasks");
                },
            "Show open and running MusicDB tasks");
    }


    AddMenuEntry(icon, name, onclick, tooltip)
    {
        let entry = new MenuEntryButton(icon, name, onclick, tooltip);
        let element = entry.GetHTMLElement();

        this.element.appendChild(element);
        this.entries.push(element);
        return;
    }



    HighlightMenuEntry(viewref)
    {
        let index = this.views.indexOf(viewref);
        if(typeof index === "number")
            this.entries[index].dataset.highlight = true;
        return;
    }



    ClearHighlightedEntries()
    {
        for(let entry of this.entries)
        {
            entry.dataset.highlight = false;
        }
    }



    ShowVideoEntry()
    {
        let index = this.views.indexOf(WebUI.GetView("VideoImport"));
        if(typeof index === "number")
            this.entries[index].style.display= "flex";
    }
    HideVideoEntry()
    {
        let index = this.views.indexOf(WebUI.GetView("VideoImport"));
        if(typeof index === "number")
            this.entries[index].style.display= "none";
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        if(fnc == "LoadWebUIConfiguration" || sig == "UpdateConfig")
        {
            if(args.WebUI.videomode == "enabled")
                this.ShowVideoEntry();
            else
                this.HideVideoEntry();
        }

        return;
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

