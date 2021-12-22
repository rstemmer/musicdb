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
        this.SetContent(AST_SETTINGS_COLUMN,    input);
        this.SetContent(AST_DESCRIPTION_COLUMN, descriptionnode);
    }
}



class AlbumSettingsTable extends Table
{
    constructor()
    {
        super(["AlbumSettingsTable"]);
        this.headlinerow     = new AlbumSettingsTableHeadline();

        this.newartistinfos  = null;
        this.knownartistinfo = null;
        this.artistnameinput = null;
        this.artistnamerow   = null;

        this.albumnameinput  = null;
        this.albumnamerow    = null;

        this.releaseyearinput= null;
        this.releaseyearrow  = null;

        this.origininput     = null;
        this.originrow       = null;

        this.importdateinput = null;
        this.importdaterow   = null;
    }



    AddArtistNameRow()
    {
        this.newartistinfo   = new MessageBarInfo("Artist unknown. New artist will be created.");
        this.newartistinfo.HideCloseButton();
        this.knownartistinfo = new MessageBarConfirm("Artist known. It already has an entry in the database.");
        this.knownartistinfo.HideCloseButton();
        let  artistinfos     = new Element("div", ["flex-column"]);
        artistinfos.AppendChild(this.newartistinfo);
        artistinfos.AppendChild(this.knownartistinfo);

        this.artistnameinput = new TextInput((value)=>{return this.ValidateArtistName(value);});

        this.artistnamerow   = new AlbumSettingsTableRow(
            "Artist Name",
            this.artistnameinput,
            "Correct name of the album artist");

        this.AddRow(this.artistnamerow   );
        this.AddRow(new TableSpanRow(3, [], artistinfos));
    }

    AddAlbumNameRow()
    {
        this.albumnameinput = new TextInput((value)=>{return this.ValidateAlbumName(value);});
        this.albumnamerow   = new AlbumSettingsTableRow(
            "Album Name",
            this.albumnameinput,
            "Correct name of the album (without release year)");
        this.AddRow(this.albumnamerow);
    }

    AddReleaseYearRow()
    {
        this.releaseyearinput = new NumberInput((value)=>{return this.ValidateReleaseYear(value);});
        this.releaseyearrow   = new AlbumSettingsTableRow(
            "Release Year",
            this.releaseyearinput,
            "Release year with 4 digits (like \"2021\")");
        this.AddRow(this.releaseyearrow);
    }

    AddOriginRow()
    {
        this.origininput        = new TextInput(  (value)=>{return this.ValidateOrigin(value);      });
        this.originrow = new AlbumSettingsTableRow(
            "Album Origin",
            this.origininput,
            "Where the data comes from (like \"internet\", \"iTunes\", \"bandcamp\", \"CD\")");
        this.AddRow(this.originrow);
    }

    AddImportDateRow()
    {
        this.importdateinput    = new TextInput(  (value)=>{return this.ValidateImportDate(value);  });
        this.importdaterow = new AlbumSettingsTableRow(
            "Import Date",
            this.importdateinput,
            "Import date (like \"30.12.2021\")");
        this.AddRow(this.importdaterow);
    }



    ValidateArtistName(value)
    {
        if(value.length <= 0)
            return false;

        // New Artist?
        let artistslist = artistscache.FindArtist(value, "strcmp");
        if(artistslist.length == 1)
        {
            this.knownartistinfo.UpdateMessage(`Artist "${value}" known. It already has an entry in the database.`);
            this.knownartistinfo.Show();
            this.newartistinfo.Hide();
        }
        else
        {
            this.newartistinfo.UpdateMessage(`Artist "${value}" unknown. New artist will be created.`);
            this.newartistinfo.Show();
            this.knownartistinfo.Hide();
        }
        return true;
    }

    ValidateAlbumName(value)
    {
        if(value.length <= 0)
            return false;
        return true;
    }

    ValidateReleaseYear(value)
    {
        let thisyear = new Date().getFullYear();

        if(value < 1000 || value > thisyear)
            return false
        return true;
    }

    ValidateOrigin(value)
    {
        if(value.length <= 0)
            return false;
        return true;
    }

    ValidateImportDate(value)
    {
        return true;
    }
}



