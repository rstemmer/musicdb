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

   **MusicDB requires Python 3.9 or later.**
   If ``python3 --version`` returns a version number less than 3.9.0 MusicDB will not work on your Linux Distribution.


For Arch Linux and Fedora, a package is provided that can be installed via ``pacman`` on Arch Linux or ``dnf`` on Fedora.
If you do not use Arch Linux or Fedora, see the :doc:`/usage/fromsource` documentation.

To make the web interface accessible ``apache`` is used as web server.
Any other web server can be used as well.
Finally Icecast is used to provide an SSL secured audio stream.
This step is optional.

.. warning::

   In Germany, password protecting the audio stream is mandatory for legal reasons (GEMA).
   Configure Icecast to ask for a password if the stream is accessible from the internet.

   See :ref:`Password Protected Audio Stream` for information on how to configure Icecast that way.

Download
--------

Download the latest package file from the `MusicDB Releases page on GitHub <https://github.com/rstemmer/musicdb/releases>`_.
There are several packages available.
Download the one that matches to your Linux Distribution or the source package.

Be aware that MusicDB requires lots of libraries because of its dependency to `FFmpeg <https://www.ffmpeg.org/>`_ and `gstreamer <https://gstreamer.freedesktop.org/>`_.
All libraries and dependencies are available in the Arch Linux repository so that they will be installed automatically by the package manager.

Installation via Package Manager
--------------------------------

Update your system before installing MusicDB.

.. tab:: Arch Linux

   After downloading the latest MusicDB package, you can simply install it with the package manager ``pacman``.
   Make sure you downloaded the package with the file extension ``.pkg.tar.zst``.

   .. code-block:: bash

      # Become root
      su

      # Install MusicDB
      pacman -U ./musicdb-$version-any.pkg.tar.zst

.. tab:: Fedora

   After downloading the latest MusicDB package for Fedora, you can install it with the Fedora package manager ``dnf``.
   MusicDB is optimized for the latest version of Fedora.
   To make the instruction version independent, ``rpm -E %fedora`` is used to get the version of your Fedora distribution.
   The output should match the fedora version encoded in the downloaded packaged.

   If ``rpm -E %fedora`` returns ``35``, the downloaded file should contain ``fc35`` in its file name. For example: *musicdb-8.0.0-1.fc35.noarch.rpm*.

   First you have to make sure you can install dependencies from the rpmfusion repository.
   MusicDB requires some dependencies that do not follow the strict free software policy fedora follows.
   Those dependencies (in our case multimedia transcoding tools like ``ffmpeg``) must be installed from a third party repository.

   .. code-block:: bash

      dnf repolist
      # Output should contain:
      #  rpmfusion-free
      #  rpmfusion-nonfree

      # If not, install the repository via the following commands:
      sudo dnf install https://mirrors.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm
      sudo dnf install https://mirrors.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm


   .. code-block:: bash

      # Install MusicDB
      sudo dnf install ./musicdb-8.1.0-1.fc$(rpm -E %fedora).noarch.rpm

.. tab:: Ubuntu

   After downloading the latest MusicDB package for Ubuntu, you can install it with the Ubuntu package manager ``apt``.
   MusicDB is primary optimized for the latest Long Term Supported (LTS )version.
   In case software dependencies of the LTS version become too old for MuiscDB, try the latest non-LTS version.

   Before beeing able to install downloaded package, you need to make sure that the user ``_apt`` is allowed to access that file.
   For example by moving the downloaded package into the ``/tmp`` directory.
   The package manager is working under this user ID for tasks that do not require ``root`` priviledges.

   .. warning::

      The Debian/Ubuntu package manager ``apt`` starts services automatically during the installation phase.
      It does not let you to configure the services before they are started.

      The web server, Icecast and MusicDB are running right after the installation before you are able to set them up correctly.
      Keep this in mind!
      MusicDB's default configuration consideres such a use case and is limited to only access connections from localhost by default.
      Other dependencies are not!


   .. code-block:: bash

      # Install MusicDB
      sudo apt install ./musicdb_8.1.0-1_all.deb

      # Stop automatically started unconfigured services
      sudo systemctl stop apache2  # if fresh installed
      sudo systemctl stop icecast2
      sudo systemctl stop musicdb

   During the installation, the packet manager asks you to configure icecast2.
   You can shoud use this opportunity to set the passwords for Icecast otherwise Icecast gets online with default passwords!
   Anyway we will come to the Icecast configuration later in this installation instruction.



Initial Setup
-------------

.. note::

   In case you just upgraded from an old (before 8.0.0) MusicDB installation, see :doc:`/basics/data` for the transition to the new file and directory structure.

This section describes the initial setup for MusicDB.
Those steps are required to provide MusicDB a valid environment.

For the following examples, the placeholder ``$username`` is used to represent the user
that owns or maintains the music collection.
The placeholder ``$username`` must be replaced by that user name.
If you do not know your user name, enter ``id`` in the terminal.
The name behind the UID is your user names.

I recommend to add your user to the ``musicdb`` group: ``usermod -G musicdb $username``.
Then you have extended read and write access to data managed by MusicDB.
All users in the ``musicdb`` group can maintain MusicDB and use the MusicDB command line interface.

.. code-block:: bash

   sudo usermod -G musicdb $username

Creating a Music Directory
^^^^^^^^^^^^^^^^^^^^^^^^^^

The music directory is the directory that contains the music files
that will be managed, presented and streamed by MusicDB.

**Its existence is mandatory for MusicDB to work correctly.**

The default music directory will be ``/var/music``.
This directory will be set up during the installation of MusicDB.
If you want to stay with this directory for your music collection you can continue with the next section.
Otherwise continue with this section to get guided to setup a different music directory.

**When using SELinux then continue reading this section in any case. Additional steps may be necessary.**

Before you can start the MusicDB server, a music directory needs to be defined.
This can be done in the :doc:`/basics/config` file that is placed at ``/etc/musicdb.ini``.
In this file you need to set the music directory in the section->entry: ``[directories]->music``.
The default directory is ``/var/music``.
This directory can be empty but it must be accessible by the MusicDB server.
The expected ownership is ``musicdb:musicdb`` with the permission ``rwxrwxr-x``.
More details about the directories and files managed by MusicDB can be found in the :doc:`/basics/data` section of the documentation.

When your Linux Distribution uses SELinux, make sure the context of the music directory is set to ``httpd_sys_content_t`` if you want to access the music files from your web browser.
For details see :doc:`/basics/data`.

The following example expects that you do not have a music directory yet.
If you have one, just check if the permissions are fine.
The placeholder ``$username`` must be replaced by the user you use to login into you system (your personal user account).
Of course it is also possible to create a new user that is only responsible for the music.

If you want to use the default music directory under ``/var/music`` you can skip the next code block.

.. code-block:: bash

   # Create a new music directory (as root)
   mkdir -p /opt/music
   chmod ug=rwx,o=rx /opt/music
   chown -R musicdb:musicdb /opt/music

   # Update [directories]->music
   vim /etc/musicdb.ini

Make sure the music directory has the right permissions set.
This should be checked for new created one as well as for the default one.
In the following code example I reference to the default directory at ``/var/music``.
Replace this path with your own music directory if you changed it.

.. code-block:: bash

   # as root
   chown -R musicdb:musicdb /var/music

   # Optional when using SELinux
   semanage fcontext -a -t httpd_sys_content_t "/var/music(/.*)?"
   restorecon -R /var/music

Websocket Settings
^^^^^^^^^^^^^^^^^^

For security reasons, by default MusicDB only accepts connections from *localhost*.
To make the MusicDB websocket server available from the local network, or internet if you setup your router correct, change the following setting: ``[websocket]->bind=0.0.0.0`` in ``/etc/musicdb.ini``

.. code-block:: ini

   [websocket]
   bind=0.0.0.0

The websocket server required an SSL cert/key pair. This is automatically generated on the first run of the MusicDB server if they do not exist.
The paths are also configured in ``/etc/musicdb.ini`` in the ``[websocket]`` section.
If you want to use your own certificates, for example managed by `Let's Encrypt <https://letsencrypt.org/>`_, you may want to change that paths as well.


Debugging logs
^^^^^^^^^^^^^^

If you want to turn off the debug log file edit ``/etc/musicdb.ini`` and change ``[log]->debugfile`` to ``/dev/null``.


Start MusicDB Server
--------------------

After checking and maybe setting up a custom music directory, the WebSocket API Key and possibly other settings,
the MusicDB websocket server can be started via ``systemctl start musicdb``.
If you want to autostart the server after a reboot (recommended), you have to enable it via ``systemctl enable musicdb``.

.. code-block:: bash

   # as root
   systemctl start musicdb
   systemctl enable musicdb

Now MusicDB is running. You can check the status via ``systemctl status musicdb``
and/or check the debug log file via ``less -R /var/log/musicdb/debuglog.ansi``.

When you start MusicDB server for the first time, there will appear some warnings because of missing files in the MusicDB *state* directory (csv-files).
This is fine. These files will automatically be created when you use MusicDB for streaming music.
There will also be an error "There are no songs in the database yet. Audio stream disabled. (Import albums and restart the server to enable audio streaming again.)".
This is also an expected behavior because no music has been added to the MusicDB database.

Now MusicDB is in a state where music can be added and managed, but not streamed.
**As soon as you added a first music album to MusicDB, you can restart the server via ``systemctl restart musicdb`` and it will work with all its features including streaming audio.**

You can already access the websocket server with your web browser to see if all network settings around MusicDB are correct.
Use the following address: `<https://127.0.0.1:9000>`_. Of course use the correct IP address and port if you changed the port.
The default SSL certificate is self-signed and needs to be confirmed explicitly.
Then the *"AutobahnPython"* web page should load telling you the version number and that this is not an actual web server.


Setup Web User Interface via Apache
-----------------------------------

An optional but highly recommended dependency to MusicDB is the `Apache HTTP Sever <https://httpd.apache.org/>`_.
Of cause any other web server can be used in place.
A web server is required to serve the *MusicDB WebUI* - The web front-end for MusicDB.

This server can simply be installed via the package manager.

If you used the package manager to install MusicDB, the Apache HTTP Server has already been installed (or recommended) as dependency.
The default MusicDB Apache server configuration is already installed in the Apache configuration directory.

If you installed MusicDB from source, you find the configuration at ``/usr/share/musicdb/apache.conf``.

This configuration just needs to be included into the Apache main configuration.
In this example, the web-server would provide the WebUI via HTTP.
It is recommend to use HTTPS. Please check the web server manual on how to setup SSL encrypted web sites.

.. tab:: Arch Linux

   The following code shows how to install and configure the HTTP server via ``pacman`` on Arch Linux.
   The configuration file has already been installed to ``/etc/httpd/conf/extra/musicdb.conf``.
   This configuration just needs to be included into the Apache main configuration: ``/etc/httpd/conf/httpd.conf``.

   .. code-block:: bash

      # Install Apache
      pacman -S apache

      # Setup web server for the front end
      echo "Include conf/extra/musicdb.conf" >> /etc/httpd/conf/httpd.conf


.. tab:: Fedora

   The following code shows how to install and configure the HTTP server via ``dnf`` on Fedora.
   The configuration file has already been installed to ``/etc/httpd/conf/musicdb.conf``.
   This configuration just needs to be moved into the Apache configuration directory: ``/etc/httpd/conf.d``.

   .. code-block:: bash

      # Install Apache
      dnf install httpd

      # Setup web server for the front end
      cp /etc/httpd/conf/musicdb.conf /etc/httpd/conf.d/.


.. tab:: Ubuntu

   The following code shows how to install and configure the HTTP server via ``apt`` on Ubuntu.
   The configuration file has already been installed to ``/etc/apache2/conf-available``.
   This configuration just needs to be linked into the Apache configuration directory: ``/etc/apache2/conf-enabled``.

   .. code-block:: bash

      # Install Apache
      apt install apache2

      # Setup web server for the front end
      cd /etc/apache2/conf-enabled
      ln -s ../conf-available/musicdb.conf musicdb.conf


Start the Web Server
^^^^^^^^^^^^^^^^^^^^

After installation and configuration, the server can be started via ``systemd``:

.. code-block:: bash

   # Start web server and enable autostart
   systemctl start httpd
   systemctl enable httpd

Now the web server is running. You can check the status via ``systemctl status httpd``.

You should now be able to access the MusicDB WebUI via ``http://127.0.0.1/musicdb/``.
The WebUI should load.
It is likely that immediately a WebSocket connection error occurs.
Follow the link presented in the error message (not in the title) to go through the web browsers process of allowing https connections to that (your) server.

.. figure:: ../images/welcome.jpg
   :align: center

   When there is no music managed by MusicDB yet, the WebUI will show you a Welcome-Message telling you that there is no music in the Queue.
   This is fine because you have not hand over any music to MusicDB.

Please consider a Apache server configuration that supports HTTPS.
For details see :doc:`/basics/security`.

You may also want to give access to your music directory.
Therefore edit the Apache configuration at ``/etc/httpd/conf/extra/musicdb.conf``.


Setup Audio Streaming via Icecast
---------------------------------

For providing a secured access to the audio stream provided by MusicDB, `Icecast <https://icecast.org/>`_ is recommended.
This section shows how to setup Icecast and how to connect MusicDB with Icecast.
If you used the package manager to install MusicDB, Icecast has already been installed as dependency.

.. note::

   If you do not want to use Icecase, deactivate the responsible interface in MusicDB.
   Open ``/etc/musicdb.ini`` and set ``[debug]->disableicecast`` to ``True``.

.. tab:: Arch Linux

   The following code shows how to install Icecast via ``pacman`` on Arch Linux.

   .. code-block:: bash

      # Setup Icecast for secure audio streaming
      pacman -S icecast

.. tab:: Fedora

   The following code shows how to install Icecast via ``dnf`` on Fedora.

   .. code-block:: bash

      # Setup Icecast for secure audio streaming
      dnf install icecast

.. tab:: Ubuntu

   The following code shows how to install Icecast via ``apt`` on Fedora.

   .. code-block:: bash

      # Setup Icecast for secure audio streaming
      apt install icecast2

Setup Icecast
^^^^^^^^^^^^^

The default settings in ``/etc/musicdb.ini`` match the default Icecast settings in ``/etc/icecast.xml``.
Only the source password needs to be configured.
You can use ``openssl rand -base64 32`` to generate a secure password.
Some more details about Icecast can be found in the chapter: :doc:`/lib/icecast`

The following listing shows the changes that are mandatory to make inside the ``/etc/icecast.xml`` file
to connect MusicDB with Icecast.
In case you are using Debian/Ubuntu, the file is stored at ``/etc/icecast2/icecast.xml``

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

Do not forget to also set the source password in ``/etc/musicdb.ini`` at ``[Icecast]->password``.


Run Icecast
^^^^^^^^^^^

After setup, you can start Icecast.
Be sure you have enabled MusicDB to connect to Icecast if you disabled it previously.

On Debian/Ubuntu it must be ``icecast2`` instead of ``icecast``.

.. code-block:: bash

   systemctl start   icecast
   systemctl enable  icecast
   systemctl restart musicdb # Just to be sure it uses the correct configuration

You then can, for example with `VLC <https://www.videolan.org/vlc/index.de.html>`_, connect to the audio stream.
The stream URL is ``http://127.0.0.1:8000/stream``.


Final Steps
-----------

At this point everything is ready to run and to use.
Next you need to add Music to MusicDB.

* :doc:`/usage/import`
* :doc:`/usage/installdocs`
* :doc:`/basics/security`


