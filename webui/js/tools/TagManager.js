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

class TagManager
{
    constructor()
    {
        this.tagcache        = null;
        this.activegenres    = null;
        this.activesubgenres = null;
        this.activesubgenrestree = null;
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
    UpdateActiveGenres(genrefilter)
    {
        if(this.tagcache == null)
            return;

        this.activegenres = new Array();
        let  genres       = this.GetGenres();
        for(let genrename of genrefilter)
        {
            let activegenre = genres.find(genre => genre.name == genrename);
            this.activegenres.push(activegenre);
        }

        return;
    }

    UpdateActiveSubgenres(subgenrefilter)
    {
        if(this.tagcache == null)
            return;

        this.activesubgenres     = new Array();
        this.activesubgenrestree = new Object();

        let genres    = this.GetGenres();
        let subgenres = this.GetSubgenres();

        for(let genre of genres)
        {
            let genrename = genre.name;
            this.activesubgenrestree[genrename] = new Array();
            for(let subgenrename of subgenrefilter[genrename])
            {
                let activesubgenre = subgenres.find(subgenre => subgenre.name == subgenrename);
                this.activesubgenrestree[genrename].push(activesubgenre);
                this.activesubgenres.push(activesubgenre);
            }

        }

        return;
    }



    GetTags()
    {
        return this.tagcache;
    }
    GetGenres()
    {
        if(this.tagcache === null)
            return null;
        return this.tagcache.genres;
    }
    GetSubgenres()
    {
        if(this.tagcache === null)
            return null;
        return this.tagcache.subgenres;
    }
    // genre: name or id
    GetSubgenresOfGenre(genre)
    {
        if(this.tagcache === null)
            return null;
        return this.tagcache.subgenres.filter(x => x.name===genre || x.parentid===genre)
    }
    GetMoods()
    {
        if(this.tagcache === null)
            return null;
        return this.tagcache.moods;
    }

    GetActiveGenres()
    {
        if(this.activegenres === null)
            return null;
        return this.activegenres;
    }
    GetActiveGenreIDs()
    {
        if(this.activegenres === null)
            return null;
        return this.activegenres.map(x => x.id);
    }

    GetActiveSubgenreIDs()
    {
        if(this.activesubgenres === null)
            return null;
        return this.activesubgenres.map(x => x.id);
    }



    GetGenreTree()
    {
        let genres     = this.GetGenres();
        let subgenres  = this.GetSubgenres();

        if(genres === null || subgenres === null)
            return null;

        // Create Tree of genres and their sub genres
        let genretree = new Object();
        for(let genre of genres)
        {
            let genreid = genre.id;
            genretree[genreid] = new Object();
            genretree[genreid]["genre"]     = genre;
            genretree[genreid]["subgenres"] = new Object();
        }

        // Add sub genre to the tree
        for(let subgenre of subgenres)
        {
            let genreid    = subgenre.parentid;
            let subgenreid = subgenre.id;
            genretree[genreid]["subgenres"][subgenreid] = subgenre;
        }

        return genretree;
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        if(fnc == "GetTags")
        {
            this.UpdateCache(args);
        }
        else if(fnc == "GetMDBState" && sig == "UpdateMDBState")
        {
            this.UpdateActiveGenres(args.GenreFilter);
            this.UpdateActiveSubgenres(args.SubgenreFilter);
        }
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

