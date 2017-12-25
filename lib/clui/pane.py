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

from lib.clui.frame import Frame

class Pane(Frame):
    def __init__(self, title=None, x=0, y=0, w=0, h=0):
        Frame.__init__(self)
        self.title = title
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def Draw(self):
        self.SetColor("1;31", "40") # reset color
        Frame.Draw(self, self.x, self.y, self.w, self.h)
        if self.title:
            self.SetCursor(self.x+2, self.y)
            self.PrintText(" " + self.title + " ")






# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

