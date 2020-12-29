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
            "Back to Artists", 
            ()=>{
                this.UnlockView();
                leftviewmanager.ShowArtistsView();
                },
            "Hide Management menu and show Artists");

        this.views.push(webuisettings);
        this.AddMenuEntry(
            new SVGIcon("Settings"),
            "WebUI Settings",
            ()=>{
                MusicDB_Request("LoadWebUIConfiguration", "ShowWebUISettings");
                },
            "Show WebUI Settings");

        this.views.push(genresettings);
        this.AddMenuEntry(
            new SVGIcon("Tags"),
            "Genre Manager",
            ()=>{
                MusicDB_Request("GetTags", "ShowGenreSettings");
                MusicDB_Request("GetTagsStatistics", "UpdateTagsStatistics");
                },
            "Manage, Add and Remove Genres and Subgenres");

        this.views.push(moodmanager);
        this.AddMenuEntry(
            new SVGIcon("Tags"),
            "Mood Manager",
            ()=>{
                MusicDB_Request("GetTags", "ShowMoodManager");
                MusicDB_Request("GetTagsStatistics", "UpdateTagsStatistics");
                },
            "Manage, Add and Remove Mood Flags");

        this.views.push(hiddenalbums);
        this.AddMenuEntry(
            new SVGIcon("Hide"),
            "Hidden Albums",
            ()=>{
                MusicDB_Request("GetHiddenAlbums", "ShowHiddenAlbums");
                },
            "Show list of hidden albums that can be made visible again");

        this.views.push(videoimport);
        this.AddMenuEntry(
            new SVGIcon("MusicDB"),
            "Import Video",
            ()=>{
                MusicDB_Request("FindNewPaths", "ShowVideoImport");
                },
            "Upload and/or Import Music Videos");
    }


    AddMenuEntry(icon, name, onclick, tooltip)
    {
        let entry = document.createElement("div");
        entry.classList.add("flex-row");
        entry.classList.add("menuentry");
        entry.classList.add("hoverframe");
        entry.title   = tooltip;
        entry.onclick = onclick;

        let text = document.createElement("span");
        text.innerText = name;

        entry.appendChild(icon.GetHTMLElement());
        entry.appendChild(text);

        this.element.appendChild(entry);
        this.entries.push(entry);
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
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

