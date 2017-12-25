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

from lib.clui.text   import Text

class Frame(Text):
    """
    This class provides an unicode based frame that gets printed around a certain area.
    
    There are the following styles available:

    ``LINESTYLE_NORMAL``:

        .. code-block:: bash

            ┌─┐
            │ │
            └─┘

    ``LINESTYLE_BOLD``:

        .. code-block:: bash

            ┏━┓
            ┃ ┃
            ┗━┛

    ``LINESTYLE_ASCII``:

        .. code-block:: bash

            +-+
            | |
            +-+

    ``LINESTYLE_DOUBLE``:

        .. code-block:: bash

            ╔═╗
            ║ ║
            ╚═╝

    ``LINESTYLE_ROUND``:

        .. code-block:: bash

            ╭─╮
            │ │
            ╰─╯


    Args:
        linestyle: The style used to draw the lines. The default linestyle is ``LINESTYLE_NORMAL``.
    """

    LINESTYLE_NORMAL    = 0
    LINESTYLE_BOLD      = 1
    LINESTYLE_ASCII     = 2
    LINESTYLE_DOUBLE    = 3
    LINESTYLE_ROUND     = 4
    LINESTYLES = [
            ["─", "│", "┌", "┐", "└", "┘"],
            ["━", "┃", "┏", "┓", "┗", "┛"],
            ["-", "|", "+", "+", "+", "+"],
            ["═", "║", "╔", "╗", "╚", "╝"],
            ["─", "│", "╭", "╮", "╰", "╯"],
            ]

    def __init__(self, linestyle=LINESTYLE_NORMAL):
        Text.__init__(self)
        self.linestyle = linestyle


    def SetLineStyle(self, linestyle):
        """
        This method can be used to set a different line style.
        You may want to call :meth:`~Draw` to redraw the frame with the new style.

        Args:
            The new style

        Returns:
            *Nothing*

        Raises:
            ValueError: When the argument does not address a valid style
        """
        if linestyle not in [LINESTYLE_NORMAL, LINESTYLE_BOLD, LINESTYLE_ASCII, LINESTYLE_DOUBLE, LINESTYLE_ROUND]:
            raise ValueError("Invalid line style.")
        self.linestyle = linestyle


    def Draw(self, x, y, w, h):
        """
        This method draws the frame around a certain area.

        The upper left corner of the frame will be at *(x;y)*, the bottom right corner at *(x+w;y+h)*

        Only the frame characters gets drawn.
        Every character inside the frame stays.
        So this method can also be called to draw a frame around already printed content.

        Args:
            x,y (int): Start position of the frame (top left corner)
            w (int): width of the frame
            h (int): height of the frame

        Returns:
            *Nothing*

        Raises:
            TypeError: When one of the arguments is not of type integer.
        """
        if type(x) != int or type(y) != int or type(w) != int or type(h) != int:
            raise TypeError("Coordinates, width and height must be of type integer")
        if x < 0 or y < 0:
            raise ValueError("No negative coordinates allowed")

        linechars = Frame.LINESTYLES[self.linestyle]
        self.SetCursor(x, y)
        self.PrintText(linechars[2] + linechars[0]*(w-2) + linechars[3])
        for row in range(y+1, y+h-1):
            self.SetCursor(x, row)
            self.PrintText(linechars[1] + " "*(w-2) + linechars[1])
        self.SetCursor(x, y+h-1)
        self.PrintText(linechars[4] + linechars[0]*(w-2) + linechars[5])


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

