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

class MoodManager extends MainView
{
    constructor()
    {
        let headline = new SimpleMainViewHeadline("Mood Manager");
        super("MoodManager", headline);

        this.table     = new MoodsTable();
        this.moods     = [];
        this.moodstats = {};

        this.element.appendChild(this.table.GetHTMLElement());
    }



    UpdateView()
    {
        this.table.Update(this.moods, this.moodstats);
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        if(fnc == "GetTags")
        {
            // When tags were added, update the view
            if(pass != null && pass.origin == "MoodsSettings")
                MusicDB_Request("GetTagsStatistics", "UpdateTagsStatistics");

            //&& sig == "ShowMoodManager")
            window.console && console.log(args.moods);
            this.moods = args.moods;
            this.UpdateView();
        }
        else if(fnc == "GetTagsStatistics")
        {
            window.console && console.log(args);
            this.moodstats = args;
            this.UpdateView();
        }
        return;
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

