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

        this.AddRow(this.headlinerow     );
        this.AddRow(this.artistnamerow   );
        this.AddRow(this.albumnamerow    );
        this.AddRow(this.releasedaterow  );
        this.AddRow(this.originrow       );
        this.AddRow(this.importartworkrow);
        this.AddRow(this.importlyricsrow );
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



    Update(artistname, albumname, releasedate, origin, hasartwork, haslyrics)
    {
        this.artistnameinput.SetValue(artistname);
        this.albumnameinput.SetValue(albumname);
        this.releasedateinput.SetValue(releasedate);
        this.origininput.SetValue(origin);
        this.importartworkinput.SetSelectionState(hasartwork);
        this.importlyricsinput.SetSelectionState(haslyrics);
    }
}


class AlbumImportLayer extends Layer
{
    // background: Instance of the Curtain class that lays behind the Layer.
    // When the layer is made visible, then also the background will be shown
    constructor(background, id)
    {
        super(background, id)
        this.albumsettingstable = new AlbumSettingsTable()
        this.AppendChild(this.albumsettingstable);
    }




    onMusicDBMessage(fnc, sig, args, pass)
    {
        if(fnc == "FindAlbumSongFiles" && sig == "ShowAlbumSongFiles")
        {
            window.console?.log(args);
            this.albumsettingstable.Update(
                args[0].artistname,
                args[0].albumname,
                args[0].releaseyear,
                args[0].origin,
                args[0].hasartwork,
                args[0].haslyrics);
        }
    }
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
