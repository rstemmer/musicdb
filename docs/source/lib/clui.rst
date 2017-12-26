
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
         BoolInput   [label = "{BoolInput||+ Draw()\l+ HandleKey\l}"]

         Text        -> Frame
         Text        -> TextInput
         Text        -> BoolInput
         Text        -> ButtonView

         Frame       -> Pane
         
         Pane        -> ListView
         Pane        -> Group

         ListView    -> Dialog
         ButtonView  -> Dialog

         Group       -> HGroup
         Group       -> VGroup

         TabGroup

      }


Text
----

.. automodule:: lib.clui.text

.. autoclass:: lib.clui.text.Text
   :members:


Frame
-----

.. automodule:: lib.clui.frame

.. autoclass:: lib.clui.frame.Frame
   :members:


Pane
----

.. automodule:: lib.clui.pane

.. autoclass:: lib.clui.pane.Pane
   :members:


ButtonView
----------

.. automodule:: lib.clui.buttonview

.. autoclass:: lib.clui.buttonview.ButtonView
   :members:


ListView
--------

.. automodule:: lib.clui.listview

.. autoclass:: lib.clui.listview.ListView
   :members:


Dialog
------

.. automodule:: lib.clui.dialog

.. autoclass:: lib.clui.dialog.Dialog
   :members:


TextInput
---------

.. automodule:: lib.clui.textinput

.. autoclass:: lib.clui.textinput.TextInput
   :members:


BoolInput
---------

.. automodule:: lib.clui.boolinput

.. autoclass:: lib.clui.boolinput.BoolInput
   :members:


TabGroup
--------

.. automodule:: lib.clui.tabgroup

.. autoclass:: lib.clui.tabgroup.TabGroup
   :members:

