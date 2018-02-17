#!/usr/bin/env python3

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

    All methods are blocking!

    Args:
        url (str): Address of the server.
        rootdir (str): Path to store the downloaded files at.
        certificate (str): Path to the certificate for authentication (A .pem file)
    """
    def __init__(self, url, rootdir, certificate):
        self.httpurl = url
        self.rootdir = rootdir
        if certificate:
            self.cert = os.path.join(".", certificate)



    def DownloadFile(self, source, destination):
        """
        This method downloads a file.
        Make sure the directory ``destination`` points to exists.
        
        Args:
            source (str): is the path of the file to download, relative to the URL of the server.
            destination (str): is the path to store the file, relative to the root-directory given to the constructor of this class.

        Returns:
            ``True`` on success. If the certificate cannot be found or an SSL error occurs ``False`` gets returned.
        """
        # Create paths
        dstpath = os.path.join(self.rootdir, destination)
        url     = self.httpurl + "/" + source

        # Check if certificate exists
        if not os.path.exists(self.cert):
            logging.error("Certificate " + cert + " does not exist!\n")
            return False

        # Open HTTPS session
        httpsession = requests.Session()
        httpsession.cert = self.cert

        # Download file
        try:
            # Verify=False to allow self-signed certificates
            response = httpsession.get(url, stream=True, verify=False)
        except requests.exceptions.SSLError as e:
            logging.error("Download failed with exception:\n%s\n"%(str(e)))
            return False

        # Store file
        with open(dstpath, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    f.flush()

        return True



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

