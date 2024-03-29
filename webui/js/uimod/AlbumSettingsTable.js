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

        this.hidealbuminput  = null;
        this.hidealbumrow    = null;
    }



    AddArtistNameRow()
    {
        this.newartistinfo   = new MessageBarInfo("Artist unknown. New artist will be created.");
        this.knownartistinfo = new MessageBarConfirm("Artist known. It already has an entry in the database.");
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
        this.importdateinput = new DateInput((value)=>{return this.ValidateImportDate(value);});
        this.importdaterow   = new AlbumSettingsTableRow(
            "Import Date",
            this.importdateinput,
            "Import date (like \"30.12.2021\")");
        this.AddRow(this.importdaterow);
    }

    AddHideAlbumRow()
    {
        this.hidealbuminput = new BooleanInput((value)=>{return true;}); // TODO
        this.hidealbumrow   = new AlbumSettingsTableRow(
            "Hide Album",
            this.hidealbuminput,
            "When the album is hidden, it will not be shown in the Artists list or considered as random music source.");
        this.AddRow(this.hidealbumrow);
    }



    ValidateArtistName(value)
    {
        if(value.length <= 0)
            return false;

        // New Artist?
        let artistslist = WebUI.GetManager("Artists").FindArtist(value, "strcmp");
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

        this.oldartistdir = new ArtistDirectoryName();
        this.newartistdir = new ArtistDirectoryName();
        this.oldalbumdir  = new AlbumDirectoryName();
        this.newalbumdir  = new AlbumDirectoryName();

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
        this.newartistdir.SetArtistName(artistname);
        this.newalbumdir.SetAlbumName(albumname);
        this.newalbumdir.SetReleaseYear(releaseyear, false); // do not validate for life preview

        // Check Parts
        let artistnameerror = this.newartistdir.CheckArtistName();
        let albumnameerror  = this.newalbumdir.CheckAlbumName();
        let releaseerror    = this.newalbumdir.CheckReleaseYear();

        // Compose Error Message
        let errors = "";
        if(artistnameerror)
            errors += `${artistnameerror} `;
        if(albumnameerror)
            errors += `${albumnameerror} `;
        if(releaseerror)
            errors += `${releaseerror}`;

        // Set Error if existing
        if(errors.length > 0)
            this.datainvalidmessage.Show();
        else
            this.datainvalidmessage.Hide();

        // Update diffs
        const grayspan  = `<span style="color: var(--color-gray)">`;
        const closespan = `</span>`;
        const grayslash = `${grayspan}/${closespan}`;
        const grayarrow = `${grayspan}&nbsp;➜&nbsp;${closespan}`;
        this.artistdiff.UpdateDiff(this.oldartistdir, this.newartistdir);
        this.albumdiff.UpdateDiff(this.oldalbumdir, this.newalbumdir);

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
        this.newpathelement.RemoveChilds();
        this.newpathelement.SetInnerHTML(pathdiff);

        // Check and propagate validation status
        let validationstatus = this.CheckIfValid();
        if(typeof this.validationstatuscallback === "function")
            this.validationstatuscallback(validationstatus);
        return;
    }



    GetArtistDirectoryName()
    {
        let artistname = this.artistnameinput.GetValue();
        artistname = this.newartistdir.MakeValidArtistName(artistname);
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

            let oldalbumdir = new AlbumDirectoryName(olddirectoryname);
            let newalbumdir = new AlbumDirectoryName(newdirectoryname);
            renamerequest.htmldiff= this.albumdiff.UpdateDiff(oldalbumdir, newalbumdir);
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

            let oldartistdir = new ArtistDirectoryName(olddirectoryname);
            let newartistdir = new ArtistDirectoryName(newdirectoryname);
            renamerequest.htmldiff= this.artistdiff.UpdateDiff(oldartistdir, newartistdir);
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

        this.oldartistdir = new ArtistDirectoryName(this.oldpath.split("/")[0]);
        this.oldalbumdir  = new AlbumDirectoryName( this.oldpath.split("/")[1]);

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
        this.oldorigin     = "";
        this.oldimportdate = "";
        this.oldhidealbum  = null;
        this.artistpath    = "";
        this.albnumid      = null;
        this.oldalbumname  = new AlbumDirectoryName();
        this.newalbumname  = new AlbumDirectoryName();
        this.albumdiff     = new AlbumDirectoryNameDiff();
        this.tasks         = new BatchExecution();
        this.tasks.SetListenSignature("ConfirmAlbumSettingsTask");
        this.tasks.SetOnFinishCallback((opentasks, finishedtasks)=>
            {
                this.onTasksFinished(opentasks, finishedtasks);
            });

        // Load / Save buttons
        this.loadbutton = new TextButton("Load", "Reset Table",
            ()=>{this.onLoad();},
            "Reset all changes made inside the album settings table.");
        this.savebutton = new TextButton("Save", "Save Changes",
            ()=>{this.onSave();},
            "Save all changes made inside the album settinsg tabke.\n"+
            "If the ablum name or release year has been changed,\n"+
            "the album directory inside the Music Diretory gets renamed as well.");
        this.toolbar   = new ToolBar();
        this.toolbar.AddButton(this.loadbutton);
        this.toolbar.AddSpacer(true /*grow*/);
        this.toolbar.AddButton(this.savebutton);

        this.datainvalidmessage = new MessageBarError("Invalid album directory name. Check red input fields.");
        this.changesmessage     = new MessageBarInfo("Changes in the settings table not yet saved.");
        this.newpathelement     = new Element("span");

        this.AddRow(this.headlinerow);
        this.AddAlbumNameRow();
        this.AddReleaseYearRow();
        this.AddRow(new TableSpanRow(3, [], this.newpathelement));
        this.AddOriginRow();
        this.AddImportDateRow();
        this.AddHideAlbumRow();
        this.AddRow(new TableSpanRow(3, [], this.changesmessage));
        this.AddRow(new TableSpanRow(3, [], this.datainvalidmessage));
        this.AddRow(new TableSpanRow(3, [], this.tasks));
        this.AddRow(new TableSpanRow(3, [], this.toolbar));

        this.albumnameinput.SetAfterValidateEventCallback(
            (value, valid)=>
            {
                this.EvaluateNewPath();
                this.CheckChanges();
            });
        this.releaseyearinput.SetAfterValidateEventCallback(
            (value, valid)=>
            {
                this.EvaluateNewPath();
                this.CheckChanges();
            });
        this.origininput.SetAfterValidateEventCallback(
            (value, valid)=>
            {
                this.CheckChanges();
            });
        this.importdateinput.SetAfterValidateEventCallback(
            (value, valid)=>
            {
                this.CheckChanges();
            });
        this.hidealbuminput.SetAfterValidateEventCallback(
            (value, valid)=>
            {
                this.CheckChanges();
            });

    }



    CheckChanges()
    {
        let origin       = this.origininput.GetValue();
        let importdate   = this.importdateinput.GetValue();
        let hidealbum    = this.hidealbuminput.GetValue();
        let olddirectory = this.oldalbumname.ComposeDirectoryName();
        let newdirectory = this.newalbumname.ComposeDirectoryName();

        let changes = false;
        if(hidealbum != this.oldhidealbum)
            changes = true;
        if(origin != this.oldorigin)
            changes = true;
        if(importdate != this.oldimportdate)
            changes = true;
        if(newdirectory != olddirectory)
            changes = true;

        if(changes)
        {
            this.changesmessage.Show();
            this.loadbutton.Enable();
            this.savebutton.Enable();
        }
        else
        {
            this.changesmessage.Hide();
            this.loadbutton.Disable();
            this.savebutton.Disable();
        }

        // Check if data is valid. If not, disable the save button
        let yearcheck = this.newalbumname.CheckReleaseYear();
        let namecheck = this.newalbumname.CheckAlbumName();

        if(yearcheck === null && namecheck === null)
        {
            this.datainvalidmessage.Hide();
            this.UpdateTasks();
        }
        else
        {
            this.datainvalidmessage.UpdateMessage(`${yearcheck||""} ${namecheck||""}`);
            this.datainvalidmessage.Show();
            this.savebutton.Disable();
            this.tasks.Clear(); // Just be sure to not mess up anything
        }
    }



    UpdateTasks()
    {
        let olddirectory = this.oldalbumname.ComposeDirectoryName();
        let newdirectory = this.newalbumname.ComposeDirectoryName();
        let origin       = this.origininput.GetValue();
        let importdate   = this.importdateinput.GetValue();
        let hidealbum    = this.hidealbuminput.GetValue();

        this.tasks.Clear();

        // Renaming includes updating name, release and origin of an album.
        // So to not override the origin settings, do renaming first.
        if(newdirectory != olddirectory)
        {
            let oldpath = `${this.artistpath}/${olddirectory}`;
            let newpath = `${this.artistpath}/${newdirectory}`;
            this.tasks.AddTask(`Rename Album Directory to "${newdirectory}"`,
                (webuitaskid)=>
                {
                    MusicDB.Request("RenameAlbumDirectory", "ConfirmAlbumSettingsTask",
                        {oldpath: oldpath, newpath: newpath},
                        {webuitaskid: webuitaskid});
                    return "active";
                },
                (fnc, sig, args, pass)=>
                {
                    if(args === true) return "good";
                    else              return "bad";
                },
                null /*on notification*/, true /*can fail*/);
        }
        if(origin != this.oldorigin)
        {
            this.tasks.AddTask(`Update Origin to ${origin}`,
                (webuitaskid)=>
                {
                    MusicDB.Request("SetAlbumOrigin", "ConfirmAlbumSettingsTask",
                        {albumid: this.albumid, origin: origin},
                        {webuitaskid: webuitaskid});
                },
                (fnc, sig, args, pass)=>
                {
                    return "good";
                },
                null /*on notification*/, true /*can fail*/);
        }
        if(importdate != this.oldimportdate)
        {
            this.tasks.AddTask("Update Import Date",
                (webuitaskid)=>
                {
                    MusicDB.Request("SetAlbumImportTime", "ConfirmAlbumSettingsTask",
                        {albumid: this.albumid, importtime: importdate},
                        {webuitaskid: webuitaskid});
                },
                (fnc, sig, args, pass)=>
                {
                    return "good";
                },
                null /*on notification*/, true /*can fail*/);
        }
        if(hidealbum != this.oldhidealbum)
        {
            this.tasks.AddTask("Update Hide-Album State",
                (webuitaskid)=>
                {
                    // This needs to be a broadcast to all clients to make them update
                    MusicDB.Broadcast("HideAlbum", "UpdateArtists",
                        {albumid: this.albumid, hide: hidealbum});
                    // Dummy call to trigger batch execution
                    MusicDB.Request("Bounce", "ConfirmAlbumSettingsTask",
                        {},
                        {webuitaskid: webuitaskid});
                },
                (fnc, sig, args, pass)=>
                {
                    return "good";
                },
                null /*on notification*/, true /*can fail*/);
        }

        // If renaming took place, update all instances of the WebUI
        if(newdirectory != olddirectory)
        {
            // Force all WebUIs reloading their album information (broadcast)
            this.tasks.AddTask("Propagate new album directory to all clients",
                (webuitaskid)=>
                {
                    // Propagate album renaming to all clients
                    MusicDB.Broadcast("GetAlbum", "AlbumRenamed",
                        {albumid: this.albumid});
                    // Dummy call to trigger batch execution
                    MusicDB.Request("Bounce", "ConfirmAlbumSettingsTask",
                        {},
                        {webuitaskid: webuitaskid});
                },
                (fnc, sig, args, pass)=>
                {
                    return "good";
                },
                null /*on notification*/, true /*can fail*/);
        }

        return;
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

        return;
    }



    onLoad()
    {
        this.albumnameinput.SetValue(this.oldalbumname.parts.name);
        this.releaseyearinput.SetValue(this.oldalbumname.parts.year);
        this.origininput.SetValue(this.oldorigin);
        this.importdateinput.SetValue(this.oldimportdate);
    }

    onSave()
    {
        this.loadbutton.Disable();
        this.savebutton.Disable();
        this.UpdateTasks(); // Just make sure all changes are considered
        this.tasks.ExecuteTasks();
    }

    onTasksFinished(opentasks, finishedtasks)
    {
        if(opentasks.length === 0)
        {
            // All tasks successfully processed.
            // Refresh whole view
            this.changesmessage.Hide();
            this.tasks.Clear();
            MusicDB.Request("GetAlbum", "ShowAlbumSettingsLayer", {albumid: this.albumid});
        }
        else
        {
            // Save has been tried without success. User should change something or reload.
            this.savebutton.Disable();
        }
    }



    Update(MDBArtist, MDBAlbum)
    {
        this.oldpath       = MDBAlbum.path
        this.oldorigin     = MDBAlbum.origin;
        this.oldimportdate = MDBAlbum.added;
        this.oldhidealbum  = MDBAlbum.hidden;
        this.artistpath    = MDBArtist.path;
        this.albumid       = MDBAlbum.id;

        this.oldalbumname = new AlbumDirectoryName( this.oldpath.split("/")[1]);

        this.albumnameinput.SetValue(MDBAlbum.name);
        this.releaseyearinput.SetValue(MDBAlbum.release);
        this.origininput.SetValue(MDBAlbum.origin);
        this.importdateinput.SetValue(MDBAlbum.added);

        this.CheckChanges(); // Reset State
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        if(sig == "ConfirmAlbumSettingsTask")
        {
            this.tasks?.onMusicDBMessage(fnc, sig, args, pass);
        }
    }
    onMusicDBNotification(fnc, sig, rawdata)
    {
        this.tasks?.onMusicDBNotification(fnc, sig, rawdata);
    }
}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

