
MusicDB Commandline Modules
===========================

Modules are the interface to the MusicDB API for the command line tool ``musicdb``.
The following sections explain how to build a module.

Loading of Modules
------------------

When ``musicdb`` gets called, all python modules in the module directory gets loaded and the ``MDBM_CreateArgumentParser`` method gets called.
So, the command line argument parser can handle the parameter given to MusicDB.py.
After some further initialization the module gets called.
This is done by creating an instance of the class and calling the ``MDBM_Main`` method.
The ``__init__`` method gets the configuration and database loaded by musicdb.

The process can be seen as the following (simplified):

.. code-block:: python

   # Load Module
   modulename = "testmodul.py"
   modulspath = "./mods"
   modfp, modpath, moddesc = imp.find_module(modulename, [modulespath])
   module     = imp.load_module(modulename, modfp, modpath, moddesc)
   modclass   = getattr(module, modulename)

   # Extend musicdb arument paser set
   parserset  = argparser.add_subparsers(title="Modules", metavar="module", help="module help")
   modclass.MDBM_CreateArgumentParser(parserset, modulename)

   # Initialize musicdb
   args     = argparser.parse_args()
   config   = MusicDBConfig(args.configpath)
   database = MusicDatabase(args.databasepath)

   # Execute module
   modclass = getattr(modules[modulename], modulename)
   modobj   = modclass(config, database)
   exitcode = modobj.MDBM_Main(args)
   exit(exitcode)


Creation of new Modules
-----------------------

Modules are a class with the same man as the file.
The class is derived from the ``MDBModule`` class as shown in the following class diagram.
Modules are regular python files stored in the MusicDB module directory (``/mod``)
Each module class must have a static method ``MDBM_CreateArgumentParser(parserset, modulename)`` that returns a sub-argument-parser.

The argument parser module `argparse <https://docs.python.org/3/howto/argparse.html>`_ from Python is used for this.
Furthermore a main method called ``MDBM_Main(self, args)`` is needed.
This method implements the main function of the CLI mod and gets called if the command is given to ``musicdb``
Last, the ``__init__`` method gets a MusicDB Configuration object and a MusicDB Database object.

   .. graphviz::

      digraph hierarchy {
         size="5,5"
         node[shape=record,style=filled,fillcolor=gray95]
         edge[dir=back, arrowtail=empty]

         mdbmod [label = "{MDBModule||+ MDBM_CreateArgumentParser()\l+ MDBM_Main()\l}"]
         example [label = "{module||/+ MDBM_CreateArgumentParser()\l/+ MDBM_Main()\l}"]

         mdbmod -> example
      }

The following example shows a template of a module:

.. literalinclude:: ../../../share/modtemplate.py

Its base class is as simple as the following:

.. literalinclude:: ../../../musicdb/lib/modapi.py


