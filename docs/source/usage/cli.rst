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
These sub commands are listed as sub-section in the left menu of this documentation.


OLD:


Modules are extensions for the command-line interface. 
Those classes are not supposed to be used inside MusicDB.
In the following documentation of each module the usage of them is also explained.
These chapters will help users to use MusicDB.
They provide lots of examples on how to use the MusicDB command line tool.

CLI Usage
---------

To call a module give its name as parameter to ``musicdb``.
The name is the last parameter for ``musicdb``, all following parameters are parameters of the module.

.. code-block:: bash

   # Show help for musicdb, and after that, for the musicai-module
   musicdb --help
   musicdb artwork --help

   # List all availabe modules
   musicdb --version

   # Call the stats-module:
   musicdb stats


.. toctree::
   :maxdepth: 1
   :caption: CLI Modules
   :glob:

   ../mod/*


Using the database module
^^^^^^^^^^^^^^^^^^^^^^^^^

The following example shows how to add artists and albums using the ``database`` module.
For details see :doc:`/mod/database`.

* The ``musicdb database`` command: :doc:`/mod/database` (the hard way)

After adding the music via ``musicdb database`` or ``musicdb repair``,
the artwork must be imported using ``musicdb artwork`` (:doc:`/mod/artwork`).
It can happen that the automatic import of the artwork does not work.
This is usually the case when there is no artwork embedded in the audio files.
In this case the artwork file path must be given to ``musicdb artwork`` explicitly.
See the :doc:`/mod/artwork` documentation where this step is described.
