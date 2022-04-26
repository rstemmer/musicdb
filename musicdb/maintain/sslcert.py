# MusicDB,  a music manager with web-bases UI that focus on music.
# Copyright (C) 2017 - 2021  Ralf Stemmer <ralf.stemmer@gmx.net>
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
This module maintains the SSL certificates used by the MusicDB WebSocket server.
It checks the existence of the files and creates them if they do not exists.

The creation of the SSL keys is done by executing the following command:

.. code-block:: bash

    openssl req -x509 -batch -utf8 -sha256 -newkey rsa:4096 -days 3650 -nodes -keyout $key.key -out $certificate.cert

The path of the key and certificate can be configured in the musicdb configuration file. (See :doc:`/basics/config`)

"""

import logging
import stat
from datetime           import datetime
from musicdb.lib.filesystem     import Filesystem


class CertificateTools(object):
    """
    This class provides a basic set of tools to check and generate certificates via ``openssl``

    Args:
        keypath (str): Absolute path to the SSL key
        certpath (str): Absolute path to the certificate

    """
    def __init__(self, keypath: str, certpath: str):
        self.keymode    = "r--------"
        self.certmode   = "r--r-----"
        self.user       = "musicdb"
        self.group      = "musicdb"
        self.keypath    = keypath
        self.certpath   = certpath
        self.filesystem = Filesystem()



    def CheckExistence(self):
        """
        This method checks if the key and certificate exist.
        The existence is checked by :meth:`musicdb.lib.filesystem.Filesystem.IsFile`.

        Returns:
            ``True`` if both files exist. Otherwise ``False``
        """
        if not self.filesystem.IsFile(self.keypath):
            return False
        if not self.filesystem.IsFile(self.certpath):
            return False
        return True



    def Create(self):
        """
        This method creates a new set of key and certificate for the MusicDB WebSocket server using ``openssl``.
        After creating the files, their permissions get updated by calling :meth:`~UpdatePermissions`

        Returns:
            ``True`` on success, otherwise ``False``
        """
        openssl = [
                "openssl",
                "req",
                "-x509",
                "-batch",
                "-utf8",
                "-sha256",
                "-newkey",
                "rsa:4096",
                "-days",
                "3650",
                "-nodes",
                "-keyout",
                self.keypath,
                "-out",
                self.certpath
                ]
        try:
            self.filesystem.Execute(openssl)
        except ChildProcessError as e:
            logging.exception("Executing openssl failed with error: %s (%s)", str(e), str(openssl))
            return False

        retval = self.UpdatePermissions()
        return retval



    def CheckPermissions(self):
        """
        This method checks if the file permissions for the key and certificate are correct.
        It is expected that both files are read-only and belong to the muiscdb user and group:
        
            * ``musicdb:musicdb r--------`` for the key file
            * ``musicdb:musicdb r--r-----`` for the certificate

        Returns:
            ``True`` if ownership and access permissions are as expected. Otherwise ``False`` gets returned.
        """
        success = True

        user, group = self.filesystem.GetOwner(self.keypath)
        mode        = self.filesystem.GetAccessPermissions(self.keypath)

        if user != self.user:
            logging.warning("User of %s is %s but should be %s!", self.keypath, user, self.user)
            success = False
        if group != self.group:
            logging.warning("Group of %s is %s but should be %s!", self.keypath, group, self.group)
            success = False
        if mode != self.keymode:
            logging.warning("Access mode of %s is %s but should be %s!", self.keypath, oct(mode), oct(self.keymode))
            success = False

        user, group = self.filesystem.GetOwner(self.certpath)
        mode        = self.filesystem.GetAccessPermissions(self.certpath)

        if user != self.user:
            logging.warning("User of %s is %s but should be %s!", self.certpath, user, self.user)
            success = False
        if group != self.group:
            logging.warning("Group of %s is %s but should be %s!", self.certpath, group, self.group)
            success = False
        if mode != self.certmode:
            logging.warning("Access mode of %s is %s but should be %s!", self.certpath, oct(mode), oct(self.certmode))
            success = False

        return success



    def UpdatePermissions(self):
        """
        This method updates the permissions of the key and certificate.
        Both files will become read-only and belong to the muiscdb user and group:
        ``musicdb:musicdb r--r-----``
        For updating the permissions the method :meth:`musicdb.lib.filesysten.Filesystem.SetAttrubutes` is used.

        After updating the access rights, :meth:`~CheckPermissions` gets called to validate the update.
        Its return value will be returned by this method.

        Returns:
            The return value of :meth:`~CheckPermissions` after updating the access rights.
        """
        self.filesystem.SetOwner(self.keypath,  self.user, self.group)
        self.filesystem.SetOwner(self.certpath, self.user, self.group)
        self.filesystem.SetAccessPermissions(self.keypath,  self.keymode)
        self.filesystem.SetAccessPermissions(self.certpath, self.certmode)
        return self.CheckPermissions()


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

