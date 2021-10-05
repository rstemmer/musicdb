
Command Line User Interface
===========================

   .. warning::

      This library is very experimental.
      Handle with care and expect interface changes with the next update.

The Command Line User Interface (CLUI) is an unicode based "graphical" user interface library.
It provides some primitive UI elements documented in this section of the documentation.



   .. graphviz::

      digraph hierarchy {
         size="5,8"
         node[shape=record,style=filled,fillcolor=gray95]
         edge[dir=back, arrowtail=empty]

         Text        [label = "{Text||}"]
         Frame       [label = "{Frame||+ Draw()\l}"]
         Pane        [label = "{Pane||+ Draw()\l}"]
         ButtonView  [label = "{ButtonView||+ Draw()\l}"]
         ListView    [label = "{ListView||+ Draw()\l+ HandleKey()\l# onDraw()\l# onAction()\l}"]
         Dialog      [label = "{Dialog||/+ Draw()\l/+ HandleKey()\l}"]
         TabGroup    [label = "{TabGroup||+ HandleKey()\l}"]
         TextInput   [label = "{TextInput||+ Draw()\l+ HandleKey\l}"]
         NoTextInput [label = "{NoTextInput||\l/+ HandleKey\l}"]
         BoolInput   [label = "{BoolInput||+ Draw()\l+ HandleKey\l}"]

         Text        -> Frame
         Text        -> TextInput
         Text        -> BoolInput
         Text        -> ButtonView

         TextInput   -> NoTextInput
         Frame       -> Pane
         
         Pane        -> ListView
         Pane        -> Group

         ListView    -> Dialog
         ButtonView  -> Dialog

         TabGroup

      }


Text
----

.. automodule:: musicdb.lib.clui.text

.. autoclass:: musicdb.lib.clui.text.Text
   :members:


Frame
-----

.. automodule:: musicdb.lib.clui.frame

.. autoclass:: musicdb.lib.clui.frame.Frame
   :members:


Pane
----

.. automodule:: musicdb.lib.clui.pane

.. autoclass:: musicdb.lib.clui.pane.Pane
   :members:


ButtonView
----------

.. automodule:: musicdb.lib.clui.buttonview

.. autoclass:: musicdb.lib.clui.buttonview.ButtonView
   :members:


ListView
--------

.. automodule:: musicdb.lib.clui.listview

.. autoclass:: musicdb.lib.clui.listview.ListView
   :members:


Dialog
------

.. automodule:: musicdb.lib.clui.dialog

.. autoclass:: musicdb.lib.clui.dialog.Dialog
   :members:


TextInput
---------

.. automodule:: musicdb.lib.clui.textinput

.. autoclass:: musicdb.lib.clui.textinput.TextInput
   :members:

.. autoclass:: musicdb.lib.clui.textinput.NoTextInput
   :members:

BoolInput
---------

.. automodule:: musicdb.lib.clui.boolinput

.. autoclass:: musicdb.lib.clui.boolinput.BoolInput
   :members:


TabGroup
--------

.. automodule:: musicdb.lib.clui.tabgroup

.. autoclass:: musicdb.lib.clui.tabgroup.TabGroup
   :members:

