Workflow for distribution
=========================

This section of the documentation describes how to MusicDB packages will be created.

The workflows starts with creating a clean source tarball.
This archive is the base of all further packages.

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

The script to create this archive is ``src-build.sh``.
It builds the archive into ``dist/musicdb-$version-src.tar.zst``.
The archive extracts into a ``musicdb-$version-src`` directory.


pacman Package
--------------

Based on the source package, a ``pacman`` package can be build with the ``pkg-build.sh`` script.

Fedora rpm Package
------------------

.. code-block:: bash

   sudo dnf install rpmdevtools
   rpmdev-setuptree

   sudo dnf install python3-devel python3-build /usr/bin/pathfix.py

   cd scripts
   ./src-build.sh
   ./rpm-build.sh
