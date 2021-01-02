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



class VideoImportFormRow extends TableRow
{
    // label must be a string, object must provide a GetHTMLElement method.
    constructor(label, object)
    {
        super(2, ["VideoImportFormRow"]);
        this.SetContent(0, document.createTextNode(label));
        this.SetContent(1, object.GetHTMLElement());
    }
}



class VideoImportFormTable extends Table
{
    constructor(artistname, musicname, origin, release)
    {
        super(["VideoImportForm"]);

        // Name, Artist, Origin, Release Date, Genre, Sub-Genre
        // TODO: create better artist input with search
        this.artistinput  = new ArtistInput((id, name)=>{return this.onArtistInput(id, name); }, artistname);
        this.nameinput    = new TextInput(  (value)=>{return this.onNameInput(value);   }, musicname);
        this.origininput  = new TextInput(  (value)=>{return this.onOriginInput(value); }, origin);
        this.releaseinput = new NumberInput((value)=>{return this.onReleaseInput(value);}, release);

        this.AddRow(new VideoImportFormRow("Artist Name:",  this.artistinput) );
        this.AddRow(new VideoImportFormRow("Video Name:",   this.nameinput)   );
        this.AddRow(new VideoImportFormRow("Release Date:", this.releaseinput));
        this.AddRow(new VideoImportFormRow("File Origin:",  this.origininput) );
    }



    Validate()
    {
        if(this.artistinput.GetValidState() == false)
            return false;
        if(this.nameinput.GetValidState() == false)
            return false;
        if(this.releaseinput.GetValidState() == false)
            return false;
        if(this.origininput.GetValidState() == false)
            return false;
        return true;
    }

    onArtistInput(artistid, artistname)
    {
        if(typeof artistname !== "string")
            return false;
        if(artistname.length > 0)
            return true;
        return false;
    }
    onNameInput(value)
    {
        if(value.length > 0)
            return true;
        return false;
    }
    onOriginInput(value)
    {
        if(value.length > 0)
            return true;
        return false;
    }
    onReleaseInput(value)
    {
        if(value < 1000 || value > 2000)
            return false;
        return true;
    }



    GetArtist()
    {
        return this.artistinput.GetValue();
    }
    GetName()
    {
        return this.nameinput.GetValue();
    }
    GetRelease()
    {
        return this.releaseinput.GetValue();
    }
    GetOrigin()
    {
        return this.origininput.GetValue();
    }
}



class VideoImportForm extends ImportForm
{
    constructor(artistname, musicname, origin, release, uploadtask=null)
    {
        let table    = new VideoImportFormTable(artistname, musicname, origin, release);
        let onsave   = null;
        let onimport = ()=>{this.onImport();};

        if(typeof uploadtask === "object")
        {
            onsave = ()=>{this.onSave(uploadtask.id);};
        }

        super(table, onsave, onimport, uploadtask);

        this.table      = table;
    }



    ValidateInputs()
    {
        return this.table.Validate();
    }



    onSave(uploadid)
    {
        let artist  = this.table.GetArtist();
        let name    = this.table.GetName();
        let release = this.table.GetRelease();
        let origin  = this.table.GetOrigin();

        MusicDB_Call("AnnotateUpload", {uploadid: uploadid, name: name, artistname: artist, release: release, origin: origin});
        //MusicDB_Broadcast("GetUploads", "ShowUploads"); // Update other clients views with the new annotation
    }



    onImport()
    {
        window.console && console.log("Import Video");
    }
}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

