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
There are severel packages avalilabe.
Download the one that matches to your Linux Distribution.

Be aware that MusicDB requires lots of libraries because of its dependency to `FFmpeg <https://www.ffmpeg.org/>`_ and `gstreamer <https://gstreamer.freedesktop.org/>`_.
All libraries and dependencies are available in the Arch Linux repository so that they will be installed automatically by the package manager.

Installation
------------

Update your system before installing MusicDB.


Arch Linux via pacman
^^^^^^^^^^^^^^^^^^^^^

After downloading the latest MusicDB package, you can simply install it with the package manager ``pacman``.
Make sure you downloaded the package with the file extension ``.pkg.tar.zst``.

.. code-block:: bash

   # Become root
   su

   # Install MusicDB
   pacman -U musicdb-$version-any.pkg.tar.zst


Fedora via dnf
^^^^^^^^^^^^^^

After downloading the latest MusicDB package for Fedora, you can install it with the Fedora package manager ``dnf``.
MusicDB is optimized for the latest version of Fedora.
To make the instruction version independed, ``rpm -E %fedora`` is used to get the version of your Fedora distribution.
The output should match the fedora version encoded in the downloaded packaged.

If ``rpm -E %fedora`` returns ``35``, the downloaded file should contail ``fc35`` in its file name. For example: *musicdb-8.0.0-1.fc35.noarch.rpm*.

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
   sudo dnf install musicdb-8.0.0-1.fc$(rpm -E %fedora).noarch.rpm


From Source
^^^^^^^^^^^

To install MusicDB from source, download the source archive: ``musicdb-8.0.0-src.tar.zst``.
Make sure you download the one with the latest version number.

The following steps show how to install MusicDB on an Fedora 35.
There will be some minor differences with other Linux distributions.
Before installing MusicDB you should update your system.

The installation process can be split into the following parts:

    #. Installing libraries and tools MusicDB depends on
    #. Installing the Back-End (``musicdb``)
    #. Installing the Front-End (The WebUI)
    #. Installing data and configuration files
    #. Create the ``musicdb`` UNIX user and group

First you need to install all libraries and tools used by MusicDB.
This can be done with the package manager of your Linux Distribution.
In case of Fedora it is ``dnf``.

The following list shows the Arch Linux package names that need to be installed:

MusicDB requires Python 3.9 or later.
If ``python3 --version`` returns a version number less than 3.9.0 MusicDB will not work on your Linux Distribution.


===========================  ===========================  ===========================  ===========================
Package Name                 Arch Linux                   Fedora                       Debian/Ubuntu
===========================  ===========================  ===========================  ===========================
zstd                                                      zstd                         zstd
---------------------------  ---------------------------  ---------------------------  ---------------------------
Python 3                     python                       python3                      python3-all
Python Build                 python-build                 python3-build
                                                          python3-devel
Python Setup Tools           python-setuptools            python3-setuptools           python3-setuptools
---------------------------  ---------------------------  ---------------------------  ---------------------------
Python GObject               python-gobject               python3-gobject              python3-gi
Python Autobahn              python-autobahn              python3-autobahn             python3-autobahn
Python systemd               python-systemd               python3-systemd              python3-systemd
Python Levenshtein           python-levenshtein           python3-Levenshtein          python3-levenshtein
Python fuzzywuzzy            python-fuzzywuzzy            python3-fuzzywuzzy           python3-fuzzywuzzy
Python mutagen               python-mutagen               python3-mutagen              python3-mutagen
Python tqdm                  python-tqdm                  python3-tqdm                 python3-tqdm
Python Pillow                python-pillow                python3-pillow               python3-willow
---------------------------  ---------------------------  ---------------------------  ---------------------------
FFmpeg                       ffmpeg                       ffmpeg                       ffmpeg
SQLite3                      sqlite                       sqlite                       sqlite3
GStreamer                    gstreamer                    gstreamer1
GStreamer plugins            gst-plugins-base             gstreamer1-plugins-base      gstreamer1.0-plugins-base
                             gst-plugins-base-libs
                             gst-plugins-good             gstreamer1-plugins-good      gstreamer1.0-plugins-good
                             gst-plugins-bad              gstreamer1-plugins-bad-free  gstreamer1.0-plugins-bad
                             gst-plugins-bad-libs         
