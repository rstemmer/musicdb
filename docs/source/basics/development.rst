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

For development you may need some additional tools.
Some basic tools are ``sed`` and ``zstd`` which may already me installed.
For building the documentation via Sphinx: ``python-sphinx``, ``python-sphinx-inline-tabs``, ``python-sphinx_rtd_theme`` and make.
To build the python modules for packaging you need ``python-setuptools`` and ``python-build``.
For building packages for you distribution you may need ``makepkg``, ``rpmbuild`` or ``debuild``.
To build the release version of the WebUI you need `svg2json <https://github.com/rstemmer/svg2json>`_.


.. code-block:: bash

   systemctl start httpd
   systemctl start musicdb


Supportive Scripts
------------------


WebUI Debugging
---------------

 → http://127.0.0.1/musicdb/debug.html


Read Debugging Log
------------------

The MusicDB websocket server writes all logs into a debug log file.
To access the log file, you need to be in the MusicDB Unix group.
The data inside the log file are Unicode encoded text strings extended with ANSI escape sequences for color.
You can simply read those logs using the ``less`` command with the ``-R`` option.
To make ``less`` continue reading the file and follow the update if MusicDB writes new entries into the log, use the ``+F`` option.

With default settings you can simply follow the following commands to access the MusicDB debugging log.

.. code-block:: bash

   less -R +F /var/log/musicdb/debuglog.ansi


