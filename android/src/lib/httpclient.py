# MusicDB,  a music manager with web-bases UI that focus on music.
# Copyright (C) 2017  Ralf Stemmer <ralf.stemmer@gmx.net>
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

import kivy
kivy.require('1.10.0')

try:
    import logging
except:
    from kivy.logger import Logger as logging

import os
import ssl
import requests


class HTTPClient(object):
    """
    This class handles the HTTP connection to the MusicDB server.
    The URL includes the protocol, port and path-offset to the MusicDB's directories.
    For example: ``"https://localhost/musicdb"``

    This method allows none-secured connections (set *certificate* to ``None``).
    But you really should use this only when the server is not accessible from the internet.

    All methods are blocking!

    Args:
        url (str): Address of the server.
        certificate (str): Path to the certificate for authentication (A .pem file)
    """
    def __init__(self, url, certificate=None):
        self.httpurl = url
        if certificate:
            self.cert = os.path.join(".", certificate)
        else:
            self.cert = None



    def DownloadFile(self, source, destination):
        """
        This method downloads a file.
        Make sure the directory ``destination`` points to exists.
        
        Args:
            source (str): is the path of the file to download, relative to the URL of the server.
            destination (str): is the path to store the file

        Returns:
            ``True`` on success. If the certificate cannot be found or an SSL error occurs ``False`` gets returned.
        """
        url = self.httpurl + "/" + source

        # Check if certificate exists
        if self.cert:
            if not os.path.exists(self.cert):
                logging.error("Certificate " + cert + " does not exist!\n")
                return False

        # Open HTTPS session
        httpsession = requests.Session()
        if self.cert:
            httpsession.cert = self.cert

        # Download file
        try:
            # Verify=False to allow self-signed certificates
            response = httpsession.get(url, stream=True, verify=False)
        except requests.exceptions.SSLError as e:
            logging.error("Download failed with exception:\n%s\n"%(str(e)))
            return False

        # Store file
        with open(destination, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    f.flush()

        return True



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

