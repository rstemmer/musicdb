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

from lib.clui.pane       import Pane
from lib.clui.listview   import ListView
from lib.clui.buttonview import ButtonView

class Dialog(ListView, ButtonView):
    """
    This class provides a dialog box that is organized like a list view.

    It provides one input element per line over several lines.
    The lines can be selected using the up (↑) and down (↓) key.
    Pressing the space bar on an :class:`~lib.clui.boolinput.BoolInput` toggles its value.
    On enter (↵), the changes shoud be committed, on escape (␛) they should be rejected.

    Beside the list of input elements a :class:`~lib.clui.buttonview.ButtonView` gets printed at the bottom of
    the dialog view telling the user about the key mentioned above.

    The dialog works on a list with each element beeing a tuple of a label, the control itself and a hint for the user.

    Example on using a Dialog:

        .. code-block:: python

            dialog     = Dialog("Add Unicode Icon", 1, 1, 40, 10)
            nameinput  = TextInput()
            iconinput  = TextInput()
            varselector= BoolInput()
            dialog.AddInput("Name:",  self.nameinput,   "Visibly for user")
            dialog.AddInput("Icon:",  self.iconinput,   "Unicode char")
            dialog.AddInput("U+FE0E:",self.varselector, "Do not replace with emoji")


    Args:
        title (str): Title of the list view
        x,y (int): Position of the list view
        w,h (int): Width and height
    """
    def __init__(self, title=None, x=0, y=0, w=0, h=0):
        ListView.__init__(self, title, x, y, w, h)
        ButtonView.__init__(self, align="center")

        self.elements       = []  # ListView works on this list. It contains a tuple (label, control, hint)
        self.maxlabellength = 0
        self.maxhintlength  = 0

        self.AddButton("↑", "Go up")
        self.AddButton("↓", "Go down")
        self.AddButton("↵", "Commit")
        self.AddButton("␣", "Toggle")
        self.AddButton("␛", "Cancel")


    def AddInput(self, label, control, hint=None):
        """
        This method adds a new control to the list of controls.
        The input control element must provide a ``Draw`` and a ``HandleKey`` method.
        Position and width of the control element will be calculated when they get printed.
        The label gets printed in front of the control element, the hint at the end of the list entry.

        The following inputs are suitable for the dialog:
            * :class:`lib.clui.textinbut.TextInput`
            * :class:`lib.clui.boolinput.BoolInput`

        Args:
            label (str): Label of the input element
            control: The input element itself
            hint (str): An additional hint to the input element. ``None`` for no hint.

        Returns:
            *Nothing*
        """
        if hint == None:
            hint = ""
        self.maxlabellength = max(self.maxlabellength, len(label))
        self.maxhintlength  = max(self.maxhintlength,  len(hint))
        self.elements.append((label, control, hint))


    def onDrawElement(self, element, number, maxwidth):
        """
        This method gets called when an element gets printed into the dialog view.
        Keep in mind that the dialog element is not able to scroll.

        The ``element`` is a tuple containing the label, the control element and the hint.
        If the number of characters is too high, the hints will not be printed.
        The number of printable characters gets calculated by the with of the label and hint of each row.
        It should be at least 10 characters be left for the control, and 2 for spaces around the control.

        Args:
            element: The element that shall be printed.
            number (int): The index of the element in the list of all elements and at the same time the y coordinate
            maxwidth (int): *Will be ignored*

        Returns:
            *Nothing*

        Raises:
            ValueError: In case the with of the dialog is to small to print at least the label and the input control
        """
        label   = element[0]
        control = element[1]
        hint    = element[2]

        x = self.x + 1
        y = self.y + number + 1
        w = self.w - 2

        # Draw label
        self.SetColor()
        self.SetCursor(x, y)
        string = label.rjust(self.maxlabellength)
        self.PrintText(string)

        # Draw control
        control.x = x + self.maxlabellength + 1
        control.y = y
        control.w = w - (self.maxlabellength + self.maxhintlength + 2) # +2 for spaces between the elements
        if control.w <= 10:
            # when the control gets too small, reject the hint and only print the control
            control.w = w - (self.maxlabellength + 1) # +1 for spaces between the elements
            if control.w <= 10:
                raise ValueError("The width of this dialog is too small!")
            control.Draw()
            return

        control.Draw()

        # Draw hint
        self.SetColor()
        self.SetCursor(x + self.maxlabellength + control.w + 2, y)
        string = hint.ljust(self.maxhintlength)
        self.PrintText(string)



    def onAction(self, element, key):
        """
        This method gets called when a key gets passed to the :meth:`~HandleKey` method.
        It is supposed to get passed to the selected control element.
        
        Args:
            element: The selected element in the list
            key (str): The key that was pressed while the element was selected

        Returns:
            *Nothing*
        """
        control = element[1]
        control.HandleKey(key)


    def SetData(self, elements):
        """
        Raises:
            NotImplementedError: *alway*
        """
        raise NotImplementedError("There are no data you can set in the dialog.")


    def SetSelectedData(self, element):
        """
        Raises:
            NotImplementedError: *alway*
        """
        raise NotImplementedError("There are no data you can set in the dialog.")


    def GetSelectedData(self):
        """
        Raises:
            NotImplementedError: *alway*
        """
        raise NotImplementedError("There are no data you can set in the dialog.")


    def Draw(self):
        """
        This method draws the list of control elements.
        """
        self.SetFGColor("1;31")
        Pane.Draw(self)

        for index, element in enumerate(self.elements):
            if self.linemarker == index:
                bgcolor = "46"
            else:
                bgcolor = "40"
            self.SetColor("1;34", bgcolor)
            self.onDrawElement(element, index, self.w-2)

        self.SetColor("1;31", "40") # reset color

        x = self.x + 1
        y = self.y + self.h - 1
        w = self.w - 2
        ButtonView.Draw(self, x, y, w)
        #self.buttons.Draw(x, y, w)


    def HandleKey(self, key):
        """
        This method must be called whenever a key was pressed and this dialog is "active".
        It expects the key name returned by :meth:`lib.clui.text.Text.GetKey`.

        If the key is ``"up"`` the element above the current selected element gets selected.
        If the key is ``"down"`` the one below will be selected.
        This will be done by passing the *up* and *down* key to the ``HandleKey`` method of the base class.

        Any other key gets passed to the :meth:`~onAction` method of this class.

        After handling an key, the :meth:`~Draw` method gets called to refresh the view.

        Args:
            key (str): Key name that shall be handled

        Returns:
            *Nothing*
        """
        if key == "up" or key == "down":
            ListView.HandleKey(self, key)

        else:
            if self.elements:
                self.onAction(self.elements[self.linemarker], key)
            self.Draw()


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

