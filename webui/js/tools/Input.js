// MusicDB,  a music manager with web-bases UI that focus on music.
// Copyright (C) 2017-2021  Ralf Stemmer <ralf.stemmer@gmx.net>
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

class Input extends Element
{
    constructor(type, onvalidate, initvalue, tooltip="")
    {
        super("input", ["Input"]);
        this.element.type    = type;
        this.element.oninput = ()=>{this.onInput();};
        this.element.value   = initvalue;
        this.element.title   = tooltip;
        this.onvalidate      = onvalidate;
        this.onInput(); // initialization is something like input
    }



    SetValidateEventCallback(callback)
    {
        this.onvalidate = callback;
    }
    SetAfterValidateEventCallback(callback)
    {
        this.onaftervalidation = callback;
    }



    onInput()
    {
        if(typeof this.onvalidate === "function")
        {
            let value = this.GetValue();
            let valid = this.onvalidate(value);
            this.SetValidState(valid);
        }
        if(typeof this.onaftervalidation === "function")
        {
            let value = this.GetValue();
            let valid = this.GetValidState();
            this.onaftervalidation(value, valid);
        }
    }



    SetValidState(valid)
    {
        this.element.dataset.valid = valid;
        this.SetData("valid", valid);
    }
    GetValidState(valid)
    {
        return this.GetData("valid") === "true";
    }



    SetValue(value)
    {
        super.SetValue(value);
        this.onInput();
        return;
    }


    SetWidth(csswidth)
    {
        this.element.style.width = csswidth;
    }

    SetEnabled(enabled=true)
    {
        this.element.disabled = !enabled;
    }
}



class TextInput extends Input
{
    constructor(oninput="", initvalue="", tooltip="")
    {
        super("text", oninput, initvalue, tooltip)
    }
}

class NumberInput extends Input
{
    constructor(oninput="", initvalue="", tooltip="")
    {
        super("number", oninput, initvalue, tooltip)
    }
}


// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