class AlbumPathSettingsTable extends AlbumSettingsTable
{
    // validationstatuscallback if a function called whenever data is validated.
    // It gets one argument (boolean) that, if true, tells that all data in this table is valid.
    constructor(validationstatuscallback)
    {
        super();
        this.validationstatuscallback = validationstatuscallback;
        this.oldpath = "";

        this.oldartistname = new ArtistDirectoryName();
        this.newartistname = new ArtistDirectoryName();
        this.oldalbumname  = new AlbumDirectoryName();
        this.newalbumname  = new AlbumDirectoryName();

        this.artistdiff    = new ArtistDirectoryNameDiff();
        this.albumdiff     = new AlbumDirectoryNameDiff();

        this.AddRow(this.headlinerow);
        this.AddArtistNameRow();
        this.AddAlbumNameRow();
        this.AddReleaseYearRow();

        this.artistnameinput.SetAfterValidateEventCallback( (value, valid)=>{this.EvaluateNewPath();});
        this.albumnameinput.SetAfterValidateEventCallback(  (value, valid)=>{this.EvaluateNewPath();});
        this.releaseyearinput.SetAfterValidateEventCallback((value, valid)=>{this.EvaluateNewPath();});

        this.datainvalidmessage = new MessageBarError("Invalid Album Settings. Check red input fields.");

        // Table
        this.newpathelement = new Element("span");

        this.AddRow(new TableSpanRow(3, [], this.newpathelement));
        this.AddRow(new TableSpanRow(3, [], this.datainvalidmessage));
    }



    CheckIfValid()
    {
        if(this.artistnameinput.GetValidState() == false)
            return false;
        if(this.albumnameinput.GetValidState() == false)
            return false;
        if(this.releaseyearinput.GetValidState() == false)
            return false;
        return true;
    }



    EvaluateNewPath()
    {
        // Get new values
        let artistname  = this.artistnameinput.GetValue();
        let albumname   = this.albumnameinput.GetValue();
        let releaseyear = this.releaseyearinput.GetValue();

        // Update new*name objects
        this.newartistname.SetArtistName(artistname);
        this.newalbumname.SetAlbumName(albumname);
        this.newalbumname.SetReleaseYear(releaseyear, false); // do not validate for life preview

        // Update diffs
        this.artistdiff.UpdateDiff(this.oldartistname, this.newartistname);
        this.albumdiff.UpdateDiff(this.oldalbumname, this.newalbumname);

        // Full path diff
        const grayspan  = `<span style="color: var(--color-gray)">`;
        const closespan = `</span>`;
        const grayslash = `${grayspan}/${closespan}`;
        const grayarrow = `${grayspan}&nbsp;➜&nbsp;${closespan}`;

        let oldpathhtml = "";
        oldpathhtml += this.artistdiff.olddiff;
        oldpathhtml += grayslash;
        oldpathhtml += this.albumdiff.olddiff;
        let newpathhtml = "";
        newpathhtml += this.artistdiff.newdiff;
        newpathhtml += grayslash;
        newpathhtml += this.albumdiff.newdiff;

        let pathdiff = "";
        if(oldpathhtml != newpathhtml)
            pathdiff = `${oldpathhtml}${grayarrow}${newpathhtml}`;
        else
            pathdiff = newpathhtml;

        // Update visualisation of path validation
        this.newpathelement.RemoveChilds();
        this.newpathelement.SetInnerHTML(pathdiff);

        // Check and propagate validation status
        let validationstatus = this.CheckIfValid();
        if(validationstatus !== true)
            this.datainvalidmessage.Show();
        else
            this.datainvalidmessage.Hide();

        if(typeof this.validationstatuscallback === "function")
            this.validationstatuscallback(validationstatus);
        return;
    }



    GetArtistDirectoryName()
    {
        let artistname = this.artistnameinput.GetValue();
        artistname = this.newartistname.MakeValidArtistName(artistname);
        return artistname;
    }

    GetAlbumDirectoryName()
    {
        let releaseyear = this.releaseyearinput.GetValue();
        let albumname   = this.albumnameinput.GetValue();
        let albumdirectoryname = new AlbumDirectoryName();

        albumdirectoryname.SetReleaseYear(releaseyear);
        albumdirectoryname.SetAlbumName(albumname);

        return albumdirectoryname.ComposeDirectoryName();
    }



