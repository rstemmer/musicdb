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

/*
 * Layout:
 *
 *   ┌──────────────────────────────────────┐
 *   │                                      │
 *   │  State [xxxx v]       (Load) (Save)  │ Main Buttons
 *   │                                      │
 *   ├──────────────────────────────────────┤
 *   │                                      │
 *   │  [Refrain] [Comment] [Background]    │ Toolbar
 *   │                                      │
 *   ├──────────────────────────────────────┤
 *   │                                      │
 *   │  Lyrics                              │ Text
 *   │                                      │
 *   └──────────────────────────────────────┘
 * 
 */


const LYRICSSTATE_EMPTY    = 0; // There are no lyrics set yet
const LYRICSSTATE_FROMFILE = 1; // The lyrics set come from the metatags of the song file
const LYRICSSTATE_FROMNET  = 2; // The lyrics were grabbed from the internet by a crawler
const LYRICSSTATE_FROMUSER = 3; // The lyrics were reviewed by the user. This noted the highest state of quality for lyrics.
const LYRICSSTATE_NONE     = 4; // There are no lyrics for this song - it is an instrumental song.



class LyricsEdit
{
    constructor()
    {
        this.element = document.createElement("div");
        this.element.classList.add("LyricsEdit");
        this.element.classList.add("flex-column");

        this.mainbar = this.CreateMainBar();
        this.toolbar = this.CreateToolBar();
        this.textbox = document.createElement("div");
        this.textbox.classList.add("flex-row");
        this.textbox.classList.add("seriffont");
        this.textbox.classList.add("lyricstext");
        this.textbox.onmouseup  = ()=>{this.onMouseUp(event);};
        this.textbox.onkeyup    = ()=>{this.onKeyUp(event);};

        this.element.dataset.editable = false;
        this.element.appendChild(this.mainbar.GetHTMLElement());
        this.element.appendChild(this.toolbar.GetHTMLElement());
        this.element.appendChild(this.textbox);

        this.selection = new Object();
        this.selection.firstelement = null;
        this.selection.startoffset  = null;
        this.selection.lastelement  = null;
        this.selection.endoffset    = null;
    }



    GetHTMLElement()
    {
        return this.element;
    }



    MakeEditable()
    {
        this.element.dataset.editable = true;
        this.textbox.contentEditable  = true;
    }



    CreateMainBar()
    {
        let ls_empty   = new SVGButton("MusicDB", ()=>{this.lyricsstate = LYRICSSTATE_EMPTY   ;});
        let ls_fromfile= new SVGButton("MusicDB", ()=>{this.lyricsstate = LYRICSSTATE_FROMFILE;});
        let ls_fromnet = new SVGButton("MusicDB", ()=>{this.lyricsstate = LYRICSSTATE_FROMNET ;});
        let ls_userappr= new SVGButton("MusicDB", ()=>{this.lyricsstate = LYRICSSTATE_FROMUSER;});
        let ls_none    = new SVGButton("MusicDB", ()=>{this.lyricsstate = LYRICSSTATE_NONE    ;});
        let loadbutton = new SVGButton("Load", ()=>{this.Reload()});
        let savebutton = new SVGButton("Save", ()=>{this.Save()});
        let mainbar    = new ToolBar();

        mainbar.GetHTMLElement().classList.add("lyricstools");

        this.stateselect = new SwitchGroup([ls_empty, ls_fromfile, ls_fromnet, ls_userappr, ls_none], 0);

        mainbar.AddButton(this.stateselect);
        mainbar.AddSpacer(true /*grow*/);
        mainbar.AddButton(new ToolGroup([loadbutton, savebutton]));
        return mainbar;
    }



    CreateToolBar()
    {
        let refrainbutton    = new SVGButton("MusicDB", ()=>{this.Format("refrain");});
        let backgroundbutton = new SVGButton("MusicDB", ()=>{this.Format("background");});
        let commentbutton    = new SVGButton("MusicDB", ()=>{this.Format("comment");});
        let toolbar          = new ToolBar();

        toolbar.GetHTMLElement().classList.add("lyricstools");

        toolbar.AddButton(new ToolGroup([refrainbutton, backgroundbutton, commentbutton]));
        toolbar.AddSpacer(true /*grow*/);
        return toolbar;
    }



    Update(songid, lyricsstate, lyrics)
    {
        this.songid      = songid;
        this.lyrics      = lyrics;
        this.lyricsstate = lyricsstate;

        window.console && console.log(this.lyricsstate);
        this.stateselect.Select(this.lyricsstate);
        this.textbox.innerText = this.lyrics; // TODO: parse markup
    }



    Reload()
    {
        MusicDB_Request("GetSongLyrics", "ReloadLyrics", {songid: this.songid});
        return;
    }



    Save()
    {
        window.console && console.log(this.lyricsstate);
        MusicDB_Call("SetSongLyrics", {songid: this.songid, lyrics: this.lyrics, lyricsstate: this.lyricsstate});
        return;
    }



    Format(style)
    {
        window.console && console.log(`Format(${style})`);
        let start = document.createElement("div");
        let end   = document.createElement("div");

        this.UpdateStyleFromSelectedLines(style);

        //start.innerText = "+" + style;
        //this.InsertElementBeforeSelection(start);

        //end.innerText = "-" + style;
        //this.InsertElementAfterSelection(end);
        return;
    }



    UpdateSelection()
    {
        let range = window.getSelection().getRangeAt(0);
        window.console && console.log(range);

        this.selection.firstelement = range.startContainer.parentNode;
        this.selection.startoffset  = range.startOffset;
        this.selection.lastelement  = range.endContainer.parentNode;
        this.selection.endoffset    = range.endOffset;
        return;
    }



    UpdateStyleFromSelectedLines(classname)
    {
        let element = this.selection.firstelement;
        do
        {
            if(element.classList.contains(classname))
            {
                window.console && console.log("remove class");
                element.classList.remove(classname);
            }
            else
            {
                window.console && console.log("add class");
                element.classList.add(classname);
            }
            element = element.nextSibling;
        }
        while(element != this.selection.lastelement.nextSibling);
        return;
    }



    InsertElementBeforeSelection(element)
    {
        let sibling = this.selection.firstelement;
        window.console && console.log("Insert Before:");
        window.console && console.log(sibling);

        this.textbox.insertBefore(element, sibling);
        return;
    }



    InsertElementAfterSelection(element)
    {
        let sibling = this.selection.lastelement.nextSibling;

        if(sibling != null)
            this.textbox.insertBefore(element, sibling);
        else
            this.textbox.appendChild(element);
        return;
    }



    onMouseUp(event)
    {
        window.console && console.log("onMouseUp");
        this.UpdateSelection();
        return;
    }



    onKeyUp(event)
    {
        let keycode = event.which || event.keyCode;
        window.console && console.log(`onKeyUp: ${keycode}`);
        window.console && console.log(this.textbox.innerHTML);

        if(keycode == 16 /*SHIFT*/)
        {
            this.UpdateSelection();
        }
        return;
    }
}




// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

