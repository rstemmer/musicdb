# MusicDB,  a music manager with web-bases UI that focus on music.
# Copyright (C) 2017 - 2021  Ralf Stemmer <ralf.stemmer@gmx.net>
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

from musicdb.lib.clui.text import Text

class BoolInput(Text):
    """
    This class provides a simple boolean input element.
    ``None`` is also allowed!

    Default representation is:

        * ``[✔]`` True
        * ``[✘]`` False
        * ``[❓]`` None

    Args:
        x,y (int): Position of the list view
        data (bool): ``True``, ``False`` or ``None`` representing the input of the BoolInput element
    """
    def __init__(self, x=0, y=0, data=None):
        Text.__init__(self)
        self.x     = x
        self.y     = y
        self.data  = None
        self.true  = "✔"
        self.false = "✘"
        self.none  = "❓"


    def SetRepresentation(self, true=None, false=None, none=None):
        """
        Define the representation of True, False and None in form of an Unicode character.

        Args:
            true,false,none (str): Unicode to represent one of the three states

        Returns:
            *Nothing*

        Raises:
            TypeError: when an argument is not ``None`` and not of type string
            ValueError: when the string is larger than one character
        """

        if true:
            if type(true) != str:
                raise TypeError("Argument must be of type string or have the value None")
            if len(true) != 1:
                raise ValueError("Only one character allowed")
            self.true = true

        if false:
            if type(false) != str:
                raise TypeError("Argument must be of type string or have the value None")
            if len(false) != 1:
                raise ValueError("Only one character allowed")
            self.false = false

        if none:
            if type(none) != str:
                raise TypeError("Argument must be of type string or have the value None")
            if len(none) != 1:
                raise ValueError("Only one character allowed")
            self.none = none



    def SetData(self, data):
        """
        This method sets the data of the input element

        Args:
            data (bool): ``True``, ``False`` or ``None`` representing the input of the BoolInput element

        Returns:
            *Nothing*
        """
        self.data = data


    def GetData(self):
        """
        Returns the string from the input element

        Returns:
            The input as bool or ``None``
        """
        return self.data


    def Draw(self):
        """
        This method draws the input control.
        """
        self.SetColor("1;37", "44")
        self.SetCursor(self.x, self.y)
        self.PrintText("[ ]")
        self.SetCursor(self.x+1, self.y)
        if self.data == True:
            self.SetColor("1;32", "44")
            self.PrintText(self.true)
        elif self.data == False:
            self.SetColor("1;31", "44")
            self.PrintText(self.false)
        elif self.data == None:
            self.SetColor("1;33", "44")
            self.PrintText(self.none)


    def HandleKey(self, key):
        """
        Space key toggles the value of the input element.
        When the previos value was ``None``, ``True`` will be the next.
        Then it alters between ``True`` and ``False``

        Args:
            key (str): Key name that shall be handled

        Returns:
            *Nothing*
        """
        if key == " ":
            if self.data == True:
                self.data = False
            else:
                self.data = True
            self.Draw()



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

