Command Line Interface
======================

Beside the WebUI, MusicDB comes also with a command line interface.
Since version 8.0.0 this command line interface, see ``musicdb --help``, is supposed to be used for fixing critical issues only.

.. warning::

   It is recommend to use the *WebUI* for all management tasks.
   The command line interface is just for debugging, testing and fixing cirtical issues.

   Before using the command line interface create a backup of the Music Database ``music.db``.

   After using the command line interface restart the WebSocket server: ``systemctl restart musicdb``.


The MusicDB command line interface is a low level interface to some basic functionality of MusicDB.
Its main purpose is to debug and repair MusicDB.
The command liner interface (CLI) consists of several sub-commands.
These sub-commands are listed as sub-section in the left menu of this documentation.

To call a module give its name as parameter to ``musicdb``.
The name is the last parameter for ``musicdb``, all following parameters are parameters of the module.
To be allowed to execute ``musicdb``, you need to be in the group ``musicdb``.

.. code-block:: bash

   # Change effective groupe
   newgrp musicb

   # Show help for musicdb, and after that, for the artwork-module
   musicdb --help
   musicdb artwork --help

   # Call the stats-module:
   musicdb stats

   # Remove an artist from the database. Restart the server to update its caches
   musicdb database remove /var/music/Bad\ Artist
   sudo systemctl restart musicdb

The following command line modules exist:

.. toctree::
   :maxdepth: 1
   :caption: CLI Modules
   :glob:

   ../mod/*

