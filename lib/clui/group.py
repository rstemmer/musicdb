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

class Group(Pane):
    def __init__(self, x, y, w, h, space=0):
        Pane.__init__(self, None, x, y, w, h)
        self.space = space
        self.panes = []

    def AddPane(self, pane):
        self.panes.append(pane)
        self.Rearange()

    def Draw(self):
        for pane in self.panes:
            pane.Draw()


class HGroup(Group):
    def __init__(self, x, y, w, h, space=0):
        Group.__init__(self, x, y, w, h, space)

    def Rearange(self):
        numpanes  = len(self.panes)
        numspaces = numpanes - 1
        x = self.x
        y = self.y
        w = int(self.w / numpanes) - int((self.space * numspaces) / numpanes)
        h = self.h
        for num, pane in enumerate(self.panes):
            pane.x = x + num * (w + self.space)
            pane.y = y
            pane.w = w
            pane.h = h


class VGroup(Group):
    def __init__(self, x, y, w, h, space=0):
        Group.__init__(self, x, y, w, h, space)

    def Rearange(self):
        numpanes  = len(self.panes)
        numspaces = numpanes - 1
        x = self.x
        y = self.y
        w = self.w
        h = int(self.h / numpanes) - int((self.space * numspaces) / numpanes)
        for num, pane in enumerate(self.panes):
            pane.x = x
            pane.y = y + num * (h + self.space)
            pane.w = w
            pane.h = h




# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

