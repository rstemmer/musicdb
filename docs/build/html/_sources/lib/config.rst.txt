
Configuration
=============

The following class diagram shows the implementation of MusicDBs configuration and state management.
Only the more important methods are shown in the diagram.
For a list of all methods see the related documentation of the class.

   .. graphviz::

      digraph hierarchy {
         size="5,5"
         node[shape=record,style=filled,fillcolor=gray95]
         edge[dir=back, arrowtail=empty]

         config   [label = "{Config||+ Load()\l+ Reload()\l+ Save()\l+ OptionAvailable()\l+ Get()\l+ Set()\l}"]
         musicdb  [label = "{MusicDBConfig||- GetDirectory()\l- GetFile()\l}"]
         extern   [label = "{ExternConfig||}"]
         mdbstate [label = "{MDBState||+ GetFilterlist()\l}"]

         config -> musicdb
         config -> extern
         config -> mdbstate
      }


Base Class
----------

.. automodule:: lib.cfg.config

.. autoclass:: lib.cfg.config.Config
   :members:

MusicDB Configuration
---------------------

Detail of the MusicDB Configuration can be found under :doc:`/basics/config`.

.. automodule:: lib.cfg.musicdb

.. autoclass:: lib.cfg.musicdb.MusicDBConfig
   :members:


External Storage Configuration
-------------------------------

.. automodule:: lib.cfg.extern

.. autoclass:: lib.cfg.extern.ExternConfig
   :members:


MusicDB State
-------------

.. automodule:: lib.cfg.mdbstate

.. autoclass:: lib.cfg.mdbstate.MDBState
   :members:





