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
    constructor(formtable, onsavedraft, onimportfile, uploadtask=null)
    {
        super("div", ["ImportForm", "flex-row"]);

        let rightcolumn = document.createElement("div");
        rightcolumn.classList.add("flex-column");

        this.savebutton   = new SVGButton("Save",    onsavedraft,  "Save Formular as Draft");
        if(typeof onsavedraft === "function")
            rightcolumn.appendChild(this.savebutton.GetHTMLElement());

        this.importbutton = new SVGButton("MusicDB", onimportfile, "Save Formular and Import Music");
        if(typeof onimportfile === "function")
            rightcolumn.appendChild(this.importbutton.GetHTMLElement());

        this.uploadtask = uploadtask;
        this.uploadstate = new ImportStateList();
        rightcolumn.appendChild(this.uploadstate.GetHTMLElement());

        this.element.appendChild(formtable.GetHTMLElement());
        this.element.appendChild(rightcolumn);

        formtable.GetHTMLElement().oninput = ()=>{this.ValidateForm();}; // Validate whenever something was edited
    }



    UpdateUploadTask(uploadtask)
    {
        this.uploadtask = uploadtask;
        this.ValidateForm();
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

