
MusicDB Data Files and Directories
==================================

In this section, all data and configuration files, as well as all directories used and maintained by MusicDB are described.


Music Directory
---------------

The music directory is the directory that contains the music files
that will be managed, presented and streamed by MusicDB.
It is mandatory for MusicDB to work correctly.

The music directory can be configured in the MusicDB configuration file ``/etc/musicdb.ini``.
Enter the absolute path at ``[directories]->music``.

Three parties need to have access to the files:

   * MusicDB, Read/Write: Needs to have access to the music directories and files to manage them.
   * You, the user, Read/Write (optional): To manage music by yourself, upload music via ``scp`` or bypass MusicDB at all.
   * The Web Server, Read-Only (optional): To allow the client user to listen to single files directly via the "preview"-feature.

The expected ownership is ``$user:musicdb`` with the permission ``rwxrwxr-x``.
With ``$user`` as your user name.
If MusicDB has no read access to the music directory, it cannot be executed.
In case it only has read access it can be executed, but some features will not work.

To give the Web Server access to the music directory you have to enable it inside the MusicDB web server configuration.
See the :doc:`/usage/install` instruction for further details on how to setup the web server.


MusicDB Data Directory
----------------------

The default path of the data directory is ``/var/lib/musicdb``.
It contains all the variable data used and needed by MusicDB, including the databases.

MusicDB needs to have write access to all of those directories.
On installation these file/directory structure gets created and setup correct.
Usually the user does not have to care about this.

The data directory can be configured in the MusicDB configuration file ``/etc/musicdb.ini``.
Enter the absolute path at ``[directories]->data``.

The expected ownership is ``$user:musicdb`` with the permission ``rwxrwxr-x``.
With ``$user`` as your user name.

It contains the following sub directories:

state/:
   This directory is used to provide and maintain a consistent state for the MusicDB WebSocket Server.
   It is mainly maintained by :mod:`musicdb.lib.cfg.mdbstate`

uploads/:
   The uploads directory contains temporary uploaded data.
   This directory is mainly maintained by :doc:`/taskmanagement/uploadmanager`

tasks/:
   Persistent state of tasks that are processed by the :mod:`musicdb.taskmanagement.managementthread`
   and managed by the :doc:`/taskmanagement/taskmanager`.

webdata/:
   This directory contains all data that needs to be available by the HTTPS web server.
   It contains the WebUI configuration ``config.js`` as well as the artwork directory.
   Keep in mind that the Web Server needs to have read access to all data inside the ``webdata`` directory.

   The artwork sub-directory comes with write access for the whole ``musicdb`` group to allow other tools take part in managing the music artworks.

===============  ===========  ===========  =============
Directory        Owner        Group        Permissions
===============  ===========  ===========  =============
state            ``musicdb``  ``musicdb``  ``rwxr-xr-x``
uploads          ``musicdb``  ``musicdb``  ``rwxr-x---``
tasks            ``musicdb``  ``musicdb``  ``rwxr-x---``
webdata          ``musicdb``  ``musicdb``  ``rwxr-xr-x``
webdata/artwork  ``musicdb``  ``musicdb``  ``rwxrwxr-x``
===============  ===========  ===========  =============


MusicDB Log File
----------------

MusicDB uses the systemd journal for logging.
Additionally it creates a file at ``/var/lib/musicdb``.
This directory can be configured in the MusicDB configuration file ``/etc/musicdb.ini``.
Enter the absolute path at ``[log]->debugfile``.


==============================  ===========  ===========  =============
Directory                       Owner        Group        Permissions
==============================  ===========  ===========  =============
/var/log/musicdb                ``root``     ``musicdb``  ``rwxrwxr-x``
/var/log/musicdb/debuglog.ansi  ``musicdb``  ``musicdb``  ``rw-r-----``
==============================  ===========  ===========  =============




Transition from 7.2.0 to 8.0.0
------------------------------

.. warning::

   Create a backup of your MusicDB data directory befor installing MusicDB.
   For example via ``cp -r /opt/musicdb/data ~/musicdb-7.2.0``.

Before the transition make sure that you started the MusicDB server at least once successfully.
Then make sure that the server is *not* running during the transition.

If in doubt run:

.. code-block:: bash

   systemctl start  musicdb
   systemctl status musicdb # make sure that MusicDB started successful
   systemctl stop   muiscdb

In this instructions it is assumed that the new data path will be ``/var/lib/musicdb``
as it is the default data path since version 8.0.0.
In the examples, this path is now called ``$newdata``.

The old data path (by default it was ``/opt/musicdb/data`` will be named ``$olddata``.


Databases
^^^^^^^^^

Copy and overwrite the old databases with the new ones.
The ``lycra.db`` will no longer be used and can be deleted.
The feature that uses this database has been removed with version 8.0.0.

.. code-block:: bash

   # as root
   cp --no-preserve=mode,ownership $oldpath/muisc.db   $newpath/music.db
   cp --no-preserve=mode,ownership $oldpath/tracker.db $newpath/tracker.db


Configuration
^^^^^^^^^^^^^

The following table shows the new paths of the most important configuration files.
To update the ``muiscdb.ini`` look at :doc:`/basics/config`.
Most categories and keys are the same.

+-------------------------------------+------------------------------------+
| Old Path                            | New Path                           |
+-------------------------------------+------------------------------------+
| /opt/musicdb/data/musicdb.ini       | /etc/muiscdb.ini                   |
| /opt/musicdb/data/webui.ini         | /var/lib/muiscdb/webui.ini         |
| /opt/musicdb/server/webui/config.js | /var/lib/musicdb/webdata/config.js |
+-------------------------------------+------------------------------------+

The WebUI configuration must also be transfered.

+--------------------------------------+------------------------------------+
| Old Path                             | New Path                           |
+--------------------------------------+------------------------------------+
| /opt/musicdb/server/webui/config.js  | /var/lib/webdata/config.js         |
+--------------------------------------+------------------------------------+



Artworks
^^^^^^^^

.. code-block:: bash

   cp -r --no-preserve=mode,ownership $olddata/artwork/* $newdata/webdata/artwork/.


Music
^^^^^

By default the new music directory path is ``/var/music``.
You can copy your music into that path or change the path setting in ``/etc/musicdb.ini`` at ``[directories]->music``.


Web Server and Logrotate
^^^^^^^^^^^^^^^^^^^^^^^^

The new configurations have been installed with MusicDB.
See the installation instructions: :doc:`/usage/install`.

