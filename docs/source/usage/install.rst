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


For Arch Linux, a package is provided that can be installed via ``pacman``.
Download the latest MusicDB package and execute the following commands.
To make the web interface accessible ``apache`` is used as web server.
Any other web server can be used as well.
Finally Icecast is used to provide an SSL secured audio stream.
This step is optional.

.. warning::

   In Germany, password protecting the audio stream is mandatory for legal reasons (GEMA),
   if the stream is accessible from the internet.

Download
--------

Download the latest package file from the `MusicDB Releases page on GitHub <https://github.com/rstemmer/musicdb/releases>`_.
Be aware that MusicDB requires lots of libraries because of its dependency to `FFmpeg <https://www.ffmpeg.org/>`_ and `gstreamer <https://gstreamer.freedesktop.org/>`_.
All libraries and dependencies are available in the Arch Linux repository so that they will be installed automatically by the package manager.


Installation via pacman
-----------------------

.. code-block:: bash

   # Install MusicDB
   pacman -U musicdb-$version-any.pkg.tar.zst


Initial Setup
-------------

Before you can start the MusicDB server, a music directory needs to be defined.
This can be done in the :doc:`~/basics/config` file that is placed at ``/etc/musicdb.ini``.
In this file you need to set the music directory in the section->entry: ``[directories]->music``.
The default directory is ``/var/music``.
This directory can be empty but must be accessible by the MusicDB server.
The expected ownership is ``$user:musicdb`` with the permission ``rwxrwxr-x``.
More details about the directories and files managed by MusicDB can be found in the :docs:`~/basics/data` section of the documentation.

The following example expects that you do not have a music directory yet.
If you have one, just check if the permissions are fine.
The placeholder ``$username`` must be replaced by the user you use to login into you system (your personal user account).
Of course it is also possible to create a new user that is only responsible for the music.

I also recommend to add your user to the ``musicdb`` group: ``usermod -G musicdb $username``.

.. code-block:: bash

   # as root
   mkdir /var/music
   chown -R $username:musicdb /var/music
   chmod ug=rwx,o=rx /var/music
   vim /etc/musicdb.ini  # update [directories]->music

You may also want to change some other settings.

If you want to turn of the debug log file edit ``/etc/musicdb.ini`` and change ``[log]->debugfile`` to ``/dev/null``.

For security reasons, by default MusicDB only accepts connections from *localhost*.
To make the MusicDB websocket server available from the local network, or internet if you setup your router correct, change the following setting: ``[websocket]->bind=0.0.0.0``.

The websocket server required an SSL cert/key pair. This is automatically generated on the first run of the MusicDB server if they do not exist.
The paths are also configured in ``/etc/musicdb.ini`` in the ``[websocket]`` section.
If you want to use your own certificates, for example managed by `Let's Encrypt <https://letsencrypt.org/de/>`_, you may want to change that paths as well.


Start MusicDB Server
--------------------

After setting up the music directory, and possibly other settings, the MusicDB websocket server can be started via ``systemctl start musicdb``.
If you want to autostart the server after a reboot (recommended), you have to enable it via ``systemctl enable musicdb``.

.. code-block:: bash

   # as root
   systemctl start musicdb
   systemctl enable musicdb

Now MusicDB is running. You can check the status via ``systemctl status musicdb``
and/or check the debug log file via ``less -R /var/log/musicdb/debuglog.ansi``.

When you start MusicDB server for the first time, there will appear some warnings because of missing files in the MusicDB *state* directory (csv-files).
This is fine. These files will automatically be created when you use MusicDB for streaming music.

You can also already access the websocket server with your web browser to see if all network settings around MusicDB are correct.
Use the following address: ``https://127.0.0.1:9000``. Of course with the correct IP address and port if you changed the port.
The default SSL certificate is self-signed and needs to be confirmed explicitly.
Then the *"AutobahnPython"* http page should load telling you the version number and that this is not an actual web server.


Setup Web User Interface via Apache
-----------------------------------

An optional but highly recommended dependency to MusicDB is the `Apache HTTP Sever <https://httpd.apache.org/>`_.
Of cause any other web server can be used in place.
A web server is required to serve the *MusicDB WebUI* - The web front-end for MusicDB.

