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
    """
    This class provides a ListView that shows a list the user can scroll through using the arrow keys.

    The data shown in the list must be a string in this class.
    For derived classes, they can be considered abstract and contain any kind of type as long as
    you adopt the :meth:`~onDrawElement` method.

    An example on how to use this class:

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
        self.drawcallback   = None


    def onDrawElement(self, element, number, maxwidth):
        """
        This method gets called when an element gets printed into the list view.
        To customize how elements will appear in the list, overload this method.

        The returned string can contain ANSI Escape Sequences for coloring.
        The number of printable character should not exceed the maximum width ``maxwidth``.

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
        In this class, nothing will be done.
        
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

        Args:
            elements (list): A list of data

        Returns:
            *Nothing*
        """
        self.elements = elements
        if self.linemarker >= len(self.elements):
            self.linemarker = len(self.elements)-1


    def SetSelectedData(self, element):
        """
        Replaces the selected element with a new one.

        Args:
            element: An element that replaces the selected element

        Returns:
            *Nothing*
        """
        self.elements[self.linemarker] = element


    def GetSelectedData(self):
        """
        This method returns the selected element.

        Returns:
            The selected element
        """
        return self.elements[self.linemarker]


    def Draw(self):
        """
        This method draws the list of elements.
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
        """
        This method must be called whenever a key was pressed and this ListView is "active".
        It expects the key name returned by :meth:`lib.clui.text.Text.GetKey`.

        If the key is ``"up"`` the element above the current selected element gets selected.
        If the key is ``"down"`` the one below will be selected.
        Any other key gets passed to the :meth:`~onAction` method.

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

            self.Draw()

        elif key == "down":
            if self.linemarker < len(self.elements)-1:
                self.linemarker += 1

            if self.linemarker >= self.listoffset + self.h-2:
                self.listoffset += 1

            self.Draw()

        else:
            if self.elements:
                updatedelement = self.onAction(self.elements[self.linemarker], key)
                if updatedelement:
                    self.elements[self.linemarker] = updatedelement
            self.Draw()


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

