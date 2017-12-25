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

class ListView(Pane):
    def __init__(self, title=None, x=0, y=0, w=0, h=0):
        Pane.__init__(self, title, x, y, w, h)
        self.listoffset     = 0
        self.linemarker     = 0
        self.elements       = None
        self.drawcallback   = None


    def onDrawElement(self, element, number, maxwidth):
        string = str(element)
        string = string[:maxwidth]
        string = string.ljust(maxwidth)
        return string


    def onAction(self, element, key):
        return element


    def SetData(self, elements):
        self.elements = elements


    def SetSelectedData(self, element):
        self.elements[self.linemarker] = element


    def GetSelectedData(self):
        return self.elements[self.linemarker]


    def Draw(self):
        self.SetFGColor("1;31")
        Pane.Draw(self)

        maxelements = len(self.elements)
        self.DrawScrollbar(self.listoffset, 0, maxelements)

        for i in range(1, self.h-1):  # line number between the frames
            index = self.listoffset + (i-1)
            if index >= maxelements:
                break

            maxwidth = self.w-2 # - frame
            string   = self.onDrawElement(self.elements[index], index, maxwidth)

            self.SetCursor(self.x+1, self.y+i)
            if self.linemarker == index:
                bgcolor = "46"
            else:
                bgcolor = "40"
            self.SetColor("1;34", bgcolor)
            self.PrintText(string)
        self.SetColor("1;31", "40") # reset color

        # DEBUG
        #self.SetCursor(self.x+1, self.y+self.h-1)
        #self.SetColor("1;30", "40")
        #self.PrintText("m=%d,o=%d"%(self.linemarker,self.listoffset))


    def DrawScrollbar(self, offset, start, end):
        length = self.h - 2     # scrollbarlength (- frames)
        crange = end - start    # content range
        if crange < length:
            return

        pos    = offset + length/2
        marker = int(pos * ((length) / (crange)))

        self.SetColor("1;31", "40")
        for y in range(1, self.h-1):
            self.SetCursor(self.x+self.w-1, self.y+y)
            if y-1 == marker:
                self.PrintText("█")
            else:
                self.PrintText("░")

        # DEBUG
        #self.SetCursor(self.x+self.w-9, self.y+self.h-1)
        #self.SetColor("1;30", "40")
        #self.PrintText("sp=%d,%d"%(pos,marker))


    def HandleKey(self, key):
        if key == "up":
            if self.linemarker > 0:
                self.linemarker -= 1

            if self.linemarker < self.listoffset:
                self.listoffset -= 1

            self.Draw()

        elif key == "down":
            if self.linemarker < len(self.elements)-1:
                self.linemarker += 1

            if self.linemarker >= self.listoffset + self.h-2:
                self.listoffset += 1

            self.Draw()

        else:
            if self.elements:
                self.elements[self.linemarker] = self.onAction(self.elements[self.linemarker], key)
            self.Draw()




# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

