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

from lib.clui.text import Text

class TextInput(Text):
    """
    This class provides a simple one-line text input element

    Args:
        x,y (int): Position of the list view
        w (int): Width
    """
    def __init__(self, x=0, y=0, w=0):
        Text.__init__(self)
        self.w     = w
        self.data  = ""
        self.caret = 0


    def SetData(self, string):
        """
        This method sets the data of the input element

        Args:
            string (str): String that will be used as the input

        Returns:
            *Nothing*

        Raises:
            TypeError: When string is not of type string
        """
        if type(string) != str:
            raise TypeError("Data must be of type string!")

        self.data = string
        self.caret= len(self.data)  # caret at the end of the text


    def GetData(self):
        """
        Returns the string from the input element

        Returns:
            The input as string
        """
        return self.data


    def Draw(self):
        """
        This method draws the input control.
        """
        self.SetColor("1;37", "44")
        string = self.data[:self.w]
        string = string.ljust(self.w)
        self.SetCursor(self.x, self.y)
        self.PrintText(string)

        self.SetCursor(self.x+self.caret, self.y)
        self.SetBGColor("46")
        self.PrintText(string[self.caret])


    def HandleKey(self, key):
        """

        Args:
            key (str): Key name that shall be handled

        Returns:
            *Nothing*
        """
        # It is allowed to pass a key that is None, so just make a robust escape for values that cannot be handled
        #  by the following code
        if type(key) != str:
            return

        if key == "left" and self.caret > 0:
            self.caret -= 1
        elif key == "right" and self.caret < len(self.data):
            self.caret += 1
        elif key == "backspace" and self.caret > 0:
            self.data   = self.data[:self.caret-1] + self.data[self.caret:]
            self.caret -= 1
        elif key == "entf" and self.caret < len(self.data):
            self.data   = self.data[:self.caret] + self.data[self.caret+1:]
        elif len(key) == 1 and key.isprintable() and len(self.data) < self.w:
            self.data   = self.data[:self.caret] + key + self.data[self.caret:]
            self.caret += 1
            if len(self.data) > self.w:
                self.data = self.data[:self.w]
        self.Draw()



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

