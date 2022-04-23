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

class AdvancedGenreSelectionView extends LeftView
{
    constructor()
    {
        super("AdvancedGenreSelectionView");

        // Tool Bar
        this.toolbar     = new ToolBar();
        this.closebutton = new TextButton("Back", "Back to Music",
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
            "Hide advanced genre selection menu and go back to the Music list");

        this.toolbar.AddSpacer(true); // grow
        this.toolbar.AddButton(this.closebutton);
        this.toolbar.AddSpacer(true); // grow

        this.AppendChild(this.toolbar);
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        return;
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