OpenSSL                                                   openssl                      openssl
libshout                     libshout                     libshout                     libshout3
---------------------------  ---------------------------  ---------------------------  ---------------------------
Icecast                      icecast                      icecast                      icecast2
logrotate                    logrotate                    logrotate                    logrotate
Apache HTTPD                 apache                       httpd                        apache2
===========================  ===========================  ===========================  ===========================


In some distributions packages have different names.
For example Debian and Ubuntu have the following changes:
``python3-pillow`` is replaced by ``python3-willow``.

On Fedora you have to make sure you can install dependencies from the rpmfusion repository.
MusicDB requires some dependencies that do not follow the strict free software policy fedora follows.
Those dependencies (in our case multimedia transcoding tools like ``ffmpeg``) must be installed from a third party repository.
On other Distributions a simular step may be necessary to get all required multimedia libraries.

.. code-block:: bash

   dnf repolist
   # Output should contain:
   #  rpmfusion-free
   #  rpmfusion-nonfree

   # If not, install the repository via the following commands:
   sudo dnf install https://mirrors.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm
   sudo dnf install https://mirrors.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm

Then the required packages for MusicDB can be installed:

.. code-block:: bash

   # Example for Fedora 35

   # Update the System
   sudo dnf upgrade

   # Install packages required by MusicDB
   sudo dnf install zstd
   sudo dnf install python3 python3-build python3-devel python3-setuptools
   sudo dnf install python3-gobject python3-autobahn python3-systemd python3-Levenshtein python3-fuzzywuzzy python3-mutagen python3-tqdm python3-pillow     
   sudo dnf install gstreamer1 gstreamer1-plugins-base gstreamer1-plugins-good gstreamer1-plugins-bad-free
   sudo dnf install ffmpeg
   sudo dnf install sqlite
   sudo dnf install openssl
   sudo dnf install libshout
   sudo dnf install logrotate
   sudo dnf install icecast
   sudo dnf install httpd

After installing the dependencies for MusicDB, the Back-End can be installed.
Again, the following shell commands show the required steps for Fedora 35.
The commands may be a little bit different on other distributions.
For example on Debian/Ubuntu the Python command is called ``python3`` instead of ``python``.

.. code-block:: bash

   # Go to the directory where the source archive is stored
   # For example your Downloads directory
   cd ~/Downloads

   # Unpack the source archive and enter the directory
   # Keep in mind that the version number may be different
   tar -xf musicdb-8.0.0-src.tar.zst
   cd musicdb-8.0.0-src

   # Build the Back-End
   python setup.py build
   sudo python setup.py install --skip-build --optimize=1

The Back-End should now be installed and can be tested by running ``musicdb --version``.
It should return the correct version and the following error message.
The group name will be different for your user.

.. code-block::

   MusicDB [8.0.0]
   MusicDB runs in UNIX group ralf but expects group musicdb.
   To change the group, run newgrp musicdb before executing MusicDB

If you see an exception then something went wrong.
You can open an Issue at the `MusicDB GitHub Page <https://github.com/rstemmer/musicdb/issues>`_ to ask for support.
Please include the full exception and mention the Linux Distribution you use.

Next step is to install the Front-End.
This is done by the following commands:

.. code-block:: bash

   sudo install -dm 755 /usr/share/webapps/musicdb
   sudo cp -r -a --no-preserve=ownership webui/* /usr/share/webapps/musicdb

Thats it for the Front-End.

Next the data and configuration files needed by MusicDB needs to be installed.
This is done by the following commands:

.. code-block:: bash

   # Shared Data
   sudo install -dm 755 /usr/share/musicdb
   sudo cp -r -a --no-preserve=ownership share/* /usr/share/musicdb
   sudo cp -r -a --no-preserve=ownership sql     /usr/share/musicdb

   # MusicDB Configuration
   sudo install -Dm 644 share/musicdb.ini /etc/musicdb.ini

   # System Configuration
   sudo install -Dm 644 share/logrotate.conf  /etc/logrotate.d/musicdb
   sudo install -Dm 644 share/apache.conf     /etc/httpd/conf/extra/musicdb.conf
   sudo install -Dm 644 share/musicdb.service /usr/lib/systemd/system/musicdb.service

In a final step the ``musicdb`` UNIX user and group must be created as well as some further data directories.
For these final steps systemd will be used.

.. code-block:: bash

   sudo install -Dm 644 share/sysusers.conf /usr/lib/sysusers.d/musicdb.conf
   sudo install -Dm 644 share/tmpfiles.conf /usr/lib/tmpfiles.d/musicdb.conf
   sudo systemd-sysusers
   sudo systemd-tmpfiles --create

That it. MusicDB is now installed and can be configured.
Continue with the next sections to create a working environment.


Initial Setup
-------------

This section describes the initial setup for MusicDB.
Those steps are required to provide MusicDB a valid environment.

For the following examples, the placeholder ``$username`` is used to represent the user
that owns or maintains the music collection.
The placeholder ``$username`` must be replaced by that user name.
I also recommend to add your user to the ``musicdb`` group: ``usermod -G musicdb $username``.

Music Directory
^^^^^^^^^^^^^^^

The music directory is the directory that contains the music files
that will be managed, presented and streamed by MusicDB.

**It is mandatory for MusicDB to work correctly.**

Before you can start the MusicDB server, a music directory needs to be defined.
This can be done in the :doc:`/basics/config` file that is placed at ``/etc/musicdb.ini``.
In this file you need to set the music directory in the section->entry: ``[directories]->music``.
The default directory is ``/var/music``.
This directory can be empty but it must be accessible by the MusicDB server.
The expected ownership is ``$username:musicdb`` with the permission ``rwxrwxr-x``.
More details about the directories and files managed by MusicDB can be found in the :doc:`/basics/data` section of the documentation.

The following example expects that you do not have a music directory yet.
If you have one, just check if the permissions are fine.
The placeholder ``$username`` must be replaced by the user you use to login into you system (your personal user account).
Of course it is also possible to create a new user that is only responsible for the music.

.. code-block:: bash

   # as root
   mkdir /var/music
   chown -R $username:musicdb /var/music
   chmod ug=rwx,o=rx /var/music

   # Update [directories]->music if you do not use /var/music
   vim /etc/musicdb.ini

Websocket Settings
^^^^^^^^^^^^^^^^^^

For security reasons, by default MusicDB only accepts connections from *localhost*.
To make the MusicDB websocket server available from the local network, or internet if you setup your router correct, change the following setting: ``[websocket]->bind=0.0.0.0`` in ``/etc/musicdb.ini``

.. code-block:: ini

   [websocket]
   bind=0.0.0.0

The websocket server required an SSL cert/key pair. This is automatically generated on the first run of the MusicDB server if they do not exist.
The paths are also configured in ``/etc/musicdb.ini`` in the ``[websocket]`` section.
If you want to use your own certificates, for example managed by `Let's Encrypt <https://letsencrypt.org/de/>`_, you may want to change that paths as well.

API-Key Setup
^^^^^^^^^^^^^

MusicDB has no user authentication integrated.
The MusicDB websocket server relies on the HTTPS server configuration to provide user authentication (For example via LDAP or client-side certificate authentication).

For details see :doc:`/basics/security`

.. note::

   There exists the following assumption:
   *Anyone can access the Websocket Port. Only authenticated users can access the WebUI (more precise: ``/var/lib/musicdb/webdata/config.js``).*

To only handle websocket traffic from authenticated users, the data must contain a secret only the WebUI knows - the API-Key.
Before the first run, you have to generate a key and provide it to the MusicDB server configuration
as well as to the MusicDB WebUI configuration.

**Generating a key is mandatory to use MusicDB.**

To generate a good key you can use ``openssl``:

.. code-block:: bash

   openssl rand -base64 32
   #> 52bRSRLIeBSOHVxN/L4SQgsxxP8IHmDDskmg8H/d0C0=
   # DO NOT COPY THIS KEY. CREATE YOUR OWN!

This key now must be entered into the server configuration.
When starting MusicDB for the first time, this key gets propargated into the generated client configuration automatically.

To write the generated random key into the MusicDB server configratuion edit ``/etc/muiscdb.ini`` and update the ``[websocket]->apikey`` value.

.. code-block:: ini

   [websocket]
   ; Example! Use your own generated key!
   apikey=52bRSRLIeBSOHVxN/L4SQgsxxP8IHmDDskmg8H/d0C0=


Debugging logs
^^^^^^^^^^^^^^

If you want to turn off the debug log file edit ``/etc/musicdb.ini`` and change ``[log]->debugfile`` to ``/dev/null``.


Start MusicDB Server
--------------------

After setting up the music directory, the WebSocket API Key and possibly other settings, the MusicDB websocket server can be started via ``systemctl start musicdb``.
If you want to autostart the server after a reboot (recommended), you have to enable it via ``systemctl enable musicdb``.

.. code-block:: bash

   # as root
   systemctl start musicdb
   systemctl enable musicdb

Now MusicDB is running. You can check the status via ``systemctl status musicdb``
and/or check the debug log file via ``less -R /var/log/musicdb/debuglog.ansi``.

When you start MusicDB server for the first time, there will appear some warnings because of missing files in the MusicDB *state* directory (csv-files).
This is fine. These files will automatically be created when you use MusicDB for streaming music.
There will also be a regular occurring error that the connection to Icecast failed.
This is also fine because Icecast has not been set up yet. Setting up Icecast is explained later in this document.

Now you can already access the websocket server with your web browser to see if all network settings around MusicDB are correct.
Use the following address: `<https://127.0.0.1:9000>`_. Of course use the correct IP address and port if you changed the port.
The default SSL certificate is self-signed and needs to be confirmed explicitly.
Then the *"AutobahnPython"* web page should load telling you the version number and that this is not an actual web server.


Setup Web User Interface via Apache
-----------------------------------

An optional but highly recommended dependency to MusicDB is the `Apache HTTP Sever <https://httpd.apache.org/>`_.
Of cause any other web server can be used in place.
A web server is required to serve the *MusicDB WebUI* - The web front-end for MusicDB.

This server can simply be installed via the package manager.
The default MusicDB Apache server configuration is already installed.
* On Arch Linux into ``/etc/httpd/conf/extra/musicdb.conf``.
* On Fedora into ``/etc/httpd/conf/musicdb.conf``.

This configuration just needs to be included into the Apache main configuration ``/etc/httpd/conf/httpd.conf``.
In this example, the web-server would provide the WebUI via HTTP.
It is recommend to use HTTPS. Please check the web server manual on how to setup SSL encrypted web sites.

Apache on Arch Linux
^^^^^^^^^^^^^^^^^^^^

The following code shows how to install the HTTP server via ``pacman`` on Arch Linux.

.. code-block:: bash

   # Install Apache
   pacman -S apache

   # Setup web server for the front end
   echo "Include conf/extra/musicdb.conf" >> /etc/httpd/conf/httpd.conf


Apache on Fedora
^^^^^^^^^^^^^^^^

The following code shows how to install the HTTP server via ``dnf`` on Fedora.

.. code-block:: bash

   # Install Apache
   dnf install httpd

   # Setup web server for the front end
   mv /etc/httpd/conf/musicdb.conf /etc/httpd/conf.d/.


Start the Web Server
^^^^^^^^^^^^^^^^^^^^

After installation and configuration, the server can be started via ``systemd``:

.. code-block:: bash

   # Start web server and enable autostart
   systemctl start httpd
   systemctl enable httpd

Now the web server is running. You can check the status via ``systemctl status httpd``.

You should now be able to access the MusicDB WebUI via ``http://127.0.0.1/musicdb/``.
When where is no music managed by MusicDB yet, the WebUI will show you a Welcome-Message telling you that there is no music in the Queue.
This is fine because you have not hand over any music to MusicDB.

Please consider a Apache server configuration that supports HTTPS.
For details see :doc:`/basics/security`.

You may also want to give access to your music directory.
Therefore edit the Apache configuration at ``/etc/httpd/conf/extra/musicdb.conf``.


Setup Audio Streaming via Icecast
---------------------------------

For providing a secured access to the audio stream provided by MusicDB, `Icecast <https://icecast.org/>`_ is recommended.
This section shows how to setup Icecast and how to connect MusicDB with Icecast.

.. note::

   If you do not want to use Icecase, deactivate the responsible interface in MusicDB.
   Open ``/etc/musicdb.ini`` and set ``[debug]->disableicecast`` to ``True``.

Icecast on Arch Linux
^^^^^^^^^^^^^^^^^^^^^^^

The following code shows how to install Icecast via ``pacman`` on Arch Linux.

.. code-block:: bash

   # Setup Icecast for secure audio streaming
   pacman -S icecast


Icecast on Fedora
^^^^^^^^^^^^^^^^^

The following code shows how to install Icecast via ``dnf`` on Fedora.

.. code-block:: bash

   # Setup Icecast for secure audio streaming
   dnf install icecast

Setup Icecast
^^^^^^^^^^^^^

The default settings in ``/etc/musicdb.ini`` match the default Icecast settings in ``/etc/icecast.xml``.
Only the source password needs to be configured.
Some more details about Icecast can be found in the chapter: :doc:`/lib/icecast`

The following listing shows the changes that are mandatory to make inside the ``/etc/icecast.xml`` file
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

Do not forget to also set the source password in ``/etc/musicdb.ini`` at ``[Icecast]->password``.


Run Icecast
^^^^^^^^^^^

After setup, you can start Icecast.
Be sure you have enabled MusicDB to connect to Icecast if you disabled it previously.

.. code-block:: bash

   systemctl start   icecast
   systemctl enable  icecast
   systemctl restart musicdb # Just to be sure it uses the correct configuration

You then can, for example with `VLC <https://www.videolan.org/vlc/index.de.html>`_, connect to the audio stream.
The stream URL is ``http://127.0.0.1:8000/stream``.


Protected Stream
^^^^^^^^^^^^^^^^

If you want to protect the audio stream, you need to configure the corresponding mount points as follows:

.. code-block:: xml

   <mount>
      <!-- … -->

      <authentication type="htpasswd">
         <option name="filename" value="/var/lib/icecast/users" />
         <option name="allow_duplicate_users" value="1" />
      </authentication>

      <!-- … -->
   </mount>

   <!-- … -->

   <paths>
      <!-- … -->

      <ssl-certificate>/etc/ssl/Icecast.pem</ssl-certificate>

      <!-- … -->
   </paths>

Then create the file ``Icecast.pem`` file, configure the ``users`` file and restart Icecast:

.. code-block:: bash

   # Create Icecast.pem …

   # Setup users
   touch /var/lib/icecast/users
   chown icecast:icecast /var/lib/icecast/users
   chmod u=rw,g=r,o-rw /var/lib/icecast/users

   # Restart Icecast
   systemctl restart icecast


Documentation Installation
--------------------------

Usually you can access the documentation on `online at rstemmer.github.io/musicdb <https://rstemmer.github.io/musicdb/build/html/index.html>`_
In case you want to have the documentation installed on your server you can do this with the following steps.

Download the ``musicdb-$version-doc.tar.zst`` file from the `GitHub Repository <https://github.com/rstemmer/musicdb/releases>`_ and install it to ``/usr/share/doc/musicdb/html``.
For example:

.. code-block:: bash

   mkdir -p /usr/share/doc/musicdb/htmldoc
   tar -xf musicdb-8.0.0-doc.tar.zst --strip-components=1 -C /usr/share/doc/musicdb/htmldoc



