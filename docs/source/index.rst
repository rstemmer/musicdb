.. MusicDB documentation master file, created by
   sphinx-quickstart on Sun Apr 23 13:41:48 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to MusicDB's documentation!
===================================

.. figure:: ./images/mdblogo.png
   :align: left

**MusicDB** is a music manager, server and player that focus on music, not the software itself.
It manages music on a server following the "strange" concept of *The Filesystem is Always Right; the Database is Just for Augmentation*.
So, the tidiness of you music is not just inside *MusicDB* but all devices like your portable music-player or your car.
The music can be streamed by MusicDB and can be received by all kind of players like iTunes or VLC.
For streaming, MusicDB connects as source client to a local `Icecast <https://icecast.org/>`_ server.
This allows encrypted and protected streams so that they can be send  out to the internet.
The stream gets controlled by a WebUI that hides the ugliness of software behind a nice, music-oriented frontend.
Your music gets presented and is not just a database entry in a boring list of artists and albums.

With *MusicDB* you control a queue of music that gets streamed.
There is no playlist-management and no repeating loop of songs. 
If you are lazy to fill the queue with new songs, a random songs get append to the queue.
This random song selector does not use cryptographic randomness.
It uses lots of constraints that the selection *feels random*.
So recently played artists, albums and songs are blocked for a specific time until they can be added again.
Furthermore, only songs with a playtime within a configurable span will be append to prevent adding intros or "long-silent-songs".

*MusicDB* is for people who hate all other players. If there is another music player/manager you like (Beets, iTunes, Spotify, ...), you probably hate this one ;)
In the :doc:`/basics/comparison` chapter is a comparison with tools similar to *MusicDB*.

See the :doc:`/basics/concept` chapter and  :doc:`/basics/overview` to get an idea what it is like to use *MusicDB*.

------------------------------------

MusicDB has several abstraction layers shown in the following table:

+-------------------+-------------------+
| Bash Scripts      | HTML Documents    |
+-------------------+-------------------+
| `MusicDB CLI`_    | `MusicDB WebUI`_  |
+-------------------+-------------------+
| `MusicDB API`_                        |
+-------------------+-------------------+
| `MusicDB Libraries`_                  |
+-------------------+-------------------+
| Python            | Linux Tools       |
+-------------------+-------------------+

*Linux Tools*  are tools like ``icecast``, ``ffmpeg`` or ``id3edit``.
Some of those tools and libraries are side projects of the MusicDB project and also documented.
A list of these side projects can be found in the subsection `Other tools and Libraries`_.

With *Python*, the interpreter itself and all python modules needed to run MusicDB are meant.
A complete list of all dependencies can be found in ``check.sh`` in the scripts directory.

A documentation of the *Bash Scripts* an be found in the chapter :doc:`/usage/scripts`

In the following chapters, the basic concepts and philosophy of MusicDB and its components are explained.
Furthermore usage guides for MusicDB and how to handle its environment are provided.
Those chapters are for users as well as for developers.

.. toctree::
   :maxdepth: 1
   :caption: Concepts
   :glob:

   basics/*


.. toctree::
   :maxdepth: 1
   :caption: Usage
   :glob:

   usage/*


MusicDB CLI
===========

Modules are extensions for the command-line interface. 
Those classes are not supposed to be used inside MusicDB.
In the following documentation of each module the usage of them is also explained.
These chapters will help users to use MusicDB.
They provide lots of examples on how to use the MusicDB command line tool.

.. toctree::
   :maxdepth: 1
   :caption: CLI Modules
   :glob:

   mod/*


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


MusicDB API
===========

The MusicDB API Classes are made to be used inside MusicDB.
These classes implement the features of MusicDB.
Their input will not be perfectly checks for sanity, so do not confront those classes with the wild.
Check user-inputs before applying them to these classes - This should be done in the `MusicDB CLI`_ modules.
The documentation for these classes are for developer.
Users may also want look at this documentation to understand whats behind the functionality.

If MusicDB has a feature, it is here. If there is no class providing a feature, the feature does not exist.

The next section lists some quick links to introductions for easy extending MusicDB.
Then a section with all API modules follows

Quick Development Start
-----------------------

Here are some links to places worth reading before starting improving MusicDB:

   * An overview of the whole MusicDB Environment: :doc:`/basics/overview`
   * Adding a new column into the music database: :mod:`lib.db.musicdb`
   * Creating a new command line module: :doc:`/basics/mods`
   * Creating a new MusicDB API module: Place the file at ``mdbapi/*.py`` and follow :doc:`/basics/concept`
   * Adding a new option to the MusicDB Configuration: :mod:`lib.cfg.musicdb`

The best way to start learning how a feature works is by starting reading the UI module description.
Then reading the documentation of the API class, followed by the documentation of the used library classes.

.. toctree::
   :maxdepth: 1
   :caption: API Classes
   :glob:

   mdbapi/*



MusicDB Libraries
=================

These chapters document the low level classes and modules used by the MusicDB API classes.
This documentation is important for developer.
Those modules provide some abstractions mandatory for the functionality of all modules of MusicDB.
When developing a new module for MusicDB, never bypass these libraries!

.. toctree::
   :maxdepth: 1
   :caption: Libraries
   :glob:

   lib/*


MusicDB WebUI
=============

The documentation of the WebUI is not complete, and will never be.
The whole WebUI must and will be rebuilt in future using `WebAssembly (no HTTPS) <http://webassembly.org/>`_  technology.
JavaScript is simply not the right language for such a complex application.

.. toctree::
   :maxdepth: 1
   :caption: JaveScript Classes
   :glob:

   webui/*


Other tools and Libraries
=========================

There are lots of tools used by MusicDB's modules.
Whenever a method or function uses an external program, it is mentioned in the documentation.
Some of them are developed by myself:

``ID3Edit``:
   Is a tool that is used by MusicDB to edit and repair `ID3 Tags (no HTTPS) <http://id3.org/>`_ in mp3-files.
   Type ``id3edit --help`` for a short help. There is no more documentation yet, sorry.
   Source code can be found at `GitHub <https://github.com/rstemmer/id3edit>`__

``libprinthex``:
   Supports ID3Edit with fancy hexadecimal outputs for debugging invalid ID3 tags.
   Source code and documentation can be found at `GitHub <https://github.com/rstemmer/libprinthex>`__


Third Party Resources
---------------------

The following free third party components are included in MusicDB:

   * `jQuery 3 <https://jquery.com/>`_
   * `jQuery UI <https://jqueryui.com/>`_
   * `jQuery nanoScroller.js <https://jamesflorentino.github.io/nanoScrollerJS/>`_
   * `Silkscreen <https://www.kottke.org/plus/type/silkscreen/index.html>`_
   * `Source Sans Pro <https://github.com/adobe-fonts/source-sans-pro>`_ and `Source Serif Pro <https://github.com/adobe-fonts/source-serif-pro>`_
   * `DejaVuSans <https://github.com/dejavu-fonts/dejavu-fonts>`_
   * `Font Awesome <https://fontawesome.io/>`_


Indices and tables
==================

   * :ref:`genindex`
   * :ref:`modindex`

.. toctree::
   :maxdepth: 1
   :caption: Other
   :glob:

   other/*

