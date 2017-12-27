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

import tty
import termios
import sys
import os

class Text(object):
    r"""
    This class handles the shell output.
    It sets color and cursor settings and handles the screen.

    The default color is gray text on black background (``0;37;40``).

    Whenever a parameter is a color, the ANSI escape format for colors as strings were expected.
    These strings were sent to the terminal as shown in the following code example:

    .. code-block:: python

        def SetColor(color):
            print("\033[%sm" % color, end="")

        SetColor("1;32")    # bright green text
        SetColor("44")      # blue background

    """
    KEY_ESCAPE      = "\x1B"
    KEY_BACKSPACE   = "\x7F"

    def __init__(self):
        self.fgcolor = "37"
        self.bgcolor = "40"


    def SetColor(self, fgcolor=None, bgcolor=None):
        """
        This method calls :meth:`~SetFGColor` and :meth:`~SetBGColor`.
        """
        self.SetFGColor(fgcolor)
        self.SetBGColor(bgcolor)

    def SetFGColor(self, color=None):
        """
        This method sets the foreground (text) color.
        If the color argument is ``None``, then the default foreground color gets used.
        If the color argument is a color, then a new default foreground color gets defined and set.
        Next time this method gets called without an argument, this new color will be used as default.

        Args:
            color (str): New foreground (text) color

        Returns:
            *Nothing*

        Raises:
            TypeError: When argument is set and not a string
        """
        if color != None and type(color) != str:
            raise TypeError("Color must be a string with an ANSI color code.")

        if color:
            self.fgcolor = color
        print("\033[%sm" % (self.fgcolor), end="")

    def SetBGColor(self, color=None):
        """
        This method sets the background color.
        If the color argument is ``None``, then the default background color gets used.
        If the color argument is a color, then a new default backgound color gets defined and set.
        Next time this method gets called without an argument, this new color will be used as default.

        Args:
            color (str): New background color

        Returns:
            *Nothing*

        Raises:
            TypeError: When argument is set and not a string
        """
        if color != None and type(color) != str:
            raise TypeError("Color must be a string with an ANSI color code.")

        if color:
            self.bgcolor = color
        print("\033[%sm" % (self.bgcolor), end="")


    def SetCursor(self, x, y):
        """
        This method sets the position of the curser.
        The top left corner is at position *x=0; y=0*.
        *y* represents the rows and *x* the columns.

        For setting the cursor the ANSI escape sequence ``[y;xH`` gets used.

        Args:
            x (int): Column position of the cursor
            y (int): Row position of the cursor

        Returns:
            *Nothing*

        Raises:
            TypeError: When *x* or *y* are not of type integer
            ValueError: When *x* or *y* are negative
        """
        if type(x) != int or type(y) != int:
            raise TypeError("The cursor coordinates must be of type int!")
        if x < 0 or y < 0:
            raise ValueError("No negative values for cursor coordinates allowed!")

        print("\033[%d;%dH" % (y+1,x+1), end="")    # I start at (0,0), vt100 at (1,1)

    def ShowCursor(self, show=True):
        """
        This method makes the cursor visible or invisible.

        Therefore the ANSI escape seqneces ``[?25h`` and ``[?25l`` will be used.

        Args:
            show (bool): ``True``: Make cursor visible, ``False``: Hide cursor

        Returns:
            *Nothing*
        """
        if show:
            print("\033[?25h")
        else:
            print("\033[?25l")


    def ClearScreen(self):
        """
        This method clears the screen using the ANSI escape squence ``[2J``.

        Returns:
            *Nothing*
        """
        print("\033[2J", end="")

    def FlushScreen(self):
        """
        This method forces the shell to flush the *stdout* buffer.
        After calling this method, everything written into the output buffer will be visible on the screen.

        Returns:
            *Nothing*
        """
        sys.stdout.flush()

    def GetScreenSize(self):
        """
        This method returns the screen size as columns and rows.
        For detecting the screen size, the tool ``stty`` gets called:

        .. code-block:: bash

            stty size

        Returns:
            columns, rows (as integer)
        """
        # https://stackoverflow.com/questions/566746/how-to-get-linux-console-window-width-in-python
        rows, columns = os.popen('stty size', 'r').read().split()
        return int(columns), int(rows)


    def PrintText(self, text):
        """
        This method simply prints text to the screen.
        It does nothing more than:
        
        .. code-block:: python
            
            print(text, end="")

        So instead of the "normal" print, there will be no line break at the end.

        Returns:
            *Nothing*
        """
        print(text, end="")


    def GetRawKey(self):
        """
        This method reads a raw key input from the input buffer without printing it on the screen.

        Usually you want to use the more abstract method :meth:`~GetKey`

        Returns:
            The key from the input buffer
        """
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    def GetKey(self):
        """
        This method returns the name of the pressed key.
        The key input gets not printed to the screen.

        Until now, the following keys will be recognized:

            * The usual prinable keys
            * ``escape`` (Must be hit twice)
            * ``enter``, ``backspace``, ``delete``
            * ``backtab`` (shift+tab)
            * ``up``, ``down``, ``left``, ``right``
            * ``Ctrl-D``

        In case you want to get other keys, it is easy to add them by editing the code of this method.
        I just implemented the one I need for the :class:`~lib.clui.listview.ListView` UI element.

        Returns:
            The pressed key. If it is a special key, then the name of the key gets returnd as string.
            ``None`` will be returnd for unknown keys.
        """
        key = self.GetRawKey()
        if key == "\x0D":
            return "enter"
        elif key == Text.KEY_BACKSPACE:
            return "backspace"
        elif key == "\04":
            return "Ctrl-D"
        elif key != Text.KEY_ESCAPE:
            return key

        key = self.GetRawKey()
        if key == Text.KEY_ESCAPE:
            return "escape"
        elif key != "[":
            return None

        key = self.GetRawKey()
        if key == "\x41":
            return "up"
        elif key == "\x42":
            return "down"
        elif key == "\x43":
            return "right"
        elif key == "\x44":
            return "left"
        elif key == "Z":
            return "backtab"

        # In case of 3, there is more comming
        if key != "3":
            return None

        key = self.GetRawKey()
        if key == "~":
            return "delete"

        return None



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

