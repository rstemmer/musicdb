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


class ImportForm extends Element
{
    constructor(formtable, onsavedraft, onimportfile, onremovefile, uploadtask=null)
    {
        super("div", ["ImportForm", "flex-row"]);

        let rightcolumn = document.createElement("div");
        rightcolumn.classList.add("flex-column");

        this.toolbar      = new ToolBar();
        this.savebutton   = new SVGButton("Save",    onsavedraft, "Save Formular as Draft");
        this.importbutton = new SVGButton("Import", onimportfile, "Save Formular and Import Music");
        this.removebutton = new SVGButton("Remove", onremovefile, "Delete File from Server");

        if(typeof onsavedraft === "function" && typeof onimportfile === "function")
            this.toolbar.AddButton(new ToolGroup([this.savebutton, this.importbutton]));
        else if(typeof onsavedraft === "function")
            this.toolbar.AddButton(this.savebutton);
        else if(typeof onimportfile === "function")
            this.toolbar.AddButton(this.importbutton);

        if(typeof onremovefile === "function")
        {
            this.toolbar.AddSpacer(true /*grow*/);
            this.toolbar.AddButton(new ToolGroup([this.removebutton]));
        }


        this.uploadtask  = uploadtask;
        this.uploadstate = new ImportStateList();
        this.UpdateStates();

        rightcolumn.appendChild(this.toolbar.GetHTMLElement());
        rightcolumn.appendChild(this.uploadstate.GetHTMLElement());

        this.element.appendChild(formtable.GetHTMLElement());
        this.element.appendChild(rightcolumn);

        formtable.GetHTMLElement().oninput = ()=>{this.ValidateForm();}; // Validate whenever something was edited
    }



    UpdateUploadTask(uploadtask)
    {
        if(typeof uploadtask !== "object")
            return;

        this.uploadtask = uploadtask;
        this.UpdateStates();
        this.ValidateForm();
    }



    UpdateStates()
    {
        let state = this.uploadtask["state"];
        switch(state)
        {
            case "waitforchunk":
                this.uploadstate.SetState("uploading",     "active");
                this.uploadstate.SetState("preprocess",    "open");
                this.uploadstate.SetState("integrate",     "open");
                this.uploadstate.SetState("importmusic",   "open");
                this.uploadstate.SetState("importartwork", "open");
                break;
            case "uploadcomplete":
                this.uploadstate.SetState("uploading",     "good");
                this.uploadstate.SetState("preprocess",    "active");
                this.uploadstate.SetState("integrate",     "open");
                this.uploadstate.SetState("importmusic",   "open");
                this.uploadstate.SetState("importartwork", "open");
                break;
            case "uploadfailed":
                this.uploadstate.SetState("uploading",     "bad");
                this.uploadstate.SetState("preprocess",    "open");
                this.uploadstate.SetState("integrate",     "open");
                this.uploadstate.SetState("importmusic",   "open");
                this.uploadstate.SetState("importartwork", "open");
                break;
            case "preprocessed":
                this.uploadstate.SetState("uploading",     "good");
                this.uploadstate.SetState("preprocess",    "good");
                this.uploadstate.SetState("integrate",     "open");
                this.uploadstate.SetState("importmusic",   "open");
                this.uploadstate.SetState("importartwork", "open");
                break;
            case "invalidcontent":
                this.uploadstate.SetState("uploading",     "good");
                this.uploadstate.SetState("preprocess",    "bad");
                this.uploadstate.SetState("integrate",     "open");
                this.uploadstate.SetState("importmusic",   "open");
                this.uploadstate.SetState("importartwork", "open");
                break;
            case "integrated":
                this.uploadstate.SetState("uploading",     "good");
                this.uploadstate.SetState("preprocess",    "good");
                this.uploadstate.SetState("integrate",     "good");
                this.uploadstate.SetState("importmusic",   "open");
                this.uploadstate.SetState("importartwork", "open");
                break;
            case "integrationfailed":
                this.uploadstate.SetState("uploading",     "good");
                this.uploadstate.SetState("preprocess",    "good");
                this.uploadstate.SetState("integrate",     "bad");
                this.uploadstate.SetState("importmusic",   "open");
                this.uploadstate.SetState("importartwork", "open");
                break;
            case "startimport":
                this.uploadstate.SetState("uploading",     "good");
                this.uploadstate.SetState("preprocess",    "good");
                this.uploadstate.SetState("integrate",     "good");
                this.uploadstate.SetState("importmusic",   "active");
                this.uploadstate.SetState("importartwork", "open");
                break;
            case "importfailed":
                this.uploadstate.SetState("uploading",     "good");
                this.uploadstate.SetState("preprocess",    "good");
                this.uploadstate.SetState("integrate",     "good");
                this.uploadstate.SetState("importmusic",   "bad");
                this.uploadstate.SetState("importartwork", "bad");
                break;
            case "importartwork":
                this.uploadstate.SetState("uploading",     "good");
                this.uploadstate.SetState("preprocess",    "good");
                this.uploadstate.SetState("integrate",     "good");
                this.uploadstate.SetState("importmusic",   "good");
                this.uploadstate.SetState("importartwork", "active");
                break;
            case "importcomplete":
                this.uploadstate.SetState("uploading",     "good");
                this.uploadstate.SetState("preprocess",    "good");
                this.uploadstate.SetState("integrate",     "good");
                this.uploadstate.SetState("importmusic",   "good");
                this.uploadstate.SetState("importartwork", "good");
                break;
        }
    }



    ValidateForm()
    {
        let uploadvalid = this.ValidateUpload();
        let inputsvalid = this.ValidateInputs();

        if(uploadvalid && inputsvalid)
        {
            this.EnableImport(true);
            return true;
        }

        this.EnableImport(false);
        return false;
    }

    ValidateUpload()
    {
        if(this.uploadtask === null)
            return true;

        if(this.uploadtask.state === "preprocessed")
            return true;

        return false;
    }

    ValidateInputs()
    {
        window.console && console.error("This method must be implemented by derived classes");
        return false;
    }



    EnableImport(state=true)
    {
        if(state === true)
            this.importbutton.Enable();
        else
            this.importbutton.Disable();
    }
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

