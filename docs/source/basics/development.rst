Workflow for development
========================


Setup the Source Code
---------------------

Before starting developing on the MusicDB source code, you need to clone if from GitHub.

You may want to create a fork of the original sources before.

.. code-block:: bash

   git clone git@github.com:rstemmer/musicdb.git # Or your fork
   cd musicdb

   # Optional steps
   git config user.name "Your Name"           # Your name
   git config user.email "your.name@mail.xyz" # Your e-mail address
   git switch develop                         # Or create a new branch from


Install and Setup MusicDB
-------------------------

It makes sense to install MusicDB on your development computer to use this installation for testing.

See :doc:`/usage/install`.

You may want to change some settings in ``/etc/musicdb.ini`` like:

* ``[debug]→loglvel`` to ``DEBUG`` for a verbose log
* ``[log]→logfile`` to ``/dev/null`` to avoid spamming the system journal
* ``[websocket]→bind`` to ``127.0.0.1`` (The default value) for security reasons
* ``[debug]→disableicecast`` to ``True`` if you do not want to setup Icecast on your development machine


Prepare Development Environment
-------------------------------

* Additional tools
   * Sphinx: python-sphinx, python-sphinx-inline-tabs, python-sphinx_rtd_theme
   * sed, zstd
   * svg2json
   * python-setuptools, python-build
   * Optional: makepkg / rpmbuild / debuild
* Install MusicDB (Setup test environment)
* Supportive scripts
* WebUI debugging
   * → http://127.0.0.1/musicdb/debug.html

.. code-block:: bash

   systemctl start httpd
   systemctl start musicdb


Read Debugging Log
------------------

The MusicDB websocket server writes all logs into a debug log file.
To access the log file, you need to be in the MusicDB Unix group. You can acting as such a group member by using the ``newgrp`` command.
The data inside the log file are Unicode encoded text strings extended with ANSI escape sequences for color.
You can simply read those logs using the ``less`` command with the ``-R`` option.
To make ``less`` continue reading the file and follow the update if MusicDB writes new entries into the log, use the ``+F`` option.

With default settings you can simply follow the following commands to access the MusicDB debugging log.

.. code-block:: bash

   newgrp musicdb
   less -R +F /var/log/musicdb/debuglog.ansi


