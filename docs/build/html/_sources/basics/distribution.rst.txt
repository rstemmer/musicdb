Workflow for distribution
=========================

This section of the documentation describes how to MusicDB packages will be created.

The workflows starts with creating a clean source tarball.
This archive is the base of all further packages.

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
   ./UpdateVersionNumbers.sh

The release date needs to be updated manually.
Also all files in ``dist/debian`` need to be updated manually.


Source Tarball
--------------

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
-------------------------

This section describes how to create a package for Arch Linux.

Based on the source package, a ``pacman`` package can be build with the ``pkg-build.sh`` script.

.. code-block:: bash

   # Create Packages
   cd scripts
   ./build src pkg doc


Fedora rpm Package
------------------

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
-------------------------

This section describes how to create a package for Debian that can also be installed on Ubuntu.

.. code-block:: bash

   # Create Build Environment
   apt install build-essential debmake fakeroot pbuilder debhelper dh-exec
   apt install zstd
   apt install dh-python python3-all python3-setuptools

   # Create Packages
   cd scripts
   ./build src deb

