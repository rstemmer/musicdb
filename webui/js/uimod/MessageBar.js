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


class MessageBar extends Element
{
    constructor(svgicon, htmlmessage=null)
    {
        super("div", ["MessageBar", "flex-row"]);
        this.icon = svgicon;
        
        this.message = new Element("div");
        if(typeof htmlmessage === "string")
            this.message.SetInnerHTML(htmlmessage);
        this.AddCSSClass("message");

        this.closebutton = new SVGButton("Approve", ()=>{this.Hide();});
        this.closebutton.SetTooltip("Confirm and hide this message");

        this.AppendChild(this.icon);
        this.AppendChild(this.message);
        this.AppendChild(this.closebutton);

        this.autohidedelay   = null;
        this.hideclosebutton = false;

        this.Hide();
    }



    UpdateMessage(htmlmessage)
    {
        this.message.SetInnerHTML(htmlmessage);
    }



    // When delay != null, then a timer automatically hides the message after delay milliseconds
    SetTimer(delay)
    {
        this.autohidedelay = delay;
    }



    ShowCloseButton()
    {
        this.hideclosebutton = false;
        this.closebutton.Show();
    }
    HideCloseButton()
    {
        this.hideclosebutton = true;
        this.closebutton.Hide();
    }



    Show()
    {
        this.element.style.display = "flex";

        if(typeof this.autohidedelay === "number")
        {
            this.HideCloseButton();
            window.setTimeout(()=>{this.Hide()}, this.autohidedelay);
        }
        else
        {
            if(this.hideclosebutton === true)
                this.HideCloseButton();
            else
                this.ShowCloseButton();
        }
    }



    Hide()
    {
        this.element.style.display = "none";
    }
}



class MessageBarInfo extends MessageBar
{
    constructor(htmlmessage=null)
    {
        super(new SVGIcon("StatusInfo"), htmlmessage);
        this.SetData("messagetype", "info");
    }
}



class MessageBarWarning extends MessageBar
{
    constructor(htmlmessage=null)
    {
        super(new SVGIcon("StatusBad"), htmlmessage);
        this.SetData("messagetype", "warning");
    }
}



class MessageBarError extends MessageBar
{
    constructor(htmlmessage=null)
    {
        super(new SVGIcon("StatusBad"), htmlmessage);
        this.SetData("messagetype", "error");
    }
}



class MessageBarConfirm extends MessageBar
{
    constructor(htmlmessage=null)
    {
        super(new SVGIcon("StatusGood"), htmlmessage);
        this.SetData("messagetype", "confirm");
    }
}



class MessageBarConfirmDelete extends MessageBar
{

    constructor(htmlmessage, expectedinput, ondelete)
    {
        super(new SVGIcon("StatusWarning"), htmlmessage);
        this.SetData("messagetype", "warning");
        this.closebutton.SetTooltip("Cancel deletion and hide this message");

        this.ondelete      = ondelete;
        this.expectedinput = expectedinput;
        this.input = new TextInput((value)=>{return this.onInput(value);});
        this.input.SetWidth(expectedinput.length + "ch");
        this.input.GetHTMLElement().onkeyup = (event)=>{this.onKeyUp(event);};

        this.AppendChild(this.input);
    }



    onInput(value)
    {
        if(value == this.expectedinput)
            return true;
        else
            return false;
    }



    onKeyUp(event)
    {
        let keycode = event.which || event.keyCode;
        if(keycode == 13 /*ENTER*/ && this.input.GetValue() == this.expectedinput)
        {
            this.Hide();
            this.ondelete();
        }
    }
}

// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

