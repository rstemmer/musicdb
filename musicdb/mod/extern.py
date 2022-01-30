# MusicDB,  a music manager with web-bases UI that focus on music.
# Copyright (C) 2021  Ralf Stemmer <ralf.stemmer@gmx.net>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
This module copies music files to external storages.
During the copy process, transcoding and fixing invalid meta-tags will be done.
**More details about the post-processing can be found in** :doc:`/mdbapi/extern`.
To use this module properly, the following workflow is recommended:

    #. Mount device. The *by-id* method is recommended.
    #. Make sure to have write permission to the related directories
    #. Run ``musicdb extern``
    #. Unmount the device

To initialize a storage device, the ``-i``/``--init`` flag must be set.
**More details about the init-process can be found in** :doc:`/mdbapi/extern`.

For updating the ``-u``/``--update`` flag must be set.
It is also possible to apply both flags.
When using both flags at the same time, you are not able to apply any configuration changes before uploading the music file!

Be sure to have write permission for the related directories.

.. warning::

    If ``-i`` is set, the device gets initialized, even if it already is!

Before anything is done, the module checks for dependencies that are optional for MusicDB
but required for this particular module using the :meth:`~musicdb.mdbapi.extern.MusicDBExtern.CheckForDependencies`.
They are ``ffmpeg`` and `id3edit <https://github.com/rstemmer/id3edit>_`.


Examples:

    Initialize a new storage:

    .. code-block:: bash

        mount /dev/sdx1 /mnt

        # Initialize storage
        musicdb extern -i /mnt
        # -i/--init: initialize storage

        umount /mnt

    Updating the storage:

    .. code-block:: bash

        mount /dev/sdx1 /mnt

        # Update storage
        musicdb extern -u /mnt
        # -u/--update: update storage

        umount /mnt
        
"""

import argparse
import os
from musicdb.lib.modapi     import MDBModule
from musicdb.mdbapi.extern  import MusicDBExtern


class extern(MDBModule, MusicDBExtern):
    def __init__(self, config, database):
        MusicDBExtern.__init__(self, config, database)


    @staticmethod
    def MDBM_CreateArgumentParser(parserset, modulename):
        parser = parserset.add_parser(modulename, help="manage external storage")
        parser.set_defaults(module=modulename)
        parser.add_argument("-i", "--init",   action="store_true", help="initialize external storage")
        parser.add_argument("-u", "--update", action="store_true", help="update external storage")
        parser.add_argument("mountpoint", help="path to external storage")


    # return exit-code
    def MDBM_Main(self, args):

        retval = self.CheckForDependencies()
        if retval == False:
            return 1

        args.mountpoint = os.path.abspath(args.mountpoint)

        if not self.SetMountpoint(args.mountpoint):
            print("\033[1;31mInvalid mountpoint - It does not exist or is not a directory.")
            return 1

        if args.init:
            self.InitializeStorage()

        if not self.IsStorageInitialized():
            print("\033[1;31mMounted device is not configured as external music storage!\033[0m")
            print("\033[1;37mInitialize befor update!\033[0m")
            return 1 

        if args.update:
            self.UpdateStorage()

        return 0


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

