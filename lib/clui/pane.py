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
    """
    This class can be used to define a whole, filled are in the shell.
    The area consist of spaces in the defined color.
    Around the area, a :class:`~lib.clui.frame.Frame` gets printed.

    If a title is set, then this title gets printed in the top left corner of the frame.
    The title gets surrounded by a space character.

    The coordinates define the placement of the frame, the usable area starts with an offset of one.

    Args:
        title (str): Optional title for the area.
        x,y (int): Start position of the frame (top left corner) of this area
        w (int): width of the frame
        h (int): height of the frame
    """

    def __init__(self, title=None, x=0, y=0, w=0, h=0):
        Frame.__init__(self)
        self.title = title

        if type(x) != int or type(y) != int or type(w) != int or type(h) != int:
            raise TypeError("Coordinates, width and height must be of type integer")
        if x < 0 or y < 0:
            raise ValueError("No negative coordinates allowed")
        
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.SetColor("1;31", "40")

    def Draw(self):
        """
        This method prints a whole area in the shell.

        Returns:
            *Nothing*
        """
        self.SetColor() # reset color
        Frame.Draw(self, self.x, self.y, self.w, self.h)
        if self.title:
            self.SetCursor(self.x+2, self.y)
            self.PrintText(" " + self.title + " ")


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

