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
    """
    This class manages a group of UI elements based on the :class:`~lib.clui.pane.Pane` class.
    It is possible to add multiple panes to this group and print them all by just calling :meth:`~Draw` once.
    This makes only sense when using the derived classes :class:`~HGroup` or :class:`~VGroup` that rearrange the panes dynamically.

    Args:
        x,y (int): Position of the pane group
        w,h (int): Width and Height of that area
        space (int): Spaces (space-characters) between two panes.
    """
    def __init__(self, x, y, w, h, space=0):
        Pane.__init__(self, None, x, y, w, h)
        self.space = space
        self.panes = []

    def AddPane(self, pane):
        """
        Adds a pane to the group

        Args:
            pane: A pane that shall be added to the group

        Return:
            *Nothing*
        """
        self.panes.append(pane)
        self.Rearange()

    def Draw(self):
        """
        Calls for each pane the ``Draw`` method

        Return:
            *Nothing*
        """
        for pane in self.panes:
            pane.Draw()


class HGroup(Group):
    """
    See :class:`~Group`
    """
    def __init__(self, x, y, w, h, space=0):
        Group.__init__(self, x, y, w, h, space)

    def Rearange(self):
        """
        Calculates the position and with for each added pane to arrange them horizontal.

        Returns:
            *Nothing*
        """
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
    """
    See :class:`~Group`
    """
    def __init__(self, x, y, w, h, space=0):
        Group.__init__(self, x, y, w, h, space)

    def Rearange(self):
        """
        Calculates the position and with for each added pane to arrange them vertical.

        Returns:
            *Nothing*
        """
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

