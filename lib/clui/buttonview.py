# MusicDB,  a music manager with web-bases UI that focus on music.
# Copyright (C) 2017  Ralf Stemmer <ralf.stemmer@gmx.net>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from lib.clui.pane import Pane

class ButtonView(Pane):
    def __init__(self, x=0, y=0, w=0, h=0, align="left"):
        Pane.__init__(self, None, x, y, w, h)
        self.buttons = []
        
        align = align[0]
        # middle = center
        if align == "m":
            align = "c"

        if align in ["l","r","c"]:
            self.align = align
        else:
            self.align = "l"


    def AddButton(self, key, name):
        self.buttons.append((key, name))


    def Draw(self):
        rbuttons = []

        # calculate max button text length
        numbuttons = len(self.buttons)
        maxsize    = self.w // numbuttons
        maxsize   -= 4  # "[x:]"
        barlength  = 0  # length of the button bar

        # render buttons
        for button in self.buttons:
            rbutton  = "\033[1;31m["
            rbutton += "\033[1;36m" + button[0]  # key
            rbutton += "\033[1;31m:"
            rbutton += "\033[1;34m" + button[1][:maxsize]  # name
            rbutton += "\033[1;31m]"
            rbuttons.append(rbutton)
            barlength += 4 + min(maxsize,len(button[1]))  # 4: "[x:]"

        if self.align == "l":
            x = self.x
        elif self.align == "c":
            x = self.x + (self.w - barlength) // 2
        elif self.align == "r":
            x = self.x + (self.w - barlength)

        self.SetCursor(x, self.y)
        for rbutton in rbuttons:
            self.PrintText(rbutton)



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

