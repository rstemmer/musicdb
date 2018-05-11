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
    This class provides a simple one-line text input element.

    The cursor mentioned in this class documentation is not related to the cursor of the terminal!
    Each TextInput maintain its own cursor.

    Args:
        x,y (int): Position of the list view
        w (int): Width
    """
    def __init__(self, x=0, y=0, w=0):
        Text.__init__(self)
        self.x     = x
        self.y     = y
        self.w     = w
        self.data  = "" # text buffer
        self.cursor= 0
        self.offset= 0  # where to start printing - important when data is larger than input element
        self.textfg   = "1;37"
        self.textbg   = "44"
        self.cursorbg = "46"


    def SetData(self, string):
        """
        This method sets the data of the input element.
        The cursor points to the end of the input data.

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


    def GetData(self):
        """
        Returns the string from the input element

        Returns:
            The input as string
        """
        return self.data


    def Draw(self):
        """
        This method draws the input control and the cursor.
        The input elements color are white text on blue background.
        The element the cursor points to has a cyan background.

        Returns:
            *Nothing*
        """
        self.SetColor(self.textfg, self.textbg)

        string = self.data[self.offset:self.offset+self.w]
        string = string.ljust(self.w)
        self.SetCursor(self.x, self.y)
        self.PrintText(string)

        self.SetCursor(self.x+self.cursor, self.y)
        self.SetBGColor(self.cursorbg)
        self.PrintText(string[self.cursor])


    def HandleKey(self, key):
        """
        This method handled the users input.
        The keys are expected as the method :meth:`lib.clui.text.Text.GetKey` returns.
        With the ``"right"`` and ``"left"`` key, the user can navigate through the text.
        With ``"backspace"`` the character left to the cursor gets removed.
        With ``"delete"`` the character right below the cursor.
        Each printable character gets inserted left to the cursor.

        Args:
            key (str): Key name that shall be handled

        Returns:
            *Nothing*
        """
        # It is allowed to pass a key that is None, so just make a robust escape for values that cannot be handled
        #  by the following code
        if type(key) != str:
            return

        if key == "left":
            if self.cursor > 0:
                self.cursor -= 1
            elif self.offset > 0:
                self.offset -= 1

        elif key == "right":
            if self.cursor < min(len(self.data), self.w-1):
                self.cursor += 1
            elif self.offset + len(self.data) > self.w and self.offset+self.cursor < len(self.data):
                self.offset += 1

        elif key == "home":
            self.cursor = 0
            self.offset = 0

        elif key == "end":
            self.cursor = min(len(self.data), self.w-1)
            if len(self.data) > self.w:
                self.offset = len(self.data)-self.w + 1

        elif key == "backspace" and self.cursor > 0:
            self.data   = self.data[:self.offset + self.cursor-1] + self.data[self.offset + self.cursor:]
            self.cursor -= 1

        elif key == "delete" and self.cursor < len(self.data):
            self.data   = self.data[:self.offset + self.cursor] + self.data[self.offset + self.cursor+1:]

        elif len(key) == 1 and key.isprintable():
            self.data   = self.data[:self.offset + self.cursor] + key + self.data[self.offset + self.cursor:]
            if self.cursor < min(len(self.data), self.w-1):
                self.cursor += 1
            elif self.offset + len(self.data) >= self.w:
                self.offset += 1

        self.Draw()



class NoTextInput(TextInput):
    """
    This is a *read-only* variation of the :class:`~TextInput` element.

    Args:
        x,y (int): Position of the list view
        w (int): Width
    """
    def __init__(self, x=0, y=0, w=0):
        TextInput.__init__(self, x, y, w)
        self.textfg   = "1;36"
        self.textbg   = "40"
        self.cursorbg = "40"

    def HandleKey(self, key=None):
        """
        This method does nothing. This is a read-only control element.

        Args:
            key: *will be ignored*

        Returns:
            *Nothing*
        """
        pass


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

