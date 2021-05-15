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

class SongSettings extends TabSelect
{
    constructor(MDBSong, MDBTags)
    {
        super();
        this.element.classList.add("SongSettings");

        this.songmoods      = new SongMoods();
        this.songproperties = new SongProperties();
        this.genreedit      = new TagListEdit("genre");
        this.subgenreedit   = new TagListEdit("subgenre");
        this.audioplayer    = new AudioPlayer(MDBSong.path);
        this.instrumental   = new SettingsCheckbox(
            "Instrumental",
            "You can use this checkbox to toggle the lyrics state between <i>Not Set</i> and <i>Instrumental</i>.<br> This option is only available if there is no other lyrics state set.");

        this.Update(MDBSong, MDBTags);

        this.genrestab  = new Element("div", ["flex-grow"]);
        this.moodstab   = new Element("div", ["flex-wrap", "flex-row"]);
        this.previewtab = new Element("div", ["flex-grow"]);

        this.moodstab.AppendChild(this.songmoods);
        this.moodstab.AppendChild(this.songproperties);
        this.moodstab.AppendChild(this.instrumental);

        this.genrestab.AppendChild(this.genreedit);
        this.genrestab.AppendChild(this.subgenreedit);

        this.previewtab.AppendChild(this.audioplayer);

        let genretabid   = this.AddTab(new SVGIcon("Tags"), "Genre Tags",         this.genrestab, true);
        let moodstabid   = this.AddTab(new SVGIcon("Tags"), "Moods & Properties", this.moodstab);
        let previewtabid = this.AddTab(new SVGIcon("Play"), "Preview",            this.previewtab);

        // When the genre tab gets selected, set focus on the main genre input element
        this.SetOnShowCallback(genretabid, ()=>{this.genreedit.SetFocus();});
    }



    Update(MDBSong, MDBTags)
    {
        this.songmoods.UpdateButtons(MDBSong, MDBTags);
        this.songproperties.UpdateButtons(MDBSong);
        this.genreedit.Update("audio", MDBSong.id, MDBTags);
        this.subgenreedit.Update("audio", MDBSong.id, MDBTags);

        // Update lyrics state
        let lyricsstate = MDBSong.lyricsstate;
        this.instrumental.SetState(lyricsstate === 4);
        if(lyricsstate === 0 || lyricsstate === 4)
            this.instrumental.Enable();
        else
            this.instrumental.Disable();
        this.instrumental.SetHandler((state)=>
            {
                // Will only be called when the checkbox is enabled
                let lyricsstate;
                if(state === true)
                    lyricsstate = 4;    // instrumental
                else
                    lyricsstate = 0;    // lyrics state not configured
                MusicDB_Broadcast("SetSongLyrics", "UpdateLyricsState", {songid: MDBSong.id, lyrics: null, lyricsstate: lyricsstate});
            }
        );

    }
}




// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

