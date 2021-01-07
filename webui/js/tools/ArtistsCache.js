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

class ArtistsCache
{
    constructor()
    {
        this.artists = null;
    }



    UpdateCache(MDBArtistsList)
    {
        this.artists = MDBArtistsList;
    }



    GetArtists()
    {
        return this.artists;
    }



    // valid algorithms: "Levenshtein", "strcmp"
    // Returns a list of MDBArtist entries
    FindArtist(searchstring, algorithm="Levenshtein")
    {
        let results = new Array();

        // strcmp
        if(algorithm == "strcmp")
        {
            for(let artist of this.artists)
                if(artist.name === searchstring)
                    return [artist]
            return [];
        }

        // Levenshtein
        for(let artist of this.artists)
        {
            let artistname = artist.name;
            let similarity = Similarity(searchstring, artistname);
            if(similarity > 0.5)
                results.push(artist);
        }

        return results;
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        if(fnc == "GetArtists")
        {
            this.UpdateCache(args);
        }
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

