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
        this.textbox.classList.add("seriffont");
        this.textbox.classList.add("lyricstext");
        this.editbox = document.createElement("textarea");
        this.editbox.classList.add("frame");
        this.editbox.classList.add("seriffont");
        this.editbox.classList.add("lyricstext");
        //this.editbox.onmouseup  = ()=>{this.onMouseUp(event);};
        //this.editbox.onkeyup    = ()=>{this.onKeyUp(event);};
        //this.editbox.oninput    = ()=>{this.onInput(event);};
        //this.editbox.oncopy     = ()=>{this.onCopy(event);};
        //this.editbox.onpaste    = ()=>{this.onPaste(event);};

        this.element.dataset.editable = false;
        this.element.appendChild(this.mainbar.GetHTMLElement());
        this.element.appendChild(this.toolbar.GetHTMLElement());
        this.element.appendChild(this.textbox);
    }



    GetHTMLElement()
    {
        return this.element;
    }



    MakeEditable()
    {
        this.element.dataset.editable = true;
        this.editbox.value = this.lyrics;
        this.element.replaceChild(this.editbox, this.textbox);
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

        this.stateselect.Select(this.lyricsstate);
        this.RenderLyrics();
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



    RenderLyrics()
    {
        this.textbox.innerText = this.lyrics;
    }



    Format(style)
    {
        switch(style)
        {
            case "refrain":
                this.InsertLinesAroundSelection(":: ref", "::");
                break;
            case "background":
                this.InsertCharactersAroundSelection("<<", ">>");
                break;
            case "comment":
                this.InsertLinesAroundSelection(":: comment", "::");
                break;
        }
        return;
    }



    InsertCharactersAroundSelection(text1, text2)
    {
        let begin = this.editbox.selectionStart;
        let end   = this.editbox.selectionEnd;
        let text  = this.editbox.value;

        let starttext   = text.substring(0,     begin);
        let middletext  = text.substring(begin, end);
        let endtext     = text.substring(end,   text.length);

        let newtext = starttext + text1 + middletext + text2 + endtext;
        this.editbox.value = newtext;
        return;
    }



    InsertLinesAroundSelection(line1, line2)
    {
        let begin = this.editbox.selectionStart;
        let end   = this.editbox.selectionEnd;

        this.InsertLineBeforeSelection(begin, line1);
        this.InsertLineAfterSelection(end+line1.length+1, line2);

        return;
    }



    InsertLineBeforeSelection(begin, line)
    {
        let text  = this.editbox.value;

        while(begin != 0 && text[begin] != '\n')
            begin--;

        if(text[begin] == '\n')
            begin++;

        let newtext;
        newtext  = text.substring(0, begin);
        newtext += line + '\n';
        newtext += text.substring(begin);

        this.editbox.value = newtext;

        return;
    }



    InsertLineAfterSelection(end, line)
    {
        let text = this.editbox.value;

        window.console && console.log(end);
        while(end != text.length && text[end] != '\n')
            end++;
        window.console && console.log(end);

        if(text[end] == '\n')
            end++;
        else if(text[end] != '\n')
            line = '\n' + line;

        let newtext;
        newtext  = text.substring(0, end);
        newtext += line + '\n';
        newtext += text.substring(end);

        this.editbox.value = newtext;

        return;
    }




    /*
    onMouseUp(event)
    {
        return;
    }



    onKeyUp(event)
    {
        return;
    }



    onInput(event)
    {
        return;
    }



    onCopy(event)
    {
        return;
    }



    onPaste(event)
    {
        return;
    }
    */
}




// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

