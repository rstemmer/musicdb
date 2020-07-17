Installation & Update
=====================

The following sections describe how to install MusicDB and its dependencies.

.. attention::

   * This is a one-man hobby project.
   * I cannot guarantee anything.
   * Whatever you do, first do a backup.
   * Please `Create a new issue on GitHub <https://github.com/rstemmer/musicdb/issues>`_ if there are any problems with MusicDB.

   I guess everyone reads this part of the documentation, so hopefully this is the most read text of the whole project.


.. warning::

   Before installing or updating MusicDB, **update your system**.
   MusicDB does not support outdated dependencies.

   Before updating MusicDB **backup the MusicDB Data directory**.
   Major updates change the configuration file and the database scheme.


Installation (Automatic)
------------------------

To install MusicDB, there is a script ``scripts/install.sh`` that will help you.
Execute this script from the scripts directory to install MusicDB.
The following subsections explain how to install MusicDB using this script.

Install Dependencies
^^^^^^^^^^^^^^^^^^^^

First, you need to install some dependencies using your systems package manager:

   * openssl
   * sqlite3
   * sed
   * git
   * icecast
   * gstreamer
   * dialog
   * gcc and clang

required gstreamer packages:

   * **Arch Linux:** gst-python, gst-plugins-good, gst-plugins-bad
   * **Fedora:** python3-gstreamer1 gstreamer1-plugins-good gstreamer1-plugins-bad-free

Executing the install.sh Script
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Now you can simply execute the ``install.sh`` script from the scripts directory in the source directory,
after you have cloned the `git <https://github.com/rstemmer/musicdb>`_ repository from GitHub.

.. code-block:: bash

   # cd to a place where the source repository shall be downloaded
   cd /src

   # download MusicDB
   git clone https://github.com/rstemmer/musicdb
   cd musicdb/scripts

   # start the installation
   su    # you need to be root
   ./install.sh
   # set and confirm the installation setup to start, or cancle and nothing will be done.

After starting the ``install.sh`` script, the script tries to determine some variables.
It also recognizes if this is a new installation or an update by checking for the symlink ``/etc/musicdb.ini``.
Then it opens a dialog where these variables can be confirmed or modified.

The following settings must be configured for the installation (and will be recognized when MusicDB shall only be updated):

   Source directory:
      The git repository with the source code.

   Server directory:
      In this directory will the MusicDB code be installed

   Data directory:
      The directory for MusicDB's data and configuration as wall as the data and configuration for its dependencies

   Music directory:
      The music collection following the :doc:`/usage/music` naming scheme

   HTTP group:
      The Unix group for HTTP documents necessary to access the WebUI

   SSL Certificate:
      Certificate file for the SSL encryption of the WebSocket communication

   SSL Key:
      Key file for the WebSocket SSL certificate


During the installation process, SSL certificates gets generated for the WebSocket connection.
The following files will be generated during installation: ``musicdb.key``, ``musicdb.crt``, ``musicdb.pfx`` and ``musicdb.pem``.
At least the *.key*, *.crt* and *.pem* files are needed to start the MusicDB server and Icecast.
If you want to use your own already available files, you can set in the settings mentioned above.
For details on how the files are created, search inside the ``install.sh`` file for ``CreateMusicDBSSLKeys``.

Whenever there is a problem, the installation process stops with an error message.
After solving the problem you can just restart the install script.
Make sure the settings are the same or still valid.
The script always tries to determine the state of a single installation step and recognizes if it is already done.

Install all Dependencies
^^^^^^^^^^^^^^^^^^^^^^^^

Execute the ``check.sh`` script to see what dependencies are missing.
In context of the install.sh script, the name of this script is a bit misleading.
It only checks for dependencies needed by MusicDB to run. It does not check the installation.

Install at least all mandatory (none optional) dependencies.
You can use your system package manager or pythons package manager ``pip`` (``pip3`` on Debian) to install them.

Configureing MusicDB
^^^^^^^^^^^^^^^^^^^^