    // Returns an object with two attributes: .newname, .oldname
    GetAlbumRenameRequest()
    {
        let newdirectoryname  = this.GetAlbumDirectoryName();
        let olddirectoryname  = this.oldpath.split("/")[1];
        if(olddirectoryname === undefined)
            return null;

        let renamerequest = null;
        if(newdirectoryname != olddirectoryname)
        {
            renamerequest = new Object();
            renamerequest.newname = newdirectoryname;
            renamerequest.oldname = olddirectoryname;
            renamerequest.htmldiff= this.albumdiff;
        }
        return renamerequest;
    }
    GetArtistRenameRequest()
    {
        let newdirectoryname  = this.GetArtistDirectoryName();
        let olddirectoryname  = this.oldpath.split("/")[0];
        if(olddirectoryname === undefined)
            return null;

        let renamerequest = null;
        if(newdirectoryname != olddirectoryname)
        {
            renamerequest = new Object();
            renamerequest.newname = newdirectoryname;
            renamerequest.oldname = olddirectoryname;
            renamerequest.htmldiff= this.artistdiff;
        }
        return renamerequest;
    }


    // When albumpath is not set, then it gets generated by the following scheme:
    //  ${artistname}/${releasedate} - ${albumname}
    Update(artistname, albumname, releasedate, albumpath=null)
    {
        if(albumpath === null)
            this.oldpath = `${artistname}/${releasedate} - ${albumname}`;
        else
            this.oldpath = albumpath;

        this.oldartistname = new ArtistDirectoryName(this.oldpath.split("/")[0]);
        this.oldalbumname  = new AlbumDirectoryName( this.oldpath.split("/")[1]);

        this.artistnameinput.SetValue(artistname);
        this.albumnameinput.SetValue(albumname);
        this.releaseyearinput.SetValue(releasedate);
    }
}



/*
 * Adds origin and import date settings
 * Handles path renaming internal by providing a "Rename" button
 *   using the RenameAlbumDirectory API
 */
class AlbumEntrySettingsTable extends AlbumSettingsTable
{
    constructor()
    {
        super();
        this.oldpath = "";
        this.oldalbumname  = new AlbumDirectoryName();
        this.newalbumname  = new AlbumDirectoryName();
        this.albumdiff     = new AlbumDirectoryNameDiff();

        this.datainvalidmessage = new MessageBarError("Invalid album directory name. Check red input fields.");
        this.newpathelement     = new Element("span");

        this.AddRow(this.headlinerow);
        this.AddAlbumNameRow();
        this.AddReleaseYearRow();
        this.AddRow(new TableSpanRow(3, [], this.newpathelement));
        this.AddRow(new TableSpanRow(3, [], this.datainvalidmessage));
        this.AddOriginRow();
        this.AddImportDateRow();

        this.albumnameinput.SetAfterValidateEventCallback(  (value, valid)=>{return this.EvaluateNewPath();});
        this.releaseyearinput.SetAfterValidateEventCallback((value, valid)=>{return this.EvaluateNewPath();});

    }



    EvaluateNewPath()
    {
        // Get new values
        let albumname   = this.albumnameinput.GetValue();
        let releaseyear = this.releaseyearinput.GetValue();

        // Update new*name objects
        this.newalbumname.SetAlbumName(albumname);
        this.newalbumname.SetReleaseYear(releaseyear, false); // do not validate for life preview

        // Update diffs
        this.albumdiff.UpdateDiff(this.oldalbumname, this.newalbumname);

        // Full path diff
        const grayspan  = `<span style="color: var(--color-gray)">`;
        const closespan = `</span>`;
        const grayslash = `${grayspan}/${closespan}`;
        const grayarrow = `${grayspan}&nbsp;➜&nbsp;${closespan}`;

        let oldpathhtml = this.albumdiff.olddiff;
        let newpathhtml = this.albumdiff.newdiff;
        let pathdiff    = "";
        if(oldpathhtml != newpathhtml)
            pathdiff = `${oldpathhtml}${grayarrow}${newpathhtml}`;
        else
            pathdiff = newpathhtml;

        // Update visualisation of path validation
        this.newpathelement.RemoveChilds();
        this.newpathelement.SetInnerHTML(pathdiff);

        // Check and propagate validation status
        let yearcheck = this.newalbumname.CheckReleaseYear();
        let namecheck = this.newalbumname.CheckAlbumName();

        if(yearcheck === null && namecheck === null)
        {
            this.datainvalidmessage.Hide();
        }
        else
        {
            this.datainvalidmessage.UpdateMessage(`${yearcheck||""} ${namecheck||""}`);
            this.datainvalidmessage.Show();
        }

        return;
    }



    Update(artistname, albumname, releasedate, albumpath, origin, importdate)
    {
        this.oldpath = albumpath;

        this.oldalbumname = new AlbumDirectoryName( this.oldpath.split("/")[1]);

        this.albumnameinput.SetValue(albumname);
        this.releaseyearinput.SetValue(releasedate);
        this.origininput.SetValue(origin);
        this.importdateinput.SetValue(importdate);
    }



}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

