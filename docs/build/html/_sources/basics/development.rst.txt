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

.. code-block:: bash

   systemctl start httpd
   systemctl start musicdb


Prepare Development Environment
-------------------------------

For development you may need some additional tools.
Some basic tools are ``sed`` and ``zstd`` which may already me installed.
For building the documentation via Sphinx: ``python-sphinx``, ``python-sphinx-inline-tabs``, ``python-sphinx_rtd_theme`` and make.
To build the python modules for packaging you need ``python-setuptools`` and ``python-build``.
For building packages for you distribution you may need ``makepkg``, ``rpmbuild`` or ``debuild``.
To build the release version of the WebUI you need `svg2json <https://github.com/rstemmer/svg2json>`_.

.. code-block:: bash

   pacman -S sed zstd \
      python-sphinx python-sphinx-inline-tabs python-sphinx_rtd_theme \
      python-setuptools python-build

   pip install svg2json



Supportive Scripts
------------------

There are some scripts that support quick updates (on Arch Linux) and additional development automation.

* **build.sh**: This script builds archives and packages for distribution and installation from the source code. See :doc:`basics/distribution` for details.
* **musicdb-update.sh**: Updates the MusicDB websocket server from a fresh build packages. It also takes care about stopping and restarting the corresponding systemd service. The package needs to be build via ``build.sh src pkg`` before.
* **webui-update.sh**: Copies the WebUI source files into the served WebUI directory. So when loading the debug.html version of the WebUI in the browser, the latest version is loaded. If you also want to update the release version you can optionally call ``build.sh webui`` before.
* **documentation-update.sh**: Installs the latest version of the documentation. The documentation needs to be build via ``build.sh doc`` before.
* **UpdateVersionNumbers.sh**: Updates all version numbers in the source codes corresponding to the versions in the VERSION file.
* **CreateWebUIClassDiagram.sh**: Generates an image of the class structures of the WebUI via `Graphviz <https://graphviz.org/>`_.
* **CreateDummyAlbum.sh**: Creates a set of dummy music albums with horrible names and meta data. First parameter must be the directory in which the albums shall be stored. You need `id3edit <https://github.com/rstemmer/id3edit>`_ to run this script.



WebUI Debugging
---------------

For debugging the WebUI I recommend to load the source files into the web browser instead of the consolidated release version.
This can be achieved by loading the *debug.html* file. Not via index.html!

→ http://127.0.0.1/musicdb/debug.html

Loading the WebUI via debug.html takes a lot of time because there are hundreds if singe http request for the singe JavaScript, CSS and SVG files.
Firefox can handle this situation. With Chromium I got issues with timeouts. You may need to fine tune the browser configuration for this.
I also recommend to disable the browser cache when using the developer tools. This avoids debugging on old CSS files.

Use the ``webui-update.sh`` script to copy the latest version of WebUI into the directory served by the http server.
These source files are only loaded when accessing the WebUI via the debug.html file. Not via index.html!



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


