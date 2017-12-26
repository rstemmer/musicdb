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

class ButtonView(Text):
    """
    This class provides a button view.
    It is a line where a key event is described.
    For example: ``[a:Add element][r:Remove element]``

    Example:

        .. code-block:: python

            cli  = Text()
            maxw, maxh = cli.GetScreenSize()

            # Place a button view in the middle of the line before the last line of the screen
            buttons = ButtonView(0, maxh-2, maxw, align="middle")
            buttons.AddButton("a", "Add new tag")
            buttons.AddButton("e", "Edit tag")
            buttons.AddButton("r", "Remove tag")

    Args:
        align (str): If the buttons are ``"left"``, ``"right"`` or ``"center"`` shall be aligned over the span of the View width.
    """
    def __init__(self, align="left"):
        Text.__init__(self)
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
        """
        This method adds a new button-description to the ButtonView.

        Args:
            key (str): A single Unicode character key
            name (str): What pressing that key will do

        Returns:
            *Nothing*

        Raises:
            TypeError: When ``key`` or ``name`` are not a string
            ValueError: When ``key`` is larger than one character
        """
        if type(key) != str or type(name) != str:
            raise TypeError("Arguments must be of type string")
        if len(key) > 1:
            raise ValueError("Key must not exceed one character")

        self.buttons.append((key, name))


    def Draw(self, x, y, w):
        """
        This method prints the ButtonView.
        It always uses the colors *red* for the [:]-characters, *light blue* for the key and *blue* for the description.

        Args:
            x,y (int): Position where to start printing the ButtonView
            w (int): Width of the ButtonView
        """
        rbuttons = [] # rendered buttons

        # calculate max button text length
        numbuttons = len(self.buttons)
        maxsize    = w // numbuttons
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
            x = x
        elif self.align == "c":
            x = x + (w - barlength) // 2
        elif self.align == "r":
            x = x + (w - barlength)

        self.SetCursor(x, y)
        for rbutton in rbuttons:
            self.PrintText(rbutton)



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

