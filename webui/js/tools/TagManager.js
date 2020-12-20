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

class TagManager
{
    constructor()
    {
        this.tagcache     = null;
        this.activegenres = null;
    }



    UpdateCache(MDBTags)
    {
        this.tagcache = MDBTags;
        // Sort main genres by posx order
        this.tagcache.genres.sort((a, b)=>
            {
                if (a.posx > b.posx)
                        return 1;
                if (a.posx < b.posx)
                        return -1;
                return 0;
            });
        // Sort moods by row and column
        this.tagcache.moods.sort((a, b)=>
            {
                let arate = a.posy * 1000 + a.posx;
                let brate = b.posy * 1000 + b.posx;
                if (arate > brate)
                        return 1;
                if (arate < brate)
                        return -1;
                return 0;
            });
    }
    UpdateActiveGenres(albumfilter)
    {
        if(this.tagcache == null)
            return;

        this.activegenres = new Array();
        let  genres       = this.GetGenres();
        for(let genrename of albumfilter)
        {
            let activegenre = genres.find(genre => genre.name == genrename);
            this.activegenres.push(activegenre);
        }

        return;
    }



    GetTags()
    {
        return this.tagcache;
    }
    GetGenres()
    {
        return this.tagcache.genres;
    }
    GetSubgenres()
    {
        return this.tagcache.subgenres;
    }
    GetMoods()
    {
        return this.tagcache.moods;
    }

    GetActiveGenres()
    {
        return this.activegenres;
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        if(fnc == "GetTags")
        {
            this.UpdateCache(args);
        }
        else if(fnc == "GetMDBState" && sig == "UpdateMDBState")
        {
            this.UpdateActiveGenres(args.albumfilter);
        }
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

