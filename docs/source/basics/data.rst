
MusicDB Data Files and Directories
==================================

In this section, all data and configuration files, as well as all directories used and maintained by MusicDB are described.

TODO

Music Directory
---------------

The expected ownership is ``$user:musicdb`` with the permission ``rwxrwxr-x``.
Keep in mind that also the web-server needs to have read access for the "preview"-feature.


Transition from 7.2.0 to 8.0.0
------------------------------

Before the transition make sure that you started the MusicDB server at least once successfully.
Then make sure that the server is *not* running during the transition.

If in doubt run:

.. code-block:: bash

   systemctl musicdb start
   systemctl musicdb status # make sure that MusicDB started successful
   systemctl muiscdb stop

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

