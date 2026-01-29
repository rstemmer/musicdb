Workflow for Distribution
=========================

This section of the documentation describes how MusicDB packages can be created.

The workflows starts with creating a clean source tarball.
This archive is the base of all further packages.

Install svg2json
----------------
The WebUI used many vector graphics in form of individual svg files.
To reduce traffic when loading the WebUI, all these individual svg files get bundled as base64 encoded strings into a JSON file.
This is done by the python application `svg2json <https://github.com/rstemmer/svg2json>`_.

You can install svg2json via ``pipx``:

.. code-block:: bash

   pipx svg2json

Create Release Candidate Branch
-------------------------------

Packages are created from a release candidate branch.

.. code-block:: bash

   git checkout -b v8.0.0-rc


Update Version Numbers
----------------------

There is a script that propagates the versions in the VERSION file through the whole project.

.. code-block:: bash

   cd scripts
   vim ../VERSION
   ./UpdateVersionNumbers.sh

The release date needs to be updated manually.
Also all files in ``dist/debian`` need to be updated manually.


Build Packages via build.sh
---------------------------

Inside the scripts directory is a script called ``build.sh``.
This script can be used to build a source tarball that then can be used to build packages for some Linux distributions.
Individual build steps can be given as parameter to the script.
These steps are executed in the order of the parameters.
The following steps exist:

* **webui**: Build the release version of the WebUI (Aggregate all JavaScript files in one .js file, all CSS files in one .css file and all vector graphics in one .json file).
* **src**: Implicit triggers the *webui* step to build a release version of the WebUI. Then all sources from the WebUI (incl. release version), the MusicDB websocket server, other shared files and some meta files like LICENSE and VERSION are collected as one tar archive. This archive contains all sources to install MusicDB from sources. The documentation is not included.
* **doc**: Build the documentation from its sources and collect the resulting html based documentation as a tar archive.
* **rpm**: Build a rpm package - expects an existing source package
* **pkg**: Build a pkg package - expects an existing source package
* **deb**: Build a deb package - expects an existing source package

All created packages are stored in the pkg sub director inside the repository root directory.
If the source archive gets not build explicitly before a distribution package gets build, an already existing source archive will be used - or an error occurs if it does not exist.



Source Tarball
^^^^^^^^^^^^^^

The source tarball is created out of some directories and files of the git repository.
It consists of the following files and directories:

* ./musicdb
* ./webui
* ./share
* ./sql
* README.md
* LICENSE
* setup.py
* pyproject.toml
* CHANGELOG

The script to create this archive is ``build.sh src``.
It builds the archive into ``pkg/musicdb-$version-src.tar.zst``.
The archive extracts into a ``musicdb-$version-src`` directory.

This source archive is then used to create other packages.

The source archive does not include the documentation.
To create a separate documentation package, run ``build.sh doc``.
It builds the archive into ``pkg/musicdb-$version-doc.tar.zst``.
The archive extracts into a ``musicdb-$version-doc`` directory.


Arch Linux pacman Package
^^^^^^^^^^^^^^^^^^^^^^^^^

This section describes how to create a package for Arch Linux.

Based on the source package, a ``pacman`` package can be build with the ``build.sh`` script.

.. code-block:: bash

   # Create Packages
   cd scripts
   ./build src pkg doc


Fedora rpm Package
^^^^^^^^^^^^^^^^^^

This section describes how to create a package for Fedora.

.. code-block:: bash

   # Create Build Environment
   sudo dnf install rpmdevtools
   rpmdev-setuptree

   sudo dnf install python3-devel python3-build /usr/bin/pathfix.py

   # Create Packages
   cd scripts
   ./build src rpm

Debian/Ubuntu deb Package
^^^^^^^^^^^^^^^^^^^^^^^^^

This section describes how to create a package for Debian that can also be installed on Ubuntu.

.. code-block:: bash

   # Create Build Environment
   apt install build-essential debmake fakeroot pbuilder debhelper dh-exec
   apt install zstd
   apt install dh-python python3-all python3-setuptools

   # Create Packages
   cd scripts
   ./build src deb