To configure MusicDB edit the ``musicdb.ini`` file in the data directory (that is also linked to /etc/musicdb.ini).
Furthermore you should check ``icecast/config.xml`` (also in MusicDB's data directory) if those settings are what you want.


Installation (Manually)
-----------------------

The whole installation and updating process can be concluded into the steps in the table below.

+-----------------------+------------------------------------------+------------------------------------------+
|         Step          |               Installation               |                  Update                  |
+=======================+==========================================+==========================================+
| MusicDB User          | - Create ``musicdb`` User and Group      |                                          |
|                       | - Add music owner to ``musicdb`` group   |                                          |
+-----------------------+------------------------------------------+------------------------------------------+
| Generate SSL Key      | - Generate an SSL certificate and key    |                                          |
+-----------------------+------------------------------------------+------------------------------------------+
| Create directory tree | - Create data and server base directory  | - Update ``artwork/default.jpg``         |
|                       | - Create Artwork Cache                   |                                          |
+-----------------------+------------------------------------------+------------------------------------------+
| MusicDB Configuration | - Install ``musicdb.ini``                | - Update ``musicdb.ini``                 |
|                       | - Set default parameters                 |                                          |
|                       | - Create symlink to ``/etc/musicdb.ini`` |                                          |
+-----------------------+------------------------------------------+------------------------------------------+
| Create databases      | - Create all databases                   | - Update database schemes                |
+-----------------------+------------------------------------------+------------------------------------------+
| Icecast Configuration | - Create icecast user and group          | - Update icecast configuration           |
|                       | - Create icecast configuration           |                                          |
|                       | - Copy SSL certificates                  |                                          |
|                       | - Generate icecast passwords             |                                          |
|                       | - Update ``musicdb.ini`` with source PW  |                                          |
+-----------------------+------------------------------------------+------------------------------------------+
| System environment    | - Install logrotate configuration        | - Update logrotate configuration         |
|                       | - Install shell profile                  |                                          |
+-----------------------+------------------------------------------+------------------------------------------+
| ID3Edit Installation  | - Install ID3Edit                        | - Update ID3Edit                         |
+-----------------------+------------------------------------------+------------------------------------------+
| MusicDB Installation  | - Install MusicDB                        | - Update MusicDB                         |
+-----------------------+------------------------------------------+------------------------------------------+



The following steps give an idea of how to install MusicDB.

System Preparation
^^^^^^^^^^^^^^^^^^

   - create a user ``musicdb`` and a group ``musicdb``
   - add your user (here called ``user``) to group ``musicdb`` so you can access the files created by MusicDB as user.
     MusicDB will set music and artwork files ownerships to ``user:musicdb``, other files are ``musicdb:musicdb``.
   - Create a directory for MusicDB installation (here ``/srv/musicdb``) and for MusicDB's data (here ``/data/musicdb``).
     The ownership must be ``musicdb:musicdb``.
   - Create a music-directory (here ``/data/music``) and set the ownership to ``user:musicdb``

.. code-block:: bash

   # as root in /
   groupadd -g 2666 musicdb
   useradd -d /data/musicdb -s /usr/bin/zsh -g 2666 -u 2666 -M musicdb
   usermod -a -G http musicdb
   usermod -a -G musicdb user

   mkdir /srv/musicdb  && chown -R musicdb:musicdb /srv/musicdb
   mkdir /data/musicdb && chown -R musicdb:musicdb /data/musicdb
   mkdir /data/music   && chown -R user:musicdb    /data/music


Install dependencies
^^^^^^^^^^^^^^^^^^^^

Some: ``git``, ``gcc``, ``python``, ``pip``

.. attention::

   On Debian the ``python`` command runs the ancient Python 2.
   Whenever this documentation is talking about Python, Python 3 is meant!

Further more, everything ``check`` tells you is missing.
The following list gives you some details about the listed modules.

   * If an optional dependency is missing, read the ``check.sh`` script. The comments help you to decide if you need them.
   * The *PIL* module can be found as ``pillow``.
   * ``icecast`` won't be detected on Debian because there it is called ``icecast2`` (This has no impact).
   * ``apachectl`` my be not found if it is only available for root user. Or you simply use another HTTP server.
   * ``jsdoc`` can be installed via ``npm install -g jsdoc``.

Basic packages
^^^^^^^^^^^^^^

There are some external tools necessary.
Furthermore there are lots of python packages needed.
You can use the ``check.sh`` script to see what packages are missing.

The missing ``id3edit`` tool is part of MusicDB.
It's installation is described in this documentation later on.

Download MusicDB
^^^^^^^^^^^^^^^^

.. code-block:: bash

   # as user in ~/projects
   git clone https://github.com/rstemmer/libprinthex.git
   git clone https://github.com/rstemmer/id3edit.git
   git clone https://github.com/rstemmer/musicdb.git



libprinthex
^^^^^^^^^^^

.. code-block:: bash

   cd libprinthex
   ./build.sh
   ./install.sh


id3edit
^^^^^^^

.. code-block:: bash

   cd id3edit
   ./build.sh
   ./install.sh

musicdb
^^^^^^^

.. code-block:: bash

   cd /srv/musicdb
   cp ~/projects/musicdb/update.sh .
   # edit update.sh and make sure it does what you expect
   ./update.sh

   # config
   cd /data/musicdb
   cp ~/projects/musicdb/share/musicdb.ini .
   cp ~/projects/musicdb/share/mdbstate.ini .
   chown musicdb:musicdb musicdb.ini
   chown musicdb:musicdb mdbstate.ini
   chmod g+w musicdb.ini
   chmod g+w mdbstate.ini
   vim musicdb.ini
    
   # this config can also be the default config
   cd /etc
   ln -s /data/musicdb/musicdb.ini musicdb.ini
   cd -
    
   # artwork
   mkdir -p artwork
   chown -R user:musicdb artwork
   chmod -R g+w artwork 
    
   cp ~/projects/musicdb/share/default.jpg artwork/default.jpg
   chown musicdb:musicdb artwork/default.jpg 
    
   # logfile
   touch debuglog.ansi && chown musicdb:musicdb debuglog.ansi
    
   # logrotate
   cp ~/projects/musicdb/share/logrotate.conf /etc/logrotate.d/musicdb



Configureing MusicDB WebUI
--------------------------

The WebUI configuration must be done inside the file ``webui/config.js``

At the begin of this file, the variable ``WEBSOCKET_URL`` must be configured.
In particular the port number must match the one set in the MusicDB Configuration file /etc/musicdb.ini.
An example variable is ``WEBSOCKET_URL = "wss://localhost:9000"``.

For further details, read the :doc:`/webui/websockets` documentation
See the sections for the watchdog and the communication to the server.

This configuration will be persistent when updating.
The update process saves the lines with the configuration and restores them after the file got replaced by a new one.

The web server must provide the following virtual directories:

   * ``/musicdb/`` pointing to the WebUI directory (``$SERVERDIR/webui``)
   * ``/musicdb/artwork/`` pointing to the artwork directory (``$DATADIR/artwork``)
   * ``/musicdb/music/`` pointing to the music source directory (``*/music``)
   * ``/musicdb/docs/`` pointing to the documentation directory (``$SERVERDIR/docs``)

An example `Apache <https://httpd.apache.org/>`_ configuration can look like this:

.. code-block:: apache

   Alias /musicdb/webui/artwork/ "/opt/musicdb/data/artwork/"
   <Directory "/opt/musicdb/data/artwork">
      AllowOverride None
      Options +FollowSymLinks
      Require all granted
   </Directory>

   Alias /musicdb/music/ "/data/music/"
   <Directory "/data/music>
      AllowOverride None
      Options +FollowSymLinks
      Require all granted
   </Directory>

   Alias /musicdb/docs/ "/opt/musicdb/server/docs/"
   <Directory "/opt/musicdb/server/docs">
       AllowOverride None
       Options +FollowSymLinks
       Require all granted
   </Directory>

   Alias /musicdb/ "/opt/musicdb/server/"
   <Directory "/opt/musicdb/server">
      AllowOverride None
      Options +ExecCGI +FollowSymLinks
      Require all granted
      AddType text/cache-manifest .iOSmanifest
   </Directory>
                              

When everything is correct, and the server is running, the WebUI can be reached via ``http://localhost/musicdb/webui/moderator.html``



First Run
---------

For starting and stopping the MusicDB WebSocket Server and its dependent processes, 
the scripts described in :doc:`/usage/scripts` are recommended.

For details of the configuration, see :doc:`/basics/config`.

You can access the WebUI by opening the file ``webui/moderator.html`` in your web browser.

The first time you want to connect to the WebSocket server you have to tell the browser that your SSL
certificates are "good".
Open the WebSocket URL in the browser with ``https`` instead of ``wss`` and create an exception.
So if your WebSocket address is ``wss://localhost:9000`` visit `https://localhost:9000`.


Update
------

.. warning::
   
   The MusicDB installation script cannot be tested as good as it should be tested.
   There may be some problems in special cases.
   Espacially when you use it for updating MusicDB, it could happen that you loose some configuration or in worts case your database.

   You really should **make a backup** of the MusicDB data directory!

If you want to update MusicDB, pull the latest version from GitHub, and execute the ``install.sh`` script.
Make sure the detected settings that are displayed in the dialog are correct.
For minor release updates, the ``quickupdate.sh`` is also OK (It just updates MusicDB without checking the environment).

.. code-block:: bash

   cd /src/musicdb      # go to MusicDB's source directory
   git pull             # get the latest source code
   git checkout master  # make sure you are in the master branch
   cd scripts           # go into the scripts directory
   su                   # you must be root for the updating process
   ./update.sh --major  # update


