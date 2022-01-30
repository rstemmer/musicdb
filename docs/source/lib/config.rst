
Configuration Access
====================

The following class diagram shows the implementation of MusicDBs configuration and state management.
Only the more important methods are shown in the diagram.
For a list of all methods see the related documentation of the class.

   .. graphviz::

      digraph hierarchy {
         size="5,5"
         node[shape=record,style=filled,fillcolor=gray95]
         edge[dir=back, arrowtail=empty]

         csv      [label = "{CSVFile||+ Read()\l+ Write()\l}"]
         config   [label = "{Config||+ Load()\l+ Reload()\l+ Save()\l+ OptionAvailable()\l+ Get()\l+ Set()\l}"]
         musicdb  [label = "{MusicDBConfig||- GetDirectory()\l- GetFile()\l}"]
         extern   [label = "{ExternConfig||}"]
         mdbstate [label = "{MDBState||+ GetFilterlist()\l}"]

         config -> musicdb
         config -> extern
         config -> mdbstate
         csv    -> mdbstate [arrowtail=open]
      }


Base Configuration Classes
--------------------------

ini Files
^^^^^^^^^

.. automodule:: musicdb.lib.cfg.config

.. autoclass:: musicdb.lib.cfg.config.Config
   :members:


csv Files
^^^^^^^^^

.. automodule:: musicdb.lib.cfg.csv

.. autoclass:: musicdb.lib.cfg.csv.CSVFile
   :members:


MusicDB Configuration File
--------------------------

Detail of the MusicDB Configuration can be found under :doc:`/basics/config`.

.. automodule:: musicdb.lib.cfg.musicdb

.. autoclass:: musicdb.lib.cfg.musicdb.MusicDBConfig
   :members:


WebUI Configuration File
------------------------

.. automodule:: musicdb.lib.cfg.webui

.. autoclass:: musicdb.lib.cfg.webui.WebUIConfig
   :members:


External Storage Configuration File
-----------------------------------

.. automodule:: musicdb.lib.cfg.extern

.. autoclass:: musicdb.lib.cfg.extern.ExternConfig
   :members:


MusicDB State Files
-------------------

.. automodule:: musicdb.lib.cfg.mdbstate

.. autoclass:: musicdb.lib.cfg.mdbstate.MDBState
   :members:


WebSocket API Key File
----------------------

.. automodule:: musicdb.lib.cfg.wsapikey

.. autoclass:: musicdb.lib.cfg.wsapikey.WebSocketAPIKey
   :members:


