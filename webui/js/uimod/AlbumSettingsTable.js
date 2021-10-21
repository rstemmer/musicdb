// MusicDB,  a music manager with web-bases UI that focus on music.
// Copyright (C) 2017 - 2021  Ralf Stemmer <ralf.stemmer@gmx.net>
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
const ALBUMSETTINGSHEADLINE = ["Property", "Settings", "Description"];
const AST_LABEL_COLUMN       = 0;
const AST_SETTINGS_COLUMN    = 1;
const AST_DESCRIPTION_COLUMN = 2;



class AlbumSettingsTableRowBase extends TableRow
{
    constructor()
    {
        super(ALBUMSETTINGSHEADLINE.length, ["AlbumSettingsTableRow"]);
    }
}


class AlbumSettingsTableHeadline extends AlbumSettingsTableRowBase
{
    constructor()
    {
        super();
        this.AddCSSClass("TableHeadline");

        for(let cellnum in ALBUMSETTINGSHEADLINE)
        {
            let headline = document.createTextNode(ALBUMSETTINGSHEADLINE[cellnum]);
            this.SetContent(cellnum, headline);
        }
    }
}


class AlbumSettingsTableRow extends AlbumSettingsTableRowBase
{
    constructor(label, input, description="")
    {
        super();
        let labelnode       = document.createTextNode(label);
        let descriptionnode = document.createTextNode(description);
        this.SetContent(AST_LABEL_COLUMN,       labelnode);
        this.SetContent(AST_SETTINGS_COLUMN,    input.GetHTMLElement());
        this.SetContent(AST_DESCRIPTION_COLUMN, descriptionnode);
    }
}



class AlbumSettingsTable extends Table
{
    constructor()
    {
        super(["AlbumSettingsTable"]);

        // Text Inputs
        this.artistnameinput     = new TextInput(  (value)=>{return this.ValidateArtistName(value);  });
        this.albumnameinput      = new TextInput(  (value)=>{return this.ValidateAlbumName(value);   });
        this.releasedateinput    = new NumberInput((value)=>{return this.ValidateReleaseDate(value); });
        this.origininput         = new TextInput(  (value)=>{return this.ValidateOrigin(value);      });
        this.importartworkinput  = new SVGCheckBox(null);
        this.importlyricsinput   = new SVGCheckBox(null);

        this.artistnameinput.SetAfterValidateEventCallback( (value, valid)=>{return this.EvaluateNewPath();});
        this.albumnameinput.SetAfterValidateEventCallback(  (value, valid)=>{return this.EvaluateNewPath();});
        this.releasedateinput.SetAfterValidateEventCallback((value, valid)=>{return this.EvaluateNewPath();});

        // Table
        this.headlinerow  = new AlbumSettingsTableHeadline();
        this.artistnamerow = new AlbumSettingsTableRow(
            "Artist Name",
            this.artistnameinput,
            "Correct name of the album artist");
        this.albumnamerow = new AlbumSettingsTableRow(
            "Album Name",
            this.albumnameinput,
            "Correct name of the album (without release year)");
        this.releasedaterow = new AlbumSettingsTableRow(
            "Release Date",
            this.releasedateinput,
            "Release year with 4 digits (like \"2021\")");
        this.originrow = new AlbumSettingsTableRow(
            "File Origin",
            this.origininput,
            "Where the file comes from. For example: \"iTunes\", \"bandcamp\", \"Amazon\", \"Google\", \"CD\", \"internet\"");
        this.importartworkrow = new AlbumSettingsTableRow(
            "Import Artwork",
            this.importartworkinput,
            "Try to import the album artwork from a song file");
        this.importlyricsrow = new AlbumSettingsTableRow(
            "Import Lyrics",
            this.importlyricsinput,
            "Try to import the lyrics from the song files");

        this.newpathelement = new Element("span");
        let  newpathnode    = this.newpathelement.GetHTMLElement();

        this.AddRow(this.headlinerow     );
        this.AddRow(this.artistnamerow   );
        this.AddRow(this.albumnamerow    );
        this.AddRow(this.releasedaterow  );
        this.AddRow(this.originrow       );
        this.AddRow(this.importartworkrow);
        this.AddRow(this.importlyricsrow );
        this.AddRow(new TableSpanRow(3, [], newpathnode));
    }



    ValidateArtistName(value)
    {
        return true;
    }
    ValidateAlbumName(value)
    {
        return true;
    }
    ValidateReleaseDate(value)
    {
        let thisyear = new Date().getFullYear();

        if(value < 1000 || value > thisyear)
            return false
        return true;
    }
    ValidateOrigin(value)
    {
        return true;
    }



    EvaluateNewPath()
    {
        const validspan = `<span style="color: var(--color-brightgreen)">`;
        const errorspan = `<span style="color: var(--color-brightred)">`;
        const grayspan  = `<span style="color: var(--color-gray)">`;
        const closespan = `</span>`;

        let newpathtext = "";
        let newpathhtml = "";

        // Artist
        let artistname = this.artistnameinput.GetValue();
        artistname = artistname.replace(/\//g,"∕" /*Division slash*/);
        if(this.artistnameinput.GetValidState() === true)
            newpathhtml += validspan;
        else
            newpathhtml += errorspan;
        newpathtext += `${artistname}/`;
        newpathhtml += `${artistname}${closespan}${grayspan}/${closespan}`;

        // Release Year
        let releaseyear = this.releasedateinput.GetValue();
        if(this.releasedateinput.GetValidState() === true)
            newpathhtml += validspan;
        else
            newpathhtml += errorspan;
        newpathtext += `${releaseyear} - `;
        newpathhtml += `${releaseyear} - ${closespan}`;

        // Album name
        let albumname = this.albumnameinput.GetValue();
        albumname = albumname.replace(/\//g,"∕" /*Division slash*/);
        if(this.albumnameinput.GetValidState() === true)
            newpathhtml += validspan;
        else
            newpathhtml += errorspan;
        newpathtext += `${albumname}`;
        newpathhtml += `${albumname}${closespan}`;

        // Show old file name if the new one is different
        let oldpathparts = this.oldalbumpath.split("/");
        let newpathparts = newpathtext.split("/");
        let oldpathhtml  = "";

        if(oldpathparts[0] != newpathparts[0])
            oldpathhtml  = `${errorspan}${oldpathparts[0]}${closespan}${grayspan}/${closespan}`
        else
            oldpathhtml  = `${grayspan}${oldpathparts[0]}/${closespan}`

        if(oldpathparts[1] != newpathparts[1])
            oldpathhtml  += `${errorspan}${oldpathparts[1]}${closespan}${grayspan}/${closespan}`
        else
            oldpathhtml  += `${grayspan}${oldpathparts[1]}/${closespan}`

        if(this.oldalbumpath != newpathtext)
            newpathhtml = `${oldpathhtml}${grayspan} ➜ ${newpathhtml}${closespan}`;

        this.newpathelement.RemoveChilds();
        this.newpathelement.SetInnerHTML(newpathhtml);
        return newpathtext;
    }



    GetArtistDirectoryName()
    {
        let artistname = this.artistnameinput.GetValue();
        artistname = artistname.replace(/\//g,"∕" /*Division slash*/);
        return artistname;
    }

    GetAlbumDirectoryName()
    {
        // Release Year
        let releaseyear = this.releasedateinput.GetValue();
        let albumname   = this.albumnameinput.GetValue();
        albumname = albumname.replace(/\//g,"∕" /*Division slash*/);
        return `${releaseyear} - ${albumname}`;
    }



    // Returns a array with two objects with two attributes: .newname, .oldname
    // First object is for the artist, second for the album directory name
    // If for one or all of them the directories are the same, null will be set instead of an object.
    GetRenameRequests()
    {
        let newartistdirectoryname = this.GetArtistDirectoryName();
        let newalbumdirectoryname  = this.GetAlbumDirectoryName();
        let oldartistdirectoryname = this.oldalbumpath.split("/")[0];
        let oldalbumdirectoryname  = this.oldalbumpath.split("/")[1];

        let renamerequests = new Array();
        let artistrenamerequest = null;
        let albumrenamerequest  = null;
        if(newartistdirectoryname != oldartistdirectoryname)
        {
            artistrenamerequest = new Object();
            artistrenamerequest.newpath = newartistdirectoryname;
            artistrenamerequest.oldpath = oldartistdirectoryname;
        }
        if(newalbumdirectoryname != oldalbumdirectoryname)
        {
            albumrenamerequest = new Object();
            albumrenamerequest.newpath = newalbumdirectoryname;
            albumrenamerequest.oldpath = oldalbumdirectoryname;
        }
        renamerequests.push(artistrenamerequest);
        renamerequests.push(albumrenamerequest);

        return renamerequests;
    }



    Update(artistname, albumname, releasedate, origin, hasartwork, haslyrics, albumpath)
    {
        this.oldalbumpath = albumpath;
        this.artistnameinput.SetValue(artistname);
        this.albumnameinput.SetValue(albumname);
        this.releasedateinput.SetValue(releasedate);
        this.origininput.SetValue(origin);
        this.importartworkinput.SetSelectionState(hasartwork);
        this.importlyricsinput.SetSelectionState(haslyrics);
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

