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



class AlbumImportLayer extends Layer
{
    // background: Instance of the Curtain class that lays behind the Layer.
    // When the layer is made visible, then also the background will be shown
    constructor(background)
    {
        super(background, "AlbumImportLayer")

        this.oldartistdirectoryname = null;
        this.oldalbumdirectoryname  = null;

        // Message Bar
        this.invalidsourceinfo  = new MessageBarError("Invalid Album Source. There were no songs in the selected Album directory.");

        // Headlines
        this.albumheadline = new LayerHeadline("Album Directory Settings",
            "These settings can be used to finalize the naming of the Album and to define to which Artist the Album belongs. "+
            "After import, the album path follows the MusicDB Naming Scheme for Albums: "+
            "\"{ArtistName}/{ReleaseYear} - {AlbumName}\"");
        this.songsheadline = new LayerHeadline("Song Files Settings",
            "These settings can be used to finalize the naming of the Song files."+
            "After import, the song files follow the MusicDB Naming Scheme for Songs: "+
            "\"{SongNumber} {SongName}.{FileExtension}\" or "+
            "\"{CDNumber}-{SongNumber} {SongName}.{FileExtension}\"");
        this.tasksheadline = new LayerHeadline("Import Tasks Overview",
            "This is an overview of the Tasks that will be executed when the Import process gets started. "+
            "During import, the status of each task will be visualized.");

        // Forms
        this.albumsettingstable = new AlbumPathSettingsTable((isvalid)=>{this.onAlbumSettingsValidation(isvalid);});
        this.songfilestable     = new SongFilesTableFromFilesystem((isvalid)=>{this.onSongsSettingsValidation(isvalid);});
        this.tasks              = new BatchExecution();

        // Tool Bar
        this.toolbar            = new ToolBar();
        this.cancelbutton       = new TextButton("Remove", "Cancel and Discard",
            ()=>{this.onClick_Cancel();},
            "Cancel album import. Nothing will be changed.");
        this.importbutton       = new TextButton("Import", "Import Album",
            ()=>{this.onClick_Import();},
            "Apply rename files and directories properly and import album into database. Create artis if not existing.");

        this.toolbar.AddButton(this.cancelbutton);
        this.toolbar.AddSpacer(true); // grow
        this.toolbar.AddButton(this.importbutton);

        this.ResetUI();
    }



    ResetUI()
    {
        this.RemoveChilds();
        this.AppendChild(this.invalidsourceinfo);
        this.AppendChild(this.albumheadline);
        this.AppendChild(this.albumsettingstable);
        this.AppendChild(this.songsheadline);
        this.AppendChild(this.songfilestable);
        this.AppendChild(this.tasksheadline);
        this.AppendChild(this.tasks);
        this.AppendChild(this.toolbar);
    }



    onClick_Cancel()
    {
        this.Hide();
    }

    onClick_Import()
    {
        let progresslayer = WebUI.GetLayer("AlbumImportProgress");
        progresslayer.ExecuteTasks(this.tasks); // Will also Show the layer
        this.Hide();
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
                    MusicDB.Request("RenameMusicFile", "ConfirmAlbumImportTask",
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
                    MusicDB.Request("RenameAlbumDirectory", "ConfirmAlbumImportTask",
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
                    MusicDB.Request("ChangeArtistDirectory", "ConfirmAlbumImportTask",
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
        let artistslist = WebUI.GetManager("Artists").FindArtist(artistdirectoryname, "strcmp");
        if(artistslist.length !== 1)
        {
            this.tasks.AddTask(`Create Artist: ${artistdirectoryname}`,
                (webuitaskid)=>{
                    MusicDB.Request("CreateArtistEntry", "ConfirmAlbumImportTask",
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
                MusicDB.Request("InitiateMusicImport", "ConfirmAlbumImportTask",
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
                if(fnc != "MusicDB:Task")
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
                    else
                        return null;
                }
                return "active";
            }
            );

        // Import Artwork
        let firstsongfile = this.songfilestable.GetNewSongFileNames()[0];
        let artworkpath   = newalbumpath + "/" + firstsongfile; // Get Artwork that is embedded in the first song of the album
        this.tasks.AddTask("Trying to Import Artwork from Song Files",
            (webuitaskid)=>{
                MusicDB.Request("InitiateArtworkImport", "ConfirmAlbumImportTask",
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
                if(fnc != "MusicDB:Task")
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
                    else
                        return null;
                }
                return "active";
            },
            /*canfail=*/ true // when importing artwork fails, it is not a big issue.
            );

        // Identify new album ID and communicate it to the album import progress layer for later use
        this.tasks.AddTask("Identify new Album ID",
            (webuitaskid)=>
            {
                MusicDB.Request("GetArtistsWithAlbums", "ConfirmAlbumImportTask",
                    {},
                    {webuitaskid: webuitaskid});
                return "active";
            },
            (fnc, sig, args, pass)=>
            {
                // Identify new album and load it
                for(let artist of args)
                {
                    window.console?.log(artist);
                    for(let albuminfos of artist.albums)
                    {
                        let MDBAlbum = albuminfos.album;
                        window.console?.log(MDBAlbum);
                        window.console?.log(`${newalbumpath} == ${MDBAlbum.path}`);
                        if(MDBAlbum.path == newalbumpath)
                        {
                            MusicDB.Request("Bounce", "InformAlbumImportProgressLayer",
                                {albumid: MDBAlbum.id});
                            return "good";
                        }
                    }
                }
                return "bad"; // Album not found. That is bad because then Import failed somewhere.
            },
            (fnc, sig, rawdata)=>{
                return null;
            },
            /*canfail=*/ true // when getting the album ID fails, it is not a big issue.
            );

    }



    onMusicDBMessage(fnc, sig, args, pass)
    {
        if(fnc == "FindAlbumSongFiles" && sig == "ShowAlbumImportLayer")
        {
            this.ResetUI();

            // It can happen that a potential album directory does not contain any songs
            if(args.length == 0)
            {
                // Clear everything and show an error
                this.albumsettingstable.Update("","","","");
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
                args[0].frommeta.artistname,
                args[0].frommeta.albumname,
                args[0].frommeta.releaseyear,
                albumpath);
            this.songfilestable.Update(args);
            this.ValidateForm();
        }
    }
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