This server can simply be installed via the package manager.
The default MusicDB Apache server configuration is already installed into ``/etc/httpd/conf/extra/musicdb.conf``.
This configuration just needs to be included into the Apache main configuration ``/etc/httpd/conf/httpd.conf``.

The following code shows how to install the HTTP server via ``pacman``.
In this example, the web-server would provide the WebUI via HTTP.
It is recommend to use HTTPS. Please check the web server manual on how to setup SSL encrypted web sites.

.. code-block:: bash

   # Setup web server for the front end
   pacman -S apache
   echo "Include conf/extra/musicdb.conf" >> /etc/httpd/conf/httpd.conf

   # Start service and enable autostart
   systemctl start httpd
   systemctl enable httpd

Now the web server is running. You can check the status via ``systemctl status httpd``.

You should now be able to access the MusicDB WebUI via ``http://127.0.0.1/musicdb/``.
Please consider a Apache server configuration that supports HTTPS.

TODO: Add reference to MusicDB Security Concept


Setup Audio Streaming via Icecast
---------------------------------

For providing a secured access to the audio stream provided by MusicDB, `Icecast <https://icecast.org/>`_ is recommended.
This section shows how to setup Icecast and how to connect MusicDB with Icecast.

.. note::

   If you do not want to use Icecase, deactivate the responsible interface in MusicDB.
   Open ``/etc/musicdb.ini`` and set ``[debug]->disableicecast`` to ``True``.

The following code shows how to install Icecast via ``pacman``.

.. code-block:: bash

   # Setup Icecast for secure audio streaming
   pacman -S icecast
   vim /etc/icecast.xml

The default settings in ``/etc/musicdb.ini`` match the default Icecast settings in ``/etc/icecast.xml``.
Only the source password needs to be configured.
Some more details about Icecast can be found in the chapter: :doc:`/lib/icecast`

The following listing shows the changes that are mandatory to make inside the ``icecast.xml`` file
to connect MusicDB with Icecast.
You should review the whole settings to make sure that Icecast is doing what you expect
and to secure the Icecast server.

.. code-block:: xml

   <icecast>

      <!-- … -->

      <authentication>
         <!-- … -->

         <!-- 
         The password set here must also be set as password in /etc/musicdb.ini [Icecast]->password
         -->
         <source-password>hackme</source-password>

         <!-- … -->
      </authentication>

      <!-- … -->

   </icecast>

You the can, for example with `VLC <https://www.videolan.org/vlc/index.de.html>`_, connect to the audio stream.
The stream URL is ``http://127.0.0.1:8000/stream``.




OLD
===

TODO: REMOVE

   * **Arch Linux:** gst-python, gst-plugins-good, gst-plugins-bad
   * **Fedora:** python3-gstreamer1 gstreamer1-plugins-good gstreamer1-plugins-bad-free


Additional Steps for Ubuntu
^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Important for Ubuntu users (and maybe Debian) only**

Usually I do not support Ubuntu for several technical reasons.
But I had a clean virtual machine with the latest Ubuntu installed, so I tried test the installation process.
The following *additional* steps are mandatory to get MusicDB to work on Ubuntu:

Before installation:

.. code-block:: bash

   apt install python-is-python3    # when executing python, python3 gets called and not the dead python2
   apt install icecast2             # Do not use the configuration dialog, MusicDB provides a secure config
                                    # Ignore that check.sh does not find icecast after installation.
                                    # This is because on Debian/Ubuntu the binary is called "icecast2".
                                    # Important scripts handle this situation of different naming.



First Run
---------

For starting and stopping the MusicDB WebSocket Server and its dependent processes, 
the scripts described in :doc:`/usage/scripts` are recommended.

You can access the WebUI by opening the file ``webui/moderator.html`` in your web browser.

The first time you want to connect to the WebSocket server you have to tell the browser that your SSL
certificates are "good".
Open the WebSocket URL in the browser with ``https`` instead of ``wss`` and create an exception.
So if your WebSocket address is ``wss://localhost:9000`` visit `https://localhost:9000`.


Update
------

For updating, you can do following steps.
Read the *Important News* of the README.md file for manual steps to do before updating to a new major release.
Only execute the scripts as root, that are followed by the comment "as root"!



