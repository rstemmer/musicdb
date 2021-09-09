// MusicDB,  a music manager with web-bases UI that focus on music.
// Copyright (C) 2021-2021  Ralf Stemmer <ralf.stemmer@gmx.net>
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

class GradientBar extends Element
{
    constructor()
    {
        super("div", ["GradientBar"]);

        this.gradientsteps = ""
    }



    // position: 0..100
    AddStep(csscolor, position)
    {
        if(this.gradientsteps.length !== 0)
            this.gradientsteps += ",";
        this.gradientsteps   += `${csscolor} ${position}%`;
        this.element.style.background = `linear-gradient(to right, ${this.gradientsteps})`;
    }
}



class IndicatorBar extends Element
{
    constructor(label, from, to, transition)
    {
        super("div", ["IndicatorBar", "flex-row"]);

        this.bar   = new GradientBar();
        this.SetValidWindow(from, to, transition);

        this.label = new Element("span");
        this.label.SetInnerText(label);

        this.indicator = new Element("div", ["Indicator", "frame"]);
        this.bar.AppendChild(this.indicator);

        this.AppendChild(this.bar);
        this.AppendChild(this.label);
    }



    // 0..100
    SetValidWindow(from, to, transition)
    {
        if(from - transition > 0 && from > 0)
            this.bar.AddStep("var(--color-red)",      0);
        if(from - transition >= 0)
            this.bar.AddStep("var(--color-red)",     from - transition);
        if(from - transition / 2 >= 0)
            this.bar.AddStep("var(--color-yellow)",  from - transition / 2);
        this.bar.AddStep("var(--color-green)",   from);
        this.bar.AddStep("var(--color-green)",   to);
        if(to + transition / 2 <= 100)
            this.bar.AddStep("var(--color-yellow)",  to + transition / 2);
        if(to + transition <= 100)
            this.bar.AddStep("var(--color-red)",     to + transition);
        if(to + transition < 100)
            this.bar.AddStep("var(--color-red)",    100);
    }



    // position: 0..100
    SetIndicator(position)
    {
        window.console?.log(`SetIndicator(${position})`);
        this.indicator.GetHTMLElement().style.left = `${position}%`;
    }

}



// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

