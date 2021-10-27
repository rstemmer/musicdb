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


class AlbumImportTasks extends Element
{
    constructor()
    {
        super("div", ["AlbumImportTaks"]);
        this.tasks = new BatchExecution();
    }



    AddTask(htmllabel, taskfunction, resultevalfunction, notificationfunction=null)
    {
        let task = this.tasks.AddTask(htmllabel, taskfunction, resultevalfunction, notificationfunction);
        this.AppendChild(task["statuselement"]);
    }



    SetListenSignature(signature)
    {
        this.tasks.SetListenSignature(signature);
    }



    Clear()
    {
        this.tasks.Clear();
        this.RemoveChilds();
    }



    ExecuteTasks()
    {
        this.tasks.ExecuteTasks();
    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        this.tasks.onMusicDBMessage(fnc, sig, args, pass);
    }

    onMusicDBNotification(fnc, sig, rawdata)
    {
        this.tasks.onMusicDBNotification(fnc, sig, rawdata);
    }
}



class AlbumImportLayer extends Layer
{
    // background: Instance of the Curtain class that lays behind the Layer.
    // When the layer is made visible, then also the background will be shown
    constructor(background, id)
    {
        super(background, id)

        this.oldartistdirectoryname = null;
        this.oldalbumdirectoryname  = null;

        // Message Bar
        this.invalidsourceinfo  = new MessageBarError("Invalid Album Source. There were no songs in the selected Album directory.");
        this.invalidsourceinfo.HideCloseButton();

        // Forms
        this.albumsettingstable = new AlbumSettingsTable((isvalid)=>{this.onAlbumSettingsValidation(isvalid);});
        this.songfilestable     = new SongFilesTable((isvalid)=>{this.onSongsSettingsValidation(isvalid);});
        this.tasks              = new AlbumImportTasks();
        this.tasks.SetListenSignature("ConfirmAlbumImportTask");

        // Tool Bar
        this.toolbar            = new ToolBar();
        this.cancelbutton       = new TextButton("MusicDB", "Cancel and Discard",
            ()=>{this.onClick_Cancel();},
            "Cancel album import. Nothing will be changed.");
        this.importbutton       = new TextButton("MusicDB", "Import Album",
            ()=>{this.onClick_Rename();},
            "Apply rename files and directories properly and import album into database. Create artis if not existing.");

        this.toolbar.AddButton(this.cancelbutton);
        this.toolbar.AddSpacer(true); // grow
        this.toolbar.AddButton(this.importbutton);

        this.AppendChild(this.invalidsourceinfo);
        this.AppendChild(this.albumsettingstable);
        this.AppendChild(this.songfilestable);
        this.AppendChild(this.tasks);
        this.AppendChild(this.toolbar);
    }



    onClick_Cancel()
    {
        this.Hide();
    }

    onClick_Rename()
    {
        this.tasks.ExecuteTasks();
    }



    onAlbumSettingsValidation(isvalid)
    {
        this.ValidateForm();
    }
    onSongsSettingsValidation(isvalid)
    {
        this.ValidateForm();
    }
    ValidateForm()
    {
        let albumvalid = this.albumsettingstable.CheckIfValid();
        let songsvalid = this.songfilestable.CheckIfValid();

        this.PrepareImportTasks();

        if(albumvalid && songsvalid)
            this.importbutton.Enable();
        else
            this.importbutton.Disable();
    }



    PrepareImportTasks()
    {
        this.tasks.Clear();

        // If there is no valid source artist or album, do nothing.
        if(this.oldartistdirectoryname === null || this.oldalbumdirectoryname === null)
        {
            return;
        }

        // Song Renaming Tasks
        let songrenamerequests  = this.songfilestable.GetRenameRequests();
        let albumdirectoryname  = this.oldalbumdirectoryname;
        let olddirectory        = this.oldartistdirectoryname + "/" + albumdirectoryname;
        let artistdirectoryname = this.oldartistdirectoryname;

        // Rename all song files
        for(let songrenamerequest of songrenamerequests)
        {
            let oldpath  = olddirectory + "/" + songrenamerequest.oldname;
            let newpath  = olddirectory + "/" + songrenamerequest.newname;
            let htmldiff = songrenamerequest.htmldiff;

            this.tasks.AddTask(`Rename Song:&nbsp;${htmldiff}`,
                (webuitaskid)=>{
                    MusicDB_Request("RenameMusicFile", "ConfirmAlbumImportTask",
                        {oldpath: oldpath, newpath: newpath},
                        {webuitaskid: webuitaskid});
                    return "active";},
                (fnc, sig, args, pass)=>{
                    if(args === true) return "good";
                    else              return "bad";
                }
                );
        }

        // Rename album directory if needed
        let albumrenamerequest = this.albumsettingstable.GetAlbumRenameRequest();
        if(albumrenamerequest != null)
        {
            let oldalbumpath = this.oldartistdirectoryname + "/" + albumrenamerequest.oldname;
            let newalbumpath = this.oldartistdirectoryname + "/" + albumrenamerequest.newname;
            let htmldiff     = albumrenamerequest.htmldiff;
            this.tasks.AddTask(`Rename Album:&nbsp;${htmldiff}`,
                (webuitaskid)=>{
                    MusicDB_Request("RenameAlbumDirectory", "ConfirmAlbumImportTask",
                        {oldpath: oldalbumpath, newpath: newalbumpath},
                        {webuitaskid: webuitaskid});
                    return "active";},
                (fnc, sig, args, pass)=>{
                    if(args === true) return "good";
                    else              return "bad";
                }
                );

            // Update album directory to the new expected name
            albumdirectoryname = albumrenamerequest.newname;
        }

        // Change artist directory if needed
        let artistrenamerequest = this.albumsettingstable.GetArtistRenameRequest();
        if(artistrenamerequest != null)
        {
            let oldartistpath = artistrenamerequest.oldname;
            let newartistpath = artistrenamerequest.newname;
            let oldalbumpath  = oldartistpath + "/" + albumdirectoryname;
            let htmldiff      = artistrenamerequest.htmldiff;
            this.tasks.AddTask(`Change Artist:&nbsp;${htmldiff}`,
                (webuitaskid)=>{
                    MusicDB_Request("ChangeArtistDirectory", "ConfirmAlbumImportTask",
                        {oldalbumpath: oldalbumpath, newartistdirectory: newartistpath},
                        {webuitaskid: webuitaskid});
                    return "active";},
                (fnc, sig, args, pass)=>{
                    if(args === true) return "good";
                    else              return "bad";
                }
                );

            artistdirectoryname = artistrenamerequest.newname;
        }

        // Check if Artist needs to be created
        let artistslist = artistscache.FindArtist(artistdirectoryname, "strcmp");
        if(artistslist.length !== 1)
        {
            this.tasks.AddTask(`Create Artist: ${artistdirectoryname}`,
                (webuitaskid)=>{
                    MusicDB_Request("CreateArtist", "ConfirmAlbumImportTask",
                        {name: artistdirectoryname},
                        {webuitaskid: webuitaskid});
                    return "active";},
                (fnc, sig, args, pass)=>{
                    if(typeof args?.id === "number")
                        return "good";
                    else
                        return "bad";
                }
                );
        }

        // Import Album
        let newalbumpath = artistdirectoryname + "/" + albumdirectoryname;
        this.tasks.AddTask("Import Album",
            (webuitaskid)=>{
                MusicDB_Request("InitiateMusicImport", "ConfirmAlbumImportTask",
                    {contenttype: "album", contentpath: newalbumpath},
                    {webuitaskid: webuitaskid});
                return "active";
            },
            (fnc, sig, args, pass)=>{
                if(args == null)
                    return "bad";
                else
                {
                    window.console?.log(`New MusicDB Task ID: ${args}`);
                    return "active";
                }
            },
            (fnc, sig, rawdata)=>{
                if(fnc != "MusicDB:Upload")
                    return null;

                if(sig == "InternalError")
                {
                    window.console?.warn(`Importing Album failed with error: "${rawdata["message"]}"`)
                    return "bad";
                }
                if(sig == "StateUpdate")
                {
                    if(rawdata["state"] == "importfailed")
                        return "bad";
                    else if(rawdata["state"] == "importcomplete")
                        return "good";
                }
                return "active";
            }
            );

        // Import Artwork
        if(this.albumsettingstable.GetImportArtworkState() === true)
        {
            let firstsongfile = this.songfilestable.GetNewSongFileNames()[0];
            let artworkpath   = newalbumpath + "/" + firstsongfile; // Get Artwork that is embedded in the first song of the album
            this.tasks.AddTask("Import Artwork from Song Files",
                (webuitaskid)=>{
                    MusicDB_Request("InitiateArtworkImport", "ConfirmAlbumImportTask",
                        {sourcepath: artworkpath, targetpath: newalbumpath},
                        {webuitaskid: webuitaskid});
                    return "active";
                },
                (fnc, sig, args, pass)=>{
                    if(args == null)
                        return "bad";
                    else
                        return "active";
                },
                (fnc, sig, rawdata)=>{
                    if(fnc != "MusicDB:Upload")
                        return null;

                    if(sig == "InternalError")
                    {
                        window.console?.warn(`Importing Artwork failed with error: "${rawdata["message"]}"`)
                        return "bad";
                    }
                    if(sig == "StateUpdate")
                    {
                        if(rawdata["state"] == "importfailed")
                            return "bad";
                        else if(rawdata["state"] == "importcomplete")
                            return "good";
                    }
                    return "active";
                },
                /*canfail=*/ true // when importing artwork fails, it is not a big issue.
                );
        }

        // Import Lyrics
        if(this.albumsettingstable.GetImportLyricsState() === true)
        {
            this.tasks.AddTask("Import Lyrics from Song Files",
                (webuitaskid)=>{
                    return "active";
                },
                (fnc, sig, args, pass)=>{
                    return "good";
                });
        }

    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        if(fnc == "FindAlbumSongFiles" && sig == "ShowAlbumSongFiles")
        {
            window.console?.log(args);

            // It can happen that a potential album directory does not contain any songs
            if(args.length == 0)
            {
                // Clear everything and show an error
                this.albumsettingstable.Update("","","","",false,false,"");
                this.albumsettingstable.Hide();
                this.songfilestable.Update([]);
                this.songfilestable.Hide();

                this.oldartistdirectoryname = null;
                this.oldalbumdirectoryname  = null;

                this.ValidateForm();
                this.invalidsourceinfo.Show();
                return;
            }
            else
            {
                this.albumsettingstable.Show();
                this.songfilestable.Show();
                this.invalidsourceinfo.Hide();
            }

            this.oldartistdirectoryname = args[0].path.split("/")[0];
            this.oldalbumdirectoryname  = args[0].path.split("/")[1];
            let albumpath = this.oldartistdirectoryname + "/" + this.oldalbumdirectoryname;

            this.albumsettingstable.Update(
                args[0].artistname,
                args[0].albumname,
                args[0].releaseyear,
                args[0].origin,
                args[0].hasartwork,
                args[0].haslyrics,
                albumpath);
            this.songfilestable.Update(args);
            this.ValidateForm();
        }
        if(sig == "ConfirmAlbumImportTask")
        {
            window.console?.log(args);
            window.console?.log(pass);
            this.tasks.onMusicDBMessage(fnc, sig, args, pass);
        }
    }
    onMusicDBNotification(fnc, sig, rawdata)
    {
        this.tasks.onMusicDBNotification(fnc, sig, rawdata);
    }
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

