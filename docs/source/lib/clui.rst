
Command Line User Interface
===========================

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
         Group       [label = "{Group||+ Draw()\l}"]
         HGroup      [label = "{HGroup||/+ Draw()\l}"]
         VGroup      [label = "{VGroup||/+ Draw()\l}"]
         TabGroup    [label = "{TabGroup||+ HandleKey()\l}"]

         Text        -> Frame
         Frame       -> Pane
         
         Pane        -> ButtonView
         Pane        -> ListView
         Pane        -> Group

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


Group
-----

.. automodule:: lib.clui.group

.. autoclass:: lib.clui.group.Group
   :members:

.. autoclass:: lib.clui.group.HGroup
   :members:

.. autoclass:: lib.clui.group.VGroup
   :members:


TabGroup
--------

.. automodule:: lib.clui.tabgroup

.. autoclass:: lib.clui.tabgroup.TabGroup
   :members:

