Installation From Source
========================

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
On other Distributions a similar step may be necessary to get all required multimedia libraries.

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

That's it for the Front-End.

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
   sudo install -Dm 644 share/apache.conf     /etc/httpd/conf/musicdb.conf
   sudo install -Dm 644 share/musicdb.service /usr/lib/systemd/system/musicdb.service

Make sure that the path to the ``musicdb`` executable in the ``musicdb.service`` file is correct:

.. code-block:: bash

   whereis musicdb
   # Should print:
   #> musicdb: /usr/bin/musicdb 
   # or:
   #> musicdb: /usr/local/bin/musicdb 

   # If it is not /usr/bin/musicdb do the following steps:
   sudo vim /usr/lib/systemd/system/musicdb.service
   # Check [Service]->ExecStart=/usr/local/bin/musicdb server
   systemctl daemon-reload



In a final step the ``musicdb`` UNIX user and group must be created as well as some further data directories.
For these final steps systemd will be used.

.. code-block:: bash

   sudo install -Dm 644 share/sysusers.conf /usr/lib/sysusers.d/musicdb.conf
   sudo install -Dm 644 share/tmpfiles.conf /usr/lib/tmpfiles.d/musicdb.conf
   sudo systemd-sysusers
   sudo systemd-tmpfiles --create

In case your distribution used SELinux, some additional steps are necessary to provide correct context to the new files and directories:

.. code-block:: bash

   semanage fcontext -a -t httpd_sys_content_t "/usr/share/webapps/musicdb(/.*)?"
   restorecon -R /usr/share/webapps/musicdb

That's it. MusicDB is now installed and can be configured.
Continue with the next sections to create a working environment.

