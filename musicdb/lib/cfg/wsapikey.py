# MusicDB,  a music manager with web-bases UI that focus on music.
# Copyright (C) 2017 - 2022  Ralf Stemmer <ralf.stemmer@gmx.net>
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
This module takes care of the WebSocket API Key

The key will be stored in the MusicDB data directory inside the config sub directory.

"""

import logging
from musicdb.lib.filesystem import Filesystem


class WebSocketAPIKey(object):
    """
    This class manages the WebSocket API Key.
    Use the method :meth:`~Read` to get the API key.

    If the key is missing, it will be generated.
    A new key gets also be set in the WebUI JavaScript configuration file ``config.js``.

    To generate a new key, delete the ``wsapikey.txt`` from the MusicDB Configuration Directory.
    
    Args:
        config: Instance of the :class:`~musicdb.lib.cfg.musicdb.MusicDBConifg` class
    """

    def __init__(self, config):
        self.keyfile    = config.files.wsapikey
        self.configjs   = config.files.webuijsconfig
        self.filesystem = Filesystem(config.directories.data)



    def Read(self):
        """
        Reads the WebSocket API Key and returns it as string.
        If it does not exist, it will be created via :meth:`~CreateIfMissing`.

        Raises an exception if the key file cannot be created.

        Returns:
            The WebSocket API Key as string.
        """
        success = self.CreateIfMissing()
        if not success:
            raise RuntimeError("Cannot create WebSocket API Key %s"%(self.keyfile))


        with open(self.keyfile) as file:
            lines = file.read()
        key = lines.splitlines()[0].strip()
        return key





    def CreateIfMissing(self):
        """
        This method creates a new WebSocket API Key if none has been created yet.

        If the WebSocke API Key file exists nothing will be done.
        If it is missing, it will be created including a new WebSocket API Key.

        It also updates a new generated WebUI ``config.js`` file.
        It is expected that the ``config.js`` file exists.

        The WebUI JavaScript configuration must already exist.
        If that file already has a key, it will not be replaced.
        If no key exists yet (a dummy key ``WSAPIKEY`` is expected in place) the key will be set.

        For creating the key, ``openssl`` is used:

        .. code-block:: bash

            openssl rand -base64 -out $path 32

        Returns:
            ``True`` on success or if the key already exists, otherwise ``False``
        """
        logging.debug("Checking if WebSocket API Key exists at %s", self.keyfile)

        if self.filesystem.Exists(self.keyfile):
            return True

        logging.info("Generating new WebSocket API Key at %s", self.keyfile)

        # Generate Key
        try:
            self.filesystem.Execute(["openssl", "rand", "-base64", "-out", self.keyfile, "32"])
        except Exception as e:
            logging.error("Creating WebSocket API Key failed with exception: %s", str(e))
            return False

        self.filesystem.SetAccessPermissions(self.keyfile, "rw-rw----")

        # Read Key
        wsapikey = self.Read()

        logging.info("Updating WebSocket API Key in %s", self.configjs)

        # Check if config.js exists
        if not self.filesystem.Exists(self.configjs):
            logging.error("Missing WebUI configuration %s. Cannot set WebSocket API Key.", self.configjs)
            return False

        # Read the config.js file
        with open(self.configjs) as file:
            oldlines = file.read()

        # Process file: Update WEBSOCKET_APIKEY line
        oldlines = oldlines.splitlines()
        newlines = []
        for line in oldlines:
            if "WEBSOCKET_APIKEY" in line:
                newlines.append("const WEBSOCKET_APIKEY = \"%s\";"%(wsapikey))
            else:
                newlines.append(line)
        newlines = "\n".join(newlines)

        # Write file
        with open(self.configjs, "w") as file:
            file.write(newlines)

        return True



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

