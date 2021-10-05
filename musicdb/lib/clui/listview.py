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

from musicdb.lib.clui.pane import Pane

class ListView(Pane):
    r"""
    This class provides a ListView that shows a list the user can scroll through using the arrow keys.

    The data shown in the list must be a string.
    For derived classes, they can be considered abstract and contain any kind of type as long as
    you adopt the :meth:`~onDrawElement` method.

    An example on how to use this class with complex data structures:

        .. code-block:: python

            class MusicView(ListView):
                def __init__(self, title):
                    ListView.__init__(self, title)

                def SetData(self, artists, albums, songs):
                    artistdata = [("artist", name) for name in artists]
                    albumdata  = [("album",  name) for name in albums ]
                    songdata   = [("song",   name) for name in songs  ]

                    data = []
                    data.extend(artistdata)
                    data.extend(albumdata )
                    data.extend(songdata  )
                    ListView.SetData(self, data)

                def onDrawElement(self, element, number, maxwidth):
                    tag  = element[0]
                    path = element[1]
                    maxnamelen = maxwidth - 6   # - "[xxx] "

                    string = "\033[1;30m["
                    if tag == "artist":
                        string += "art"
                    elif tag == "album":
                        string += "alb"
                    elif tag == "song":
                        string += "sng"
                    else:
                        string += "INV"
                    string += "] \033[1;34m"
                    string += path[:(maxnamelen)].ljust(maxpathlen)
                    return string

            artists = ["Artist A", "Brtist B"]
            albums  = ["An album", "And Another Album"]
            songs   = ["This is a song name"]
            sv  = MusicView("Music", 2, 2, 10, 5)
            sv.SetData(artists, albums, songs)
            sv.Draw()


    The elements in the list are stored in a variable ``elements``.
    This list can be maintained using :meth:`~SetData`.

    A second variable ``linemarker`` points (in form of an index) to the selected element in this list.
    The element the linemarker points to can be accessed via :meth:`~GetSelectedData` and :meth:`~SetSelectedData`

    When the list of element exceeds the height of the list, a scroll bar will be printed in place of the right frame edge.

    Args:
        title (str): Title of the list view
        x,y (int): Position of the list view
        w,h (int): Width and height
    """
    def __init__(self, title=None, x=0, y=0, w=0, h=0):
        Pane.__init__(self, title, x, y, w, h)
        self.listoffset     = 0
        self.linemarker     = 0
        self.elements       = []


    def onDrawElement(self, element, number, maxwidth):
        r"""
        This method gets called when an element gets printed into the list view.
        To customize how elements will appear in the list, overload this method.

        The returned string can contain ANSI Escape Sequences for coloring.
        The number of printable character should not exceed the maximum width ``maxwidth``.
        Furthermore the string should be exact ``maxwidth`` wide.

        An example how to implement a custom ``onDrawElement`` method can be seen in the following code example:

        .. code-block:: python

            def onDrawElement(self, element, number, maxwidth):
                # Print the element number in front of each entry.
                # Alternate the text color with each line. Odd lines in white, even in blue.

                num = "%2d: "%(number)      # start list entry with the index of the element
                val = element[:maxwidth-4]  # Limit string to max width. 4 Characters are consumed for the num variable

                # Alternating colors with each line
                # Colors do not count to the width of the string because they are not printable
                if num % 2:
                    color = "\033[1;37m"    # Set color to white for odd lines
                else:
                    color = "\033[1;34m"    # Set color to blue for even lines
    
                return color + num + val

        Args:
            element: The element that shall be printed.
            number (int): The index of the element in the list of all elements
            maxwidth (int): The maximum number of characters that can be printed in one line of the list view

        Returns:
            The string that will be printed in one line of the list view
        """
        string = str(element)
        string = string[:maxwidth]
        string = string.ljust(maxwidth)
        return string


    def onAction(self, element, key):
        """
        This method gets called when a key gets passed to the :meth:`~HandleKey` method.
        It is supposed to process the selected line in the list of elements.
        In this class, nothing will be done with the data.

        This function must return the processed element back to the list.
        It is also possible to return a new element to replace the old one.
        When a line shall not be updated, return None.
        A case where this may be useful will be presented in the following example:

        .. code-block:: python
            
            def onAction(self, element, key):
                # this method manipulates a list of numbers

                if key == "r":      # remove element
                    self.elements.remove(element)
                    return None

                elif key == "a":    # append number to list
                    self.elements.append("0")

                elif key == "0":    # reset number
                    return "0"

                elif key == "+":    # increment number
                    element = str(int(element) + 1)

                elif key == "-":    # decrement number
                    element = str(int(element) - 1)

                return element

        When the last element gets removed, the ``linemarker`` variable gets moved to the previous line.
        Otherwise it stays at its position that will now be the element next after the removed one.
        
        Args:
            element: The selected element in the list
            key (str): The key that was pressed while the element was selected

        Returns:
            The modified element that will be put back in the list of elements.
        """
        return element


    def SetData(self, elements):
        """
        This method can be used to initialize the list of data that will be shown in the list view
        If the :meth:`~onDrawElement` method is not overloaded, the list must contain strings.

        After setting the new ``elements`` list, the ``linemarker`` gets set to the begin of the list.

        Args:
            elements (list): A list of data

        Returns:
            *Nothing*
        """
        self.elements = elements
        self.linemarker = 0
        self.listoffset = 0


    def GetData(self):
        """
        Returns the list of elements.

        Returns:
            The list of elements of the list view
        """
        return self.elements


    def SetSelectedData(self, element):
        """
        Replaces the selected element with a new one.
        This method can be used to interact with the list without triggering the :meth:`~onAction` callback.

        Args:
            element: An element that replaces the selected element

        Returns:
            *Nothing*
        """
        self.elements[self.linemarker] = element


    def GetSelectedData(self):
        """
        This method returns the selected element from the list.

        Returns:
            The selected element
        """
        return self.elements[self.linemarker]


    def Draw(self):
        """
        This method draws the list of elements.
        If the list exceeds the height of the list view, a scroll bar gets added and the user can scroll though the data.

        The background of the list view will be black.
        The surrounding frame is red.
        The lines in the list will be printed in blue.
        The selected line gets a cyan background color.

        Returns:
            *Nothing*
        """
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


    def HandleKey(self, key):
        """
        This method must be called whenever a key was pressed and this list view is "active".
        It expects the key name returned by :meth:`musicdb.lib.clui.text.Text.GetKey`.

        If the key is ``"up"`` the element above the current selected element gets selected.
        If the key is ``"down"`` the one below will be selected.
        Any other key gets passed to the :meth:`~onAction` method.
        Read the documentation of the :meth:`~onAction` method to see how the return value of that method gets processed.

        After handling an key, the :meth:`~Draw` method gets called to refresh the view.

        Args:
            key (str): Key name that shall be handled

        Returns:
            *Nothing*
        """
        if key == "up":
            if self.linemarker > 0:
                self.linemarker -= 1

            if self.linemarker < self.listoffset:
                self.listoffset -= 1

        elif key == "down":
            if self.linemarker < len(self.elements)-1:
                self.linemarker += 1

            if self.linemarker >= self.listoffset + self.h-2:
                self.listoffset += 1

        else:
            if self.elements:
                updatedelement = self.onAction(self.elements[self.linemarker], key)
                if updatedelement:
                    self.elements[self.linemarker] = updatedelement
                elif self.linemarker >= len(self.elements):
                    self.linemarker = len(self.elements)-1

        self.Draw()


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

